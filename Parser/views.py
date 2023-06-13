from django.shortcuts import render
from .forms import *
from .parser import Parser
from .db import *


def index(request):  # рендер главной страницы
    form = IndexForm()
    context = {"form": form, "error": False}
    return render(request, "index.html", context)


def results(request):
    if request.method == 'POST':  # если запрос был отправлен
        form = IndexForm(request.POST)
        if form.is_valid():
            data = str(form['partCode'].value())  # что ввел пользователь
            partsItrade, partsShate = Parser(data).getAvailableParts()  # ищем детали
            if partsItrade or partsShate: # если хоть где-то детали есть
                loadToItradeDB(data, partsItrade)  # сохраняем в таблицу Forum-Auto
                loadToShateDB(data, partsShate) # сохраняем в таблицу Shate-M
                context = {"table1": ForumAuto.objects.filter(Request=data),
                           "table2": ShateM.objects.filter(Request=data), "request": data}
                return render(request, "results.html", context) # рендер страницы результата

    # если ошибка поиска или нет такой детали - рендер главной страницы с сообщением о неудаче
    return render(request, "index.html", {"form": IndexForm(), "error": True})