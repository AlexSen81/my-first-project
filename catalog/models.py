from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL-префикс (slug)")
    # Поле для обложки баннера на главной странице
    image = models.ImageField(upload_to='category_pics/', verbose_name="Обложка категории (для главной)", blank=True, null=True)
    description = models.TextField(verbose_name="Описание для главного баннера", blank=True, null=True,
                                   help_text="Расскажите покупателю об особенностях этой категории товаров на главной странице")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

class Product(models.Model):
    # Разрешаем временно создавать товар без категории
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='products', verbose_name="Категория", blank=True, null=True)
    name = models.CharField(max_length=200, verbose_name="Название товара")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    # Разрешаем временно создавать товар без фотографии
    image = models.ImageField(upload_to='products_pics/', verbose_name="Фото товара", blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name="Активен (выводится на сайте)")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="Товар")
    image = models.ImageField(upload_to='products_pics/gallery/', verbose_name="Дополнительное фото")

    class Meta:
        verbose_name = "Фото для галереи"
        verbose_name_plural = "Галерея фотографий товара"

    def __str__(self):
        return f"Фото для {self.product.name}"
