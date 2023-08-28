from django import template
from django.conf import settings
import zoneinfo
from datetime import timedelta, date, datetime
register = template.Library()


@register.filter
def extract_dict(dicio, key):
    """Método de uso no template, em que a tag retorna o valor do dicionário
        correspondente à chave passada como parâmetro.

    Args:
        dicio (Dict): Dict
        key (Str): Dict key

    Returns:
        Any: Qualquer tipo que seja value em um dicionário.
    """
    return key


@register.filter
def tempo_que_falta(data):
    hoje = datetime.now(tz=zoneinfo.ZoneInfo(settings.TIME_ZONE))
    falta = data - hoje
    return falta.days


@register.filter
def matricula_ativa_filter(data):
    if data < datetime.now(tz=zoneinfo.ZoneInfo(settings.TIME_ZONE)):
        return False
    else:
        return True


@register.filter
def tempo_acabando(data):
    hoje = datetime.now(tz=zoneinfo.ZoneInfo(settings.TIME_ZONE))
    timeuntil = data - hoje
    if data > hoje:
        if timeuntil < timedelta(days=30):
            return True
        return False
    else:
        return False


@register.filter
def get_media_lista(lista):
    soma = 0
    for i in lista:
        soma += i
    if len(lista) > 0:
        media = round(soma/len(lista), 2)
    else:
        media = 0
    return media


@register.filter
def set_empty(content):
    if content == None:
        return ''
    else:
        return content

@register.filter
def alternativas(alternativas, indice):
    texto = f" \
        <table class='table-small'> \
            <thead> \
            </thead> \
            <tbody> \
                <tr> \
                    <th style='text-align:center;font-weight:600;padding: 0 0.5rem;'>Opção</th> \
                    <td> A </td> \
                    <td> B </td>  \
                    <td> C </td> \
                    <td> D </td> \
                    <td> E </td> \
                </tr> \
                <tr> \
                    <th style='text-align:center;font-weight:600;'> % </th> \
                    <td> {alternativas[str(indice)]['A']} </td> \
                    <td> {alternativas[str(indice)]['B']} </td> \
                    <td> {alternativas[str(indice)]['C']} </td> \
                    <td> {alternativas[str(indice)]['D']} </td> \
                    <td> {alternativas[str(indice)]['E']} </td> \
            </tbody> \
        </table>" 
    return texto

@register.filter
def status_resposta(dicio):
    if dicio:
        return "Respondido"
    else:
        return "Falta responder"
