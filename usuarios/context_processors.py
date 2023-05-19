from django.utils import translation
from django.shortcuts import redirect
from politicas.models import PolicyAcepted, DevPolicyAcepted
from .models import UserMessages
from utils import resources
from django.conf import settings


def custom_get_language(request):
    """Obtém a linguagem utilizada no navegador do usuário. E a partir dessa
    informação, atribui a lingua utilizada no sistema de tradução do Django.    

    Args:
        request (_type_): _description_

    Returns:
        Dict: Uso no template: {{ lang }}.
    """
    lang = translation.get_language()
    if lang in resources.TRANSLATIONS_LANGUAGES:
        translation.activate(lang)
    else:
        translation.activate('en')
    return {'lang': lang}


def custom_site_info(request):
    """Recebe informações gerais do site e aplica dinamicamente no código, onde necessário.

    Args:
        request (get): request

    Returns:
        Dict: Geralmente constantes atribuídas no arquivo core.settings.py
    """
    dicio = {
        'site_name': settings.SITE_NAME,
        'site_contact_fone': settings.SITE_CONTACT_FONE,
        'site_contact_email': settings.SITE_CONTACT_EMAIL
    }
    return dicio


def get_user_new_msgs(request):
    if request.user.is_authenticated:
        new_msgs = UserMessages.objects.filter(
            to_user=request.user,
            openned=False
        ).count()
        return {'new_msgs': new_msgs}
    else:
        return {'new_msgs': 0}


def check_accepted_policy(request):
    if request.user.is_anonymous:
        return {'need_politica': False}
    if request.user.is_authenticated:
        user_policy = PolicyAcepted.objects.filter(user=request.user)
        dev_policy = DevPolicyAcepted.objects.filter(user=request.user)
        got_policy = user_policy or dev_policy
        if not got_policy:
            return {'need_politica': True}
    else:
        return {'need_politica': False}


# def check_user_has_email_checked(request):
#     if not request.user.email_checked:
#         return redirect('usuarios:index')
