import ssl
import json
import urllib.request
from django.conf import settings


def send_telegram_notification(order, receipt_items):
    """
    Абсолютно независимая версия на встроенном urllib.request.
    Полностью обходит зависания requests и баги SSL в Python 3.14.
    """
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

    # Прямой URL

    url = f"https://api.telegram.org/bot8985203102:AAHZQ09XLnk_I0GQGS0DxYeBXNjVBYMK49Y/sendMessage"

    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }

    # Превращаем данные в байты JSON
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')

    # ЖЕСТКИЙ ПРОБОЙ SSL: Создаем системный контекст, который полностью игнорирует любые проверки
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # Формируем чистый низкоуровневый HTTP-запрос
    req = urllib.request.Request(
        url,
        data=data,
        headers={'Content-Type': 'application/json'}
    )

    try:
        # Отправляем со строгим таймаутом 5 секунд, чтобы поток никогда не зависал!
        with urllib.request.urlopen(req, context=ctx, timeout=5) as response:
            html = response.read().decode('utf-8')
            print(f"[Telegram УСПЕХ] Ответ API: {html}")
    except Exception as e:
        print(f"[Telegram КРИТИЧЕСКАЯ ОШИБКА]: {e}")
