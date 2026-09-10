from django.shortcuts import render

# Эта функция ОБЯЗАТЕЛЬНО должна быть здесь:
def index(request):
    return render(request, 'catalog/index.html')

# Наша новая функция:
def contacts(request):
    return render(request, 'catalog/contacts.html')
