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
def matricula_ativa_filter(matricula):
    no_prazo = True if matricula.encerra_em.astimezone() > datetime.now(tz=zoneinfo.ZoneInfo(settings.TIME_ZONE)) else False    
    ativa = matricula.ativa
    if ativa and no_prazo:
        return True
    elif matricula.ativa:
        matricula.ativa = False
        matricula.save()  
        return False      
    else:        
        return False


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

@register.filter
def boolean_filter(boolean):
    if boolean:
        return "Habilitada"
    else:
        return "Desabilitada"
    
@register.filter
def aplica_oferta(valor, desconto):
    entrada = float(valor.replace(',', '.'))
    deduzido = entrada * (1 - (desconto/100))
    return round(deduzido,2)

@register.filter
def get_qtd_preenchida(dicio, materia):
    if dicio and materia:
        if materia in dicio:
            qtd = dicio[materia]['qtd']
        else:
            return
    else: 
        return
    return qtd

@register.filter
def get_letras_preenchidas(dicio, materia):
    if dicio and materia:
        if materia in dicio:
            letras = dicio[materia]['letras']
        else:
            return
    else: 
        return
    return letras