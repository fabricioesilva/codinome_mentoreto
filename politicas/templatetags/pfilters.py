from django import template
from django.conf import settings
import zoneinfo
from datetime import timedelta, date, datetime
register = template.Library()


@register
def situacao_pagamentos(mentor):    
    return True

@register
def matriculas_ativas(mentor):
    return "Quantidade:"

## Planos de pagamentos
# Qtd Alunos  ----    Valor   ----    Preço P/A
#     2               50,00           25,00
#     5               120,00          24,00
#     10              230,00          23,00
#     20              400,00          20,00
#     60              960,00          16,00
#     +X             960+(x 12)       ----
