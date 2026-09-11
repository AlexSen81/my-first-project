from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from .cart import Cart
from .forms import CartAddProductForm  # Импортируем нашу форму количества


def index(request):
    return render(request, 'catalog/index.html')


def contacts(request):
    return render(request, 'catalog/contacts.html')


def catalog_view(request):
    products = Product.objects.all()
    return render(request, 'catalog/catalog.html', {'products': products})


def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    # Передаем форму на детальную страницу, чтобы там тоже можно было выбрать количество перед добавлением
    cart_product_form = CartAddProductForm()
    return render(request, 'catalog/product_detail.html', {'product': product, 'cart_product_form': cart_product_form})


# Обновленная функция добавления/обновления количества
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data
        # Передаем выбранное количество и флаг перезаписи
        cart.add(product=product, quantity=cd['quantity'], override_quantity=cd['override'])
    else:
        # Если форма не отправлялась (кликнули из каталога), просто добавляем +1
        cart.add(product=product, quantity=1, override_quantity=False)

    return redirect('cart_detail')


def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')


# Обновленная страница корзины
def cart_detail(request):
    cart = Cart(request)
    # Для каждого товара в корзине создаем свою форму с уже выбранным количеством
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={
            'quantity': item['quantity'],
            'override': True  # Указываем, что это изменение количества изнутри корзины
        })
    return render(request, 'catalog/cart_detail.html', {'cart': cart})


# Новая функция для мгновенного изменения количества через кнопки + и -
def cart_update_ajax(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    # Получаем действие: 'plus' или 'minus'
    action = request.GET.get('action')
    product_id_str = str(product.id)

    current_quantity = cart.cart.get(product_id_str, {}).get('quantity', 0)

    if action == 'plus':
        if current_quantity < 20:  # Ограничим максимум 20 шт.
            cart.add(product=product, quantity=1, override_quantity=False)
    elif action == 'minus':
        if current_quantity > 1:
            cart.add(product=product, quantity=-1, override_quantity=False)
        elif current_quantity == 1:
            cart.remove(product)  # Если уменьшили до 0, удаляем товар
            return JsonResponse({'removed': True})

    # Пересчитываем новые суммы
    item_quantity = cart.cart.get(product_id_str, {}).get('quantity', 0)
    item_total_price = float(product.price) * item_quantity

    return JsonResponse({
        'removed': False,
        'quantity': item_quantity,
        'item_total_price': f"{item_total_price:.2f} руб.",
        'cart_total_price': f"{float(cart.get_total_price()):.2f} руб."
    })