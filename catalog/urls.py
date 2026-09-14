from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('contacts/', views.contacts, name='contacts'),
    path('catalog/', views.catalog_view, name='catalog'),
    path('product/<int:pk>/', views.product_detail_view, name='product_detail'),

    # Ссылки для корзины
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),

    # Ссылка для мгновенного обновления корзины через AJAX
    path('cart/update-ajax/<int:product_id>/', views.cart_update_ajax, name='cart_update_ajax'),
]
