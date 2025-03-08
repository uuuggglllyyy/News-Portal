from django.contrib import admin
from django.urls import path, include  # Импортируем include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pages/', include('django.contrib.flatpages.urls')),
    path('', include('news.urls')),
    path('accounts/', include('allauth.urls')), # Добавляем allauth
    path('', include('protect.urls'))
]

# Добавьте этот блок для обслуживания статических файлов в режиме отладки
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
