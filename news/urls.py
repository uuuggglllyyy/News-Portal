from django.urls import path, include
from . import views

urlpatterns = [
    path('news/', views.news_list, name='news_list'),
    path('news/<int:news_id>/', views.news_detail, name='news_detail'),
    path('news/search/', views.news_search, name='news_search'), #URL для поиска
    path('news/create/', views.NewsCreate.as_view(), name='news_create'),
    path('news/<int:pk>/edit/', views.NewsUpdate.as_view(), name='news_edit'),
    path('news/<int:pk>/delete/', views.NewsDelete.as_view(), name='news_delete'),
    path('articles/create/', views.ArticleCreate.as_view(), name='articles_create'),
    path('articles/<int:pk>/edit/', views.ArticleUpdate.as_view(), name='articles_edit'),
    path('articles/<int:pk>/delete/', views.ArticleDelete.as_view(), name='articles_delete'),
    path('<int:pk>/', views.PostDetail.as_view(), name='post_detail'),
    path('subscribe/<int:category_id>/', views.subscribe, name='subscribe'),
    path('test_logging/', views.test_logging_view, name='test_logging_view'), #тест логов, вызывает ошибку
]
