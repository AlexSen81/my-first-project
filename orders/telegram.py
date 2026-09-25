import requests
from django.conf import settings


def send_telegram_notification(order, receipt_items):
    """Изолированный чистый модуль отправки в Telegram"""
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)

    if not token or not chat_id:
        print("Telegram бот не настроен в settings.py")
        return

    # Формируем текст сообщения
    message = f"🔔 **НОВЫЙ ЗАКАЗ №{order.id} на сайте ya-studio.shop!**\n\n"
    message += f"👤 **Клиент:** {order.first_name} {order.last_name}\n"
    message += f"📞 **Телефон:** {order.phone}\n\n"

    message += "📦 **СОСТАВ ЗАКАЗА:**\n"
    total_price = 0
    for item in receipt_items:
        item_total = (item['Price'] / 100) * item['Quantity']
        total_price += item_total
        # Убираем спецсимволы, чтобы не ломать разметку Telegram
        clean_name = str(item['Name']).replace('*', '').replace('_', '')
        message += f"• {clean_name} — {item['Quantity']} шт. ({item_total:.2f} руб.)\n"

    message += f"\n💰 **Итого к оплате:** {total_price:.2f} руб.\n"
    message += "💳 **Статус:** Ожидает оплаты (Т-Банк / СБП)"

    url = f"https://telegram.org{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }

    try:
        response = requests.post(url, json=payload, timeout=5)
        print(f"Ответ Telegram API из модуля telegram.py: {response.status_code}")
    except Exception as e:
        print(f"Ошибка внутри модуля telegram.py: {e}")
