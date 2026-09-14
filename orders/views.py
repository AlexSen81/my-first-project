import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from .models import OrderItem, Order
from .forms import OrderCreateForm
from catalog.cart import Cart

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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

            cart.clear()

            headers = {'Content-Type': 'application/json'}
            payload = {
                "TerminalKey": settings.TINKOFF_TERMINAL_KEY,
                "Amount": total_amount_kopecks,
                "OrderId": f"YASEN-{order.id}",
                "Description": f"Оплата заказа №{order.id} в ЯсеньStudio",
                "SuccessURL": f"http://127.0.0{order.id}/",
                "FailURL": "http://127.0.0",
                "Receipt": {
                    "Email": "info@yasenstudio.ru",
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

                # Защита: проверяем, что банк вернул именно JSON-данные
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

            # РЕЗЕРВНЫЙ СЦЕНАРИЙ: Если банк лежит, перенаправляем на нашу внутреннюю страницу с QR-кодом СБП
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
