from django.forms import *


class IndexForm(Form): # поле ввода данных
    partCode = CharField(widget=TextInput(attrs={'class': 'field'}))
