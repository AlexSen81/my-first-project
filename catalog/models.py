from django.db import models


class Product(models.Model):
    # Название изделия (например, "Стол из массива ясеня")
    title = models.CharField(max_length=200, verbose_name="Название изделия")

    # Подробное описание изделия
    description = models.TextField(verbose_name="Описание")

    # Цена товара (максимум 10 знаков, 2 знака после запятой)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена (руб.)")

    # Дата добавления в каталог (чтобы новинки были вверху)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Изделие"
        verbose_name_plural = "Изделия"
        ordering = ['-created_at']  # Новые товары будут первыми в списке

    def __str__(self):
        return self.title
