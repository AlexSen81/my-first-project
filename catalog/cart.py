from decimal import Decimal
from django.conf import settings
from .models import Product


class Cart:
    def __init__(self, request):
        # Инициализируем корзину из сессии пользователя
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            # Если корзины нет в сессии, создаем пустую
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product, quantity=1):
        # Добавляем товар в корзину или увеличиваем его количество
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        self.cart[product_id]['quantity'] += quantity
        self.save()

    def remove(self, product):
        # Удаляем товар из корзины
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        # Сохраняем изменения в сессии
        self.session.modified = True

    def __iter__(self):
        # Получаем товары из базы данных, чтобы вывести их в шаблоне
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        # Считаем общее количество товаров в корзине
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        # Считаем общую стоимость всех товаров в корзине
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        # Очищаем корзину
        del self.session['cart']
        self.save()
