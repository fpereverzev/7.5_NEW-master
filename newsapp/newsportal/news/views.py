from django.shortcuts import render, redirect
from .forms import ArticleForm, PostForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Category, Subscriber
from django.contrib import messages


def create_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('news:article_list')  # Замените на правильный путь
    else:
        form = ArticleForm()
    return render(request, 'news/create_article.html', {'form': form})

def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('news:post_list')  # Замените на правильный путь
    else:
        form = PostForm()
    return render(request, 'news/create_post.html', {'form': form})

@login_required
def manage_subscription(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        selected_categories = request.POST.getlist('categories')
        Subscriber.objects.filter(user=request.user).delete()
        for category_id in selected_categories:
            category = get_object_or_404(Category, id=category_id)
            Subscriber.objects.create(user=request.user, category=category)
        messages.success(request, "Your subscriptions have been updated.")
        return redirect('news:subscriptions')

    user_subscriptions = Subscriber.objects.filter(user=request.user).values_list('category_id', flat=True)
    return render(request, 'news/subscriptions.html', {'categories': categories, 'user_subscriptions': user_subscriptions})
