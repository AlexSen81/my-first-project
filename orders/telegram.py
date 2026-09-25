import os
import json
import tempfile
import subprocess
from django.conf import settings


def send_telegram_notification(order, receipt_items):
    """Изолированный чистый модуль отправки в Telegram через системный curl"""
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
        # Убираем спецсимволы, чтобы не ломать разметку Telegram
        clean_name = str(item['Name']).replace('*', '').replace('_', '')
        message += f"• {clean_name} — {item['Quantity']} шт. ({item_total:.2f} руб.)\n"

    message += f"\n💰 **Итого к оплате:** {total_price:.2f} руб.\n"
    message += "💳 **Статус:** Ожидает оплаты (Т-Банк / СБП)"

    # ИСПРАВЛЕНО: Правильный URL для API Telegram
    url = f"https://api.telegram.org/bot8985203102:AAHZQ09XLnk_I0GQGS0DxYeBXNjVBYMK49Y/sendMessage"

    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }

    temp_file_path = None
    try:
        # Создаем временный файл в памяти для безопасной передачи текста с переносами строк
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8') as tf:
            json.dump(payload, tf, ensure_ascii=False)
            temp_file_path = tf.name

        # Системный curl гарантированно обходит баг SSL рукопожатия Python 3.14
        command = [
            'curl', '-i', '-X', 'POST', url,
            '-H', 'Content-Type: application/json',
            '-d', f'@{temp_file_path}'
        ]

        # Выполняем изолированный процесс с таймаутом 8 секунд
        result = subprocess.run(command, capture_output=True, text=True, timeout=8)
        print(f"[Telegram] Ответ системного curl: {result.stdout}")

    except subprocess.TimeoutExpired:
        print("[Telegram] Ошибка: Превышен таймаут ожидания curl.")
    except Exception as e:
        print(f"[Telegram] Ошибка внутри модуля telegram.py: {e}")
    finally:
        # Железно удаляем временный файл с сервера после отправки
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception as e:
                print(f"[Telegram] Не удалось удалить временный файл: {e}")
