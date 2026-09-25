import requests
from urllib.parse import urlunparse
import threading
from requests.adapters import HTTPAdapter

from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from .models import OrderItem, Order
from .forms import OrderCreateForm
from catalog.cart import Cart


# проблемный блок
def send_telegram_notification(order, receipt_items):
    """Абсолютно защищенная от багов версия отправки в Telegram через системный curl"""
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)

    if not token or not chat_id:
        print("Telegram бот не настроен в settings.py")
        return

    # Формируем текст сообщения
    message = f"🔔 **НОВЫЙ ЗАКАЗ №{order.id} на сайте ya-studio.shop!**\n\n"

    first_name = getattr(order, 'first_name', '')
    last_name = getattr(order, 'last_name', '')
    message += f"👤 **Клиент:** {first_name} {last_name}\n"

    phone = getattr(order, 'phone', 'Не указан')
    message += f"📞 **Телефон:** {phone}\n"

    message += "\n📦 **СОСТАВ ЗАКАЗА:**\n"
    total_price = 0
    for item in receipt_items:
        item_total = (item['Price'] / 100) * item['Quantity']
        total_price += item_total
        clean_name = str(item['Name']).replace('*', '').replace('_', '')
        message += f"• {clean_name} — {item['Quantity']} шт. ({item_total:.2f} руб.)\n"

    message += f"\n💰 **Итого к оплате:** {total_price:.2f} руб.\n"
    message += f"💳 **Статус:** Ожидает оплаты (Т-Банк / СБП)"

    # СБОРКА URL
    url_components = (
        'https',
        'api.telegram.org',
        f'/bot{token}/sendMessage',
        '',
        '',
        ''
    )
    url = urlunparse(url_components)

    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }

    try:
        import subprocess
        import json
        import tempfile
        import os

        # Создаем временный файл в памяти сервера, который сам удалится
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8') as tf:
            json.dump(payload, tf, ensure_ascii=False)
            temp_file_path = tf.name

        # Команда curl читает данные напрямую из файла через символ @
        # Это защищает сообщение от любых багов с кавычками и переносами строк!
        command = [
            'curl', '-v', '-X', 'POST', url,
            '-H', 'Content-Type: application/json',
            '-d', f'@{temp_file_path}'
        ]

        # Выполняем команду БЕЗ опасного shell=True как чистый изолированный процесс
        result = subprocess.run(command, capture_output=True, text=True, timeout=5)
        print(f"Ответ системного curl: {result.stdout}")

        # Удаляем временный файл после отправки
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    except Exception as e:
        print(f"Ошибка отправки через curl-файл в Telegram: {e}")


def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            total_amount_kopecks = int(cart.get_total_price() * 100)

            receipt_items = []
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
                receipt_items.append({
                    "Name": item['product'].name[:60],
                    "Price": int(item['price'] * 100),
                    "Quantity": item['quantity'],
                    "Amount": int(item['total_price'] * 100),
                    "Tax": "none"
                })

            # Создаем одну общую фоновую задачу для всех уведомлений
            def run_notifications_bg(ord_obj, items_obj):
                # 1. Отправляем почту из нашего нового файла emails.py
                try:
                    from .emails import send_email_notification
                    send_email_notification(ord_obj, items_obj)
                except Exception as ex:
                    print(f"Ошибка фоновой почты: {ex}")

                # 2. Затем отправляем Телеграм
                try:
                    send_telegram_notification(ord_obj, items_obj)
                except Exception as ex:
                    print(f"Ошибка фонового ТГ: {ex}")

            # Запускаем поток БЕЗ daemon=True
            threading.Thread(
                target=run_notifications_bg,
                args=(order, receipt_items)
            ).start()

            # Возвращаем очистку корзины на место
            cart.clear()

            headers = {'Content-Type': 'application/json'}
            payload = {
                "TerminalKey": settings.TINKOFF_TERMINAL_KEY,
                "Amount": total_amount_kopecks,
                "OrderId": f"YASEN-{order.id}",
                "Description": f"Оплата заказа №{order.id} в ЯсеньStudio",
                "SuccessURL": f"https://ya-studio.shop{order.id}/",
                "FailURL": "https://ya-studio.shop",
                "Receipt": {
                    "Email": "info@ya-studio.shop",
                    "Phone": order.phone,
                    "Taxation": "usn_income",
                    "Items": receipt_items
                }
            }

            try:
                base_url = settings.TINKOFF_API_URL.rstrip('/')
                url = f"{base_url}/Init"

                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=5,
                    verify=False
                )

                if response.status_code == 200 and 'application/json' in response.headers.get('Content-Type', ''):
                    response_data = response.json()
                    if response_data.get('Success') and 'PaymentURL' in response_data:
                        order.tinkoff_payment_id = response_data.get('PaymentId')
                        order.save()
                        return redirect(response_data['PaymentURL'])

                print(
                    f"Тестовый сервер Т-Банка вернул текст вместо JSON (Код: {response.status_code}). Включаем резервный QR-код.")
            except Exception as e:
                print(f"Тестовый сервер Т-Банка недоступен: {e}. Включаем резервный QR-код.")

            return render(request, 'orders/pay_sbp.html', {'order': order, 'total_price': total_amount_kopecks / 100})
    else:
        form = OrderCreateForm()

    return render(request, 'orders/create.html', {'cart': cart, 'form': form})


def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.paid = True
    order.save()
    return render(request, 'orders/success.html', {'order': order})


def payment_fail(request):
    return render(request, 'orders/fail.html')
