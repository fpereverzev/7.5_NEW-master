from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Post, PostCategory

@receiver(m2m_changed, sender=Post.categories.through)
def post_categories_changed(sender, instance, action, **kwargs):
    if action == 'post_add':
        # Логика, которую нужно выполнить после добавления категорий
        print(f'Categories added to post {instance.title}')
