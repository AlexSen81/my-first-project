from django.contrib import admin
from .models import Category, Product, ProductImage

# Настройка встраиваемой галереи прямо в карточку товара
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3 # Сколько пустых полей для новых фото показывать сразу (можно добавлять и больше)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name', 'slug']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description']
    # Магия: вставляем галерею внутрь карточки товара!
    inlines = [ProductImageInline]
