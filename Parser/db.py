from .models import *
from django.contrib.staticfiles import finders

itradeIdPath = finders.find('currentItradeID.txt')
shateIdPath = finders.find('currentShateID.txt')


def loadToItradeDB(request, parts):  # Загрузка результатов поиска в таблицу
    ForumAuto.objects.filter(Request=request).delete()  # ищем записи по запросу пользователя и удаляем их
    # (чтобы потом заменить новыми данными)
    id = defineItradeID()  # чтобы избежать повторения id полей, значение всегда растет и хранится в файле
    for part in parts:
        for i in range(len(part)):
            part[i] = part[i][:200]  # ограничение по длине в 200 символов
        ForumAuto(id, request, *part).save()  # сохраняем данные в таблицу
        id += 1
    rewriteItradeID(id)  # обновляем счетчик id

def loadToShateDB(request, parts):  # все аналогично верхнему классу
    ShateM.objects.filter(Request=request).delete()
    id = defineShateID()
    for part in parts:
        ShateM(id, request, *part).save()
        id += 1
    rewriteShateID(id)


def defineItradeID():
    with open(itradeIdPath, "r") as file:
        return int(file.read())


def rewriteItradeID(id):
    with open(itradeIdPath, "w") as file:
        file.write(str(id))


def defineShateID():
    with open(shateIdPath, "r") as file:
        return int(file.read())


def rewriteShateID(id):
    with open(shateIdPath, "w") as file:
        file.write(str(id))