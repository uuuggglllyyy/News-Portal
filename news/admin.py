from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import News, Author, Category, Post, PostCategory, Comment

class NewsAdmin(TranslationAdmin):
    model = News

class CategoryAdmin(TranslationAdmin):
    model = Category

class PostAdmin(TranslationAdmin):
    model = Post

admin.site.register(News, NewsAdmin)
admin.site.register(Author)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(PostCategory)
admin.site.register(Comment)
