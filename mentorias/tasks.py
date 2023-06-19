# import time
# from celery import shared_task
from core.celery import app
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import send_mail

from .models import AplicacaoSimulado, Mentorias


@app.task
def add(x, y):
    z = x + y
    print(f"Deu tantas horas e a tarefa foi executada. Soma é: {z}")
    return


@app.task
def envia_aviso_simulado():
    timedelta = timezone.timedelta(hours=24)
    print(f'Timezone improesso : {timezone.now()}')
    amanha = timezone.now() + timedelta
    print(f"$#$@@@@@@@@@@@ {amanha}")
    aplicacoes = AplicacaoSimulado.objects.filter(
        aplicacao_agendada__gte=timezone.now()).filter(
        aplicacao_agendada__lte=amanha)

    if aplicacoes:
        for aplicacao in aplicacoes:
            mentoria = Mentorias.objects.get(simulados_mentoria=aplicacao)
            print(mentoria)

            email_template_name = "mentorias/simulados/simulado_email.txt"
            c = {
                'domain': settings.DOMAIN,
                'site_name': settings.SITE_NAME,
                'mentor': aplicacao.simulado.mentor,
                'aluno': aplicacao.aluno.nome_aluno,
                'protocol': settings.PROTOCOLO,
                'senha_do_aluno': aplicacao.senha_do_aluno
            }
            mensagem_email = render_to_string(email_template_name, c)
            send_mail(
                f"Novo simulado na mentoria {mentoria}",
                mensagem_email,
                settings.NOREPLY_EMAIL,
                [aplicacao.aluno.email_aluno]
            )
