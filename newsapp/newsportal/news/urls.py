from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('articles/create/', views.create_article, name='create_article'),
    path('posts/create/', views.create_post, name='create_post'),
    path('subscriptions/', views.manage_subscription, name='subscriptions'),
]
