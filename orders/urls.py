from django.urls import path
from django.views.generic import TemplateView  # Добавили стандартный импорт для текстовых страниц
from . import views

urlpatterns = [
    path('create/', views.order_create, name='order_create'),

    # Страница политики конфиденциальности для ФЗ-152
    path('privacy/', TemplateView.as_view(template_name='orders/privacy.html'), name='privacy'),

    # Новые адреса для возврата из банка:
    path('payment/success/<int:order_id>/', views.payment_success, name='payment_success'),
    path('payment/fail/', views.payment_fail, name='payment_fail'),
]
