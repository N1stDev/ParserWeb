from django.forms import *


class IndexForm(Form):
    partCode = CharField(widget=TextInput(attrs={'class': 'field'}))
