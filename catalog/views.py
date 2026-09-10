from django.shortcuts import render
from django.http import HttpResponse  # Импортируем HttpResponse, чтобы вернуть простой текст

def index(request):
    return HttpResponse("<h1>Добро пожаловать в мастерскую ЯсеньStudio!</h1><p>Здесь скоро будет каталог наших изделий.</p>")
