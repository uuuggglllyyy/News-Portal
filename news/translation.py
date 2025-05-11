from modeltranslation.translator import register, TranslationOptions
from .models import News, Category, Post

@register(News)
class NewsTranslationOptions(TranslationOptions):
    fields = ('title', 'text')

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Post)
class PostTranslationOptions(TranslationOptions):
    fields = ('title', 'text')
