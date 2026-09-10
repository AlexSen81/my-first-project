from django.shortcuts import render

def index(request):
    # Теперь мы не пишем HTML в коде, а вызываем готовый шаблон из папки templates
    return render(request, 'catalog/index.html')
