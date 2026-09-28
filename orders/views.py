from django.shortcuts import render, get_object_or_404, redirect
import threading
from .models import OrderItem, Order
from .forms import OrderCreateForm
from catalog.cart import Cart
from .payments import init_payment  # Наш новый чистый импорт


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

            # Изолированный фоновый поток уведомлений (почта)
            def run_notifications_bg(ord_obj, items_obj):
                try:
                    from .emails import send_email_notification
                    send_email_notification(ord_obj, items_obj)
                except Exception as ex:
                    print(f"Ошибка отправки почты: {ex}")

                try:
                    from .telegram import send_telegram_notification
                    send_telegram_notification(ord_obj, items_obj)
                except Exception as ex:
                    print(f"Ошибка вызова модуля telegram.py: {ex}")

            threading.Thread(target=run_notifications_bg, args=(order, receipt_items)).start()

            # Вызываем наш новый модуль оплаты, который сам сгенерирует токен
            payment_data = init_payment(order, total_amount_kopecks, receipt_items)

            # Очищаем корзину
            cart.clear()

            if payment_data:
                # Если Т-Банк успешно создал платеж, сохраняем PaymentId и редиректим клиента
                order.tinkoff_payment_id = payment_data['PaymentId']
                order.save()
                return redirect(payment_data['PaymentURL'])

            # Резервный сценарий (СБП/QR-код), если банк недоступен или ключи не подошли
            print("Включаем резервный QR-код из-за отсутствия ответа от API Т-Банка.")
            return render(request, 'orders/pay_sbp.html', {'order': order, 'total_price': total_amount_kopecks / 100})
    else:
        form = OrderCreateForm()

    return render(request, 'orders/create.html', {'cart': cart, 'form': form})

def payment_success(request, order_id):
    """Страница успешной оплаты заказа"""
    order = get_object_or_404(Order, id=order_id)
    order.paid = True
    order.save()
    return render(request, 'orders/success.html', {'order': order})


def payment_fail(request):
    """Страница неудачной оплаты заказа"""
    return render(request, 'orders/fail.html')
