from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('contacts/', views.contacts, name='contacts'),
    path('catalog/', views.catalog_view, name='catalog'),
    # Динамический путь для открытия конкретного изделия по его ID:
    path('catalog/<int:pk>/', views.product_detail_view, name='product_detail'),
]

