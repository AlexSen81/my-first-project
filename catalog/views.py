from django.shortcuts import render, get_object_or_404
from .models import Product

# 1. Главная страница
def index(request):
    return render(request, 'catalog/index.html')

# 2. Страница контактов
def contacts(request):
    return render(request, 'catalog/contacts.html')

# 3. Общая страница каталога (все товары)
def catalog_view(request):
    products = Product.objects.all()
    return render(request, 'catalog/catalog.html', {'products': products})

# 4. Детальная страница конкретного товара
def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'catalog/product_detail.html', {'product': product})
