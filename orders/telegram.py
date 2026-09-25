import requests
import urllib3
from django.conf import settings

# Жестко отключаем любые варнинги и проверки SSL на уровне сетевой библиотеки
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def send_telegram_notification(order, receipt_items):
    """Изолированный модуль отправки в Telegram с принудительным отключением SSL-проверок"""
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)

    if not token or not chat_id:
        print("[Telegram] Бот не настроен в settings.py")
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
        clean_name = str(item['Name']).replace('*', '').replace('_', '')
        message += f"• {clean_name} — {item['Quantity']} шт. ({item_total:.2f} руб.)\n"

    message += f"\n💰 **Итого к оплате:** {total_price:.2f} руб.\n"
    message += "💳 **Статус:** Ожидает оплаты (Т-Банк / СБП)"

    # Прямой URL бота

    url = f"https://api.telegram.org/bot8985203102:AAHZQ09XLnk_I0GQGS0DxYeBXNjVBYMK49Y/sendMessage"

    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }

    try:
        # verify=False принудительно заставит Python 3.14 пропустить handshake
        response = requests.post(url, json=payload, timeout=8, verify=False)
        print(f"[Telegram] Ответ API: Код {response.status_code}, Тело: {response.text}")
    except Exception as e:
        print(f"[Telegram] Ошибка отправки: {e}")
