from django import template
from datetime import timedelta, date


register = template.Library()


@register.filter
def matricula_ativa_filter(data):    
    if data < date.today():
        return False
    else:
        return True


@register.filter
def encerra_em_filter(data):
    timeuntil = data - date.today()
    if data > date.today():
        if timeuntil < timedelta(days=30):
            return True
        return False
    else:
        return False
