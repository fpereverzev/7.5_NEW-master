from django.db import models
from django.db.models import Sum
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import send_notification

@login_required
@permission_required('news.add_article', raise_exception=True)
def create_article(request):
    if request.method == 'POST':
        # Пример логики создания статьи
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_ids = request.POST.getlist('categories')

        # Получаем текущего автора
        author = Author.objects.get(authorUser=request.user)

        # Создаем пост
        post = Post.objects.create(
            author=author,
            title=title,
            text=content,
            categoryType='AR'
        )

        # Добавляем категории
        post.categories.set(Category.objects.filter(id__in=category_ids))

        return redirect('some_view_name')  # Замените 'some_view_name' на имя вашего представления

    return render(request, 'create_article.html')

@login_required
@permission_required('news.change_article', raise_exception=True)
def edit_article(request, article_id):
    # Ваша логика для редактирования статьи
    pass

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_date = models.DateTimeField()
    post_type = models.CharField(max_length=10, choices=[('news', 'Новость'), ('article', 'Статья')], default='article')

    def __str__(self):
        return self.title

class Author(models.Model):
    authorUser = models.OneToOneField(User, on_delete=models.CASCADE)
    ratingAuthor = models.SmallIntegerField(default=0)

    def update_rating(self):
        postRat = self.post_set.aggregate(postRating=Sum('rating'))
        pRat = postRat.get('postRating', 0) or 0

        commentRat = self.authorUser.comment_set.aggregate(commentRating=Sum('rating'))
        cRat = commentRat.get('commentRating', 0) or 0

        self.ratingAuthor = pRat * 3 + cRat
        self.save()

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    subscribers = models.ManyToManyField(User, through='Subscriber', blank=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    NEWS = 'NW'
    ARTICLE = 'AR'
    CATEGORY_CHOICES = (
        (NEWS, 'Новость'),
        (ARTICLE, 'Статья'),
    )
    categoryType = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default=ARTICLE)
    dateCreation = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through='PostCategory', related_name='posts')
    title = models.CharField(max_length=128)
    text = models.TextField()
    rating = models.SmallIntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return f'{self.text[:123]} ... {self.rating}'

    def __str__(self):
        return self.title

# Сигнал для отправки уведомлений при создании поста
@receiver(post_save, sender=Post)
def notify_subscribers(sender, instance, created, **kwargs):
    if created and instance.categoryType == Post.NEWS:
        send_notification.delay(instance.id)

class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('post', 'category')

    def __str__(self):
        return f"{self.post.title} - {self.category.name}"

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    dateCreation = models.DateTimeField(auto_now_add=True)
    rating = models.SmallIntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return f'{self.text[:123]} ... {self.rating}'

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"

class Subscriber(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'category')

    def __str__(self):
        return f"{self.user.username} - {self.category.name}"
