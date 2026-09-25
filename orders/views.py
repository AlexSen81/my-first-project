import requests
import threading

from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from .models import OrderItem, Order
from .forms import OrderCreateForm
from catalog.cart import Cart



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

            # ИСПРАВЛЕННЫЙ ВАРИАНТ: Поток живет на своих изолированных переменных!
            # ИДЕАЛЬНЫЙ ВАРИАНТ: Импорты внутри через относительный путь папки orders
            def run_notifications_bg(ord_obj, items_obj):
                # 1. Отправляем почту
                try:
                    from .emails import send_email_notification
                    send_email_notification(ord_obj, items_obj)
                except Exception as ex:
                    print(f"Ошибка отправки почты: {ex}")

                # 2. Отправляем Telegram
                try:
                    from .telegram import send_telegram_notification
                    send_telegram_notification(ord_obj, items_obj)
                except Exception as ex:
                    print(f"Ошибка вызова модуля telegram.py: {ex}")

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
                "OrderId": f"YEN-{order.id}",
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

                print(f"Тестовый сервер Т-Банка вернул текст вместо JSON (Код: {response.status_code}). Включаем резервный QR-код.")
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
