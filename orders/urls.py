from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    # Новые адреса для возврата из банка:
    path('payment/success/<int:order_id>/', views.payment_success, name='payment_success'),
    path('payment/fail/', views.payment_fail, name='payment_fail'),
]
