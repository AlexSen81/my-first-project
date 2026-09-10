from django.shortcuts import render
from .models import Product

def index(request):
    return render(request, 'catalog/index.html')

def contacts(request):
    return render(request, 'catalog/contacts.html')

# Проверь эту функцию:
def catalog_view(request):
    products = Product.objects.all()
    return render(request, 'catalog/catalog.html', {'products': products})
