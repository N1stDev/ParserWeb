from .models import *
from django.contrib.staticfiles import finders

itradeIdPath = finders.find('currentItradeID.txt')
shateIdPath = finders.find('currentShateID.txt')


def loadToItradeDB(request, parts):
    ForumAuto.objects.filter(Request=request).delete()
    id = defineItradeID()
    for part in parts:
        ForumAuto(id, request, *part).save()
        id += 1
    rewriteItradeID(id)

def loadToShateDB(request, parts):
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