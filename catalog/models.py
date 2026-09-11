from django.db import models

from django.db import models


class Product(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название изделия")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена (руб.)")

    # Новое поле для загрузки фото. Картинки будут сохраняться в папку products_pics/
    image = models.ImageField(upload_to='products_pics/', verbose_name="Фотография", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Изделие"
        verbose_name_plural = "Изделия"
        ordering = ['-created_at']

    def __str__(self):
        return self.title
