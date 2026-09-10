from django.contrib import admin
from django.urls import path, include  # Импортируем include для подключения ссылок приложения

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('catalog.urls')),  # Подключаем все будущие ссылки из приложения catalog
]
