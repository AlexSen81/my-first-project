from django.core.mail import send_mail
from django.conf import settings


def send_email_notification(order, receipt_items):
    """Чистая функция отправки Email-уведомлений"""
    subject = f"Новый заказ №{order.id} на сайте ya-studio.shop"

    # Формируем читаемый текст письма
    message = f"🔔 Новый заказ №{order.id}\n\n"
    message += f"👤 Клиент: {order.first_name} {order.last_name}\n"
    message += f"📞 Телефон: {order.phone}\n\n"
    message += "📦 СОСТАВ ЗАКАЗА:\n"

    for item in receipt_items:
        message += f"• {item['Name']} — {item['Quantity']} шт.\n"

    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'info@ya-studio.shop')

    # Отправляем на твою почту Beget/Mail.ru
    send_mail(
        subject,
        message,
        from_email,
        [from_email],  # Шлём сами себе на info@ya-studio.shop
        fail_silently=False,
    )
    print("Email уведомление успешно отправлено!")
