from django.shortcuts import render
from .forms import *
from .parser import Parser
from .db import *


def index(request):
    form = IndexForm()
    context = {"form": form, "error": False}
    return render(request, "index.html", context)


def results(request):
    if request.method == 'POST':
        form = IndexForm(request.POST)
        if form.is_valid():
            data = str(form['partCode'].value())
            partsItrade, partsShate = Parser(data).getAvailableParts()
            if partsItrade or partsShate:
                loadToItradeDB(data, partsItrade)
                loadToShateDB(data, partsShate)
                context = {"table1": ForumAuto.objects.filter(Request=data),
                           "table2": ShateM.objects.filter(Request=data), "request": data}
                return render(request, "results.html", context)

    return render(request, "index.html", {"form": IndexForm(), "error": True})