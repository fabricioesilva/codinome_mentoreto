# import time
# from celery import shared_task
from core.celery import app
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import send_mail, BadHeaderError
from .models import AplicacaoSimulado, Mentoria


@app.task
def envia_aviso_simulado():
    timedelta = timezone.timedelta(hours=24)
    dia_seguinte = timezone.now() + timedelta
    aplicacoes = AplicacaoSimulado.objects.filter(
        aplicacao_agendada__gte=timezone.now()).filter(
        aplicacao_agendada__lte=dia_seguinte)

    if aplicacoes:
        for aplicacao in aplicacoes:
            mentoria = Mentoria.objects.get(simulados_mentoria=aplicacao)
            email_template_name = "mentorias/simulados/simulado_email.txt"
            c = {
                'domain': settings.DOMAIN,
                'site_name': settings.SITE_NAME,
                'mentor': aplicacao.simulado.mentor,
                'aluno': aplicacao.aluno.nome_aluno,
                'protocol': settings.PROTOCOLO,
                'senha_do_aluno': aplicacao.senha_do_aluno,
                'aplicacao_id': aplicacao.id
            }
            mensagem_email = render_to_string(email_template_name, c)
            try:
                send_mail(
                    f"Novo simulado na mentoria {mentoria}",
                    mensagem_email,
                    settings.NOREPLY_EMAIL,
                    [aplicacao.aluno.email_aluno]
                )
            except BadHeaderError:
                print("Erro ao enviar o email.")
        else:
            print("Nenhuma aplicação nas próximas 24 horas foi encontrada.")
