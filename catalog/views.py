# Измени самую первую строчку импорта, добавив туда redirect:
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from .cart import Cart # Импортируем наш новый класс корзины

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
# 1. Функция добавления товара в корзину
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product=product)
    return redirect('cart_detail') # После добавления сразу перекидываем в корзину

# 2. Функция удаления товара из корзины
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')

# 3. Страница отображения самой корзины
def cart_detail(request):
    cart = Cart(request)
    return render(request, 'catalog/cart_detail.html', {'cart': cart})