from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Какие поля отображать в списке товаров в админке
    list_display = ('title', 'price', 'created_at')
    # По какому полю можно кликнуть, чтобы перейти к редактированию
    list_display_links = ('title',)
    # Поля, по которым можно искать товары
    search_fields = ('title', 'description')
