from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category
from .cart import Cart
from .forms import CartAddProductForm  # Твоя форма количества


# ОБНОВЛЕННАЯ ФУНКЦИЯ ГЛАВНОЙ СТРАНИЦЫ
def index(request):
    # Достаем все категории, чтобы вывести их в виде баннеров
    categories = Category.objects.all()
    return render(request, 'catalog/index.html', {'categories': categories})


def contacts(request):
    return render(request, 'catalog/contacts.html')


# ИСПРАВЛЕННЫЙ КАТАЛОГ С УМНОЙ ФИЛЬТРАЦИЕЙ ПО КАТЕГОРИЯМ
def catalog_view(request):
    category_slug = request.GET.get('category')

    if category_slug:
        # Если кликнули по категории (например, decor), фильтруем товары
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category, is_active=True)
    else:
        # Иначе показываем все товары мастерской
        products = Product.objects.filter(is_active=True)
        category = None

    context = {
        'products': products,
        'selected_category': category,
        'categories': Category.objects.all()
    }
    return render(request, 'catalog/catalog.html', context)


# ИСПРАВЛЕННАЯ СТРАНИЦА ТОВАРА С ПОДДЕРЖКОЙ ФОРМЫ КОЛИЧЕСТВА И ГАЛЕРЕИ
def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    # Передаем форму на детальную страницу, чтобы можно было выбрать количество
    cart_product_form = CartAddProductForm()

    context = {
        'product': product,
        'cart_product_form': cart_product_form
    }
    return render(request, 'catalog/product_detail.html', context)


# ДОБАВЛЕНИЕ/ОБНОВЛЕНИЕ ТОВАРА ИЗ ЛЮБОГО МЕСТА
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product, quantity=cd['quantity'], override_quantity=cd['override'])
    else:
        # Если кликнули «В корзину» прямо из плитки каталога (без отправки формы), добавляем +1
        cart.add(product=product, quantity=1, override_quantity=False)

    return redirect('cart_detail')


# ПОЛНОЕ УДАЛЕНИЕ ИЗ КОРЗИНЫ
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')


# СТРАНИЦА ОТОБРАЖЕНИЯ КОРЗИНЫ С ИНИЦИАЛИЗАЦИЕЙ ФОРМ ДЛЯ КАЖДОГО ТОВАРА
def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={
            'quantity': item['quantity'],
            'override': True  # Изменение количества изнутри корзины
        })
    return render(request, 'catalog/cart.html', {'cart': cart})


# РОДНАЯ СТРОГАЯ ЛОГИКА ОБНОВЛЕНИЯ ЧЕРЕЗ AJAX ПО КЛИКУ НА ПЛЮС И МИНУС
def cart_update_ajax(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    # Получаем действие: 'plus' или 'minus'
    action = request.GET.get('action')
    product_id_str = str(product.id)

    current_quantity = cart.cart.get(product_id_str, {}).get('quantity', 0)

    if action == 'plus':
        if current_quantity < 20:  # Ограничение 20 шт. на набор
            cart.add(product=product, quantity=1, override_quantity=False)
    elif action == 'minus':
        if current_quantity > 1:
            cart.add(product=product, quantity=-1, override_quantity=False)
        elif current_quantity == 1:
            cart.remove(product)  # Если уменьшили до 0, полностью удаляем товар
            return JsonResponse({
                'removed': True,
                'cart_total_price': f"{float(cart.get_total_price()):.2f} руб."
            })

    # Пересчитываем новые суммы
    item_quantity = cart.cart.get(product_id_str, {}).get('quantity', 0)
    item_total_price = float(product.price) * item_quantity

    return JsonResponse({
        'removed': False,
        'quantity': item_quantity,
        'item_total_price': f"{item_total_price:.2f} руб.",
        'cart_total_price': f"{float(cart.get_total_price()):.2f} руб."
    })


def delivery_view(request):
    return render(request, 'catalog/delivery.html')
