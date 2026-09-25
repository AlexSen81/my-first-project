from django.db import models
from catalog.models import Product


class Order(models.Model):
    # Данные клиента
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    last_name = models.CharField(max_length=50, verbose_name="Фамилия", blank=True)
    phone = models.CharField(max_length=20, verbose_name="Телефон")

    # Системные поля для Т-Банка
    created = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated = models.DateTimeField(auto_now=True, verbose_name="Обновлен")
    paid = models.BooleanField(default=False, verbose_name="Оплачен")

    # ID транзакции в системе Т-Банка (нужен для проверки статуса платежа)
    tinkoff_payment_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="ID платежа Т-Банка")

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'Заказ № {self.id}'

    def get_total_cost(self):
        # Считаем общую стоимость всего заказа
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    # Эта модель связывает конкретный заказ с товарами из каталога
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    def __str__(self):
        return f'Товар {self.product.name} для заказа № {self.order.id}'

    def get_cost(self):
        return self.price * self.quantity
