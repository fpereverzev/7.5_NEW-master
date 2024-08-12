from django import forms
from .models import Article, Post

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'published_date', 'post_type']

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['author', 'categoryType', 'title', 'text']
