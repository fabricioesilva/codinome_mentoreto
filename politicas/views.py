from django.shortcuts import render
from django.core.mail import send_mail, BadHeaderError
from django.shortcuts import render, redirect
from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.contrib import messages
from django.utils.translation import gettext as _

from .models import PolicyRules, AboutUs
from utils.resources import POLICY_LANGUAGES


# Create your views here.
def show_policy(request):
    if request.method == 'GET':
        if request.LANGUAGE_CODE in POLICY_LANGUAGES:
            context = {'policy': PolicyRules.objects.get(
                language=request.LANGUAGE_CODE, active=True)}
        else:
            context = {'policy': PolicyRules.objects.get(
                language='en', active=True)}
        return render(request, 'politicas/policy_show.html', context)
    else:
        return redirect('usuarios:index')


def about_us(request):
    if request.method == 'GET':
        if request.LANGUAGE_CODE in POLICY_LANGUAGES:
            context = {'about': AboutUs.objects.get(
                language=request.LANGUAGE_CODE, active=True)}
        else:
            context = {'about': AboutUs.objects.get(
                language='en', active=True)}
        return render(request, 'politicas/about_us.html', context)
    else:
        return redirect('usuarios:index')

def fazer_contato(request):    
    if request.method == 'POST':
        subject = "Contato recebido por email"
        email_template_name = "politicas/contato_recebido.txt"
        contact_us_email = settings.CONTACTUS_EMAIL
        email_enviar = 'fabreuesilva@gmail.com' if request.POST.get('tipoContato') == 'comercial' else 'servico@expertzone.com.br'
        c = {
            'nome': request.POST.get('nome'),
            "email": request.POST.get('email'),
            'telefone': request.POST.get('telefone'),
            'conteudo': request.POST.get('conteudo'), 
            'usuario': request.user.id,
            'site_name': settings.SITE_NAME       
        }
        mensagem_email = render_to_string(email_template_name, c)
        try:
            send_mail(subject, mensagem_email, settings.NOREPLY_EMAIL,
            [contact_us_email, email_enviar], fail_silently=False)
            messages.success(request, _('Mensagem enviada com sucesso!'))
        except BadHeaderError:
            return HttpResponse('Envio de contato falhou.')
        return redirect("contato")
    
    return render(request, 'politicas/fazer_contato.html', {})

def error_404_page_view(request, exception):
    return render(request, 'politicas/404.html', {})


def error_500_page_view(request, exception=None):
    return render(request, 'politicas/500.html', {})


def error_400_page_view(request, exception):
    return render(request, 'politicas/400.html', {})


def error_403_page_view(request, exception):
    return render(request, 'politicas/403.html', {})


