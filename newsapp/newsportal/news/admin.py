from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from news.models import Article, Post


# Убедитесь, что эта функция вызывается только один раз, например, через сигнал или специальную команду
def create_authors_group():
    authors_group, created = Group.objects.get_or_create(name='authors')

    if created:
        # Получаем типы контента для моделей Article и Post
        article_ct = ContentType.objects.get_for_model(Article)
        post_ct = ContentType.objects.get_for_model(Post)

        # Получаем нужные разрешения
        permissions = Permission.objects.filter(
            content_type__in=[article_ct, post_ct],
            codename__in=['add_article', 'change_article', 'add_post', 'change_post']
        )

        # Назначаем разрешения группе
        for permission in permissions:
            authors_group.permissions.add(permission)

        print('Группа "authors" создана и права назначены.')
    else:
        print('Группа "authors" уже существует.')


# Вызываем функцию создания группы
create_authors_group()
