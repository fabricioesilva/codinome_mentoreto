from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.utils.translation import gettext as _
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth import logout
from chartjs.views.lines import BaseLineChartView
import random
import string
import copy
import json
import os
from datetime import date

from .models import (
    Mentoria, Materias, Alunos, Simulados, LinksExternos, AplicacaoSimulado,
    ArquivosMentoria, RespostasSimulados, ArquivosAluno, MatriculaAlunoMentoria
)
from .forms import (
    CriarMentoriaForm, CadastrarAlunoForm, CadastrarSimuladoForm, CadastrarMateriaForm, MatriculaAlunoMentoriaForm,
    ConfirmMentorPasswordForm, LinksExternosForm
)

# Create your views here.


class MentoriasView(View):
    template_name = 'mentorias/mentorias_mentor.html'

    def post(self, request, *args, **kwargs):
        if request.POST.get('mentoria-remover'):
            Mentoria.objects.get(pk=int(request.POST.get('mentoria-remover'))).delete()
            return JsonResponse({'data': True})

    def get(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return redirect('usuarios:index')
        ctx = {
            'mentorias': Mentoria.objects.filter(mentor=request.user)
        }
        return render(request, self.template_name, ctx)


def criar_mentoria(request):
    if request.user.is_anonymous:
        return redirect('usuarios:index')
    template_name = 'mentorias/criar_mentoria.html'
    form = CriarMentoriaForm()
    if request.method == 'POST':
        form = CriarMentoriaForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.mentor = request.user
            instance.save()
            messages.success(request, _('Mentoria criada com sucesso!'))
            return redirect('usuarios:home_mentor')
        else:
            form = CriarMentoriaForm(request.POST)
    return render(request, template_name, {'form': form})


@login_required
def mentoria_detalhe(request, pk):
    mentoria = get_object_or_404(Mentoria, pk=pk)
    if request.user != mentoria.mentor:
        return redirect('usuarios:index')
    alunos_atuais = mentoria.matriculas.filter(encerra_em__gte=date.today())
    if request.method == 'POST':
        if request.POST.get('link-remover'):
            link_remover = LinksExternos.objects.get(pk=int(request.POST.get('link-remover')))
            mentoria.links_externos.remove(link_remover)
            mentoria.save()
            link_remover.delete()
            return JsonResponse({'data': True})
        if request.POST.get('matricula-remover'):
            alunos_atuais.filter(pk=int(request.POST.get('matricula-remover')))[0].delete()
            return JsonResponse({'data': True})
        if request.FILES.get('arquivo', None):
            ArquivosMentoria.objects.create(
                mentoria=mentoria,
                mentor=request.user,
                arquivo_mentoria=request.FILES.get('arquivo', None)
            )
            return JsonResponse({'data': True})
        if request.POST.get('arquivo-remover'):
            arquivo = ArquivosMentoria.objects.get(id=int(request.POST.get('arquivo-remover')))
            os.remove(arquivo.arquivo_mentoria.path)
            arquivo.delete()
            return JsonResponse({'data': True})
        if request.POST.get('controle'):
            texto = request.POST.get('controle')
            if texto == 'false':
                texto = ''
            mentoria.controle = texto
            mentoria.save()
            return JsonResponse({'data': True})
        if request.POST.get('situacao-mentoria'):
            situacao = 'Ativa'
            if mentoria.ativa:
                mentoria.ativa = False
                situacao = 'Inativa'
            else:
                mentoria.ativa = True
            mentoria.save()
            return JsonResponse({'situacao': situacao})
        if request.POST.get('resumo'):
            texto = request.POST.get('resumo')
            if texto == 'false':
                texto = ''
            mentoria.resumo_mentoria = texto
            mentoria.save()
            return JsonResponse({'data': True})
        if request.POST.get('titulo-novo'):
            mentoria.titulo = request.POST.get('titulo-novo')
            mentoria.save()
            return JsonResponse({'data': True})
    ex_alunos = mentoria.matriculas.filter(encerra_em__lt=date.today())
    ctx = {
        'mentoria': mentoria,
        'alunos_atuais': alunos_atuais,
        'ex_alunos': ex_alunos,
    }
    return render(request, 'mentorias/mentoria_detalhe.html', ctx)


@login_required
def mentoria_apagar(request, pk):
    mentoria = Mentoria.objects.get(pk=pk)
    if request.user != mentoria.mentor:
        return redirect('usuarios:index')
    template_name = 'mentorias/mentoria_apagar.html'
    form = ConfirmMentorPasswordForm
    ctx = {
        'mentoria': mentoria,
        'form': form
    }
    if request.method == 'POST':
        form = ConfirmMentorPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            senha_correta = request.user.check_password(password)
            if senha_correta:
                mentoria.delete()
                return redirect('mentorias:mentorias_mentor')
            else:
                messages.error(request, _('Senha incorreta!'))
    return render(request, template_name, ctx)


@login_required
def alunos_mentor(request):
    if request.method == 'POST':
        if request.POST.get('aluno-remover'):
            Alunos.objects.get(id=int(request.POST.get('aluno-remover'))).delete()
        return JsonResponse({'data': True})
    ctx = {
        'alunos': Alunos.objects.filter(mentor=request.user)
    }
    return render(request, 'mentorias/alunos/alunos_mentor.html', ctx)


@login_required
def simulados_mentor(request):
    ctx = {
        'simulados': Simulados.objects.filter(mentor=request.user)
    }
    return render(request, 'mentorias/simulados/simulados_mentor.html', ctx)


@login_required
def materias_mentor(request):
    if request.method == 'POST':
        Materias.objects.get(id=int(request.POST.get('materia-remover'))).delete()
        return JsonResponse({'data': True})
    ctx = {
        'materias': Materias.objects.filter(mentor=request.user)
    }
    return render(request, 'mentorias/materias/materias_mentor.html', ctx)


@login_required
def cadastrar_aluno(request):
    form = CadastrarAlunoForm()
    if request.method == 'POST':
        form = CadastrarAlunoForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.mentor = request.user
            instance.save()
            messages.success(request, _('Aluno criado com sucesso!'))
            return redirect('usuarios:home_mentor')
        else:
            messages.error(request, _('Erro ao cadastrar aluno!'))
            form = CadastrarAlunoForm(request.POST)
    return render(request, 'mentorias/alunos/cadastrar_aluno.html', {'form': form})


@login_required
def cadastrar_simulado(request):
    template_name = 'mentorias/simulados/cadastrar_simulado.html'
    form = CadastrarSimuladoForm()
    if request.method == 'POST':
        form = CadastrarSimuladoForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.mentor = request.user
            instance.save()
            messages.success(request, _('Simulado criado com sucesso!'))
            return redirect('usuarios:home_mentor')
        else:
            messages.error(request, _('Erro ao criar simulado!'))
            form = CadastrarSimuladoForm(request.POST)
    return render(request, template_name, {'form': form})


@login_required
def aluno_matricular(request, pk):
    mentoria = Mentoria.objects.get(pk=pk)
    if request.user != mentoria.mentor:
        return redirect('usuarios:index')
    template_name = 'mentorias/aluno_matricular.html'
    form = MatriculaAlunoMentoriaForm(mentor=request.user)
    ctx = {
        'form': form,
        'mentoria': mentoria
    }
    if request.method == 'POST':
        form = MatriculaAlunoMentoriaForm(mentor=request.user, data=request.POST)
        if form.is_valid():
            for aluno in form.cleaned_data.get('aluno'):
                nova_matricula = True
                existente = mentoria.matriculas.filter(aluno=aluno)
                if existente:
                    for item in existente:
                        if item.encerra_em > date.today():
                            messages.warning(request, _(
                                f"O aluno {item.aluno} já possui matrícula com vencimento vigente, {item.encerra_em}."))
                            nova_matricula = False
                if nova_matricula:
                    matricula = MatriculaAlunoMentoria.objects.create(aluno=aluno,
                                                                      encerra_em=form.cleaned_data.get('encerra_em'))
                    mentoria.matriculas.add(matricula)
                    email_template_name = "mentorias/matriculas/matricula_email.txt"
                    c = {
                        'domain': settings.DOMAIN,
                        'site_name': settings.SITE_NAME,
                        'mentor': mentoria.mentor,
                        'aluno': matricula.aluno.nome_aluno,
                        'protocol': settings.PROTOCOLO,
                        'senha_do_aluno': matricula.senha_do_aluno,
                        'matricula_id': matricula.id
                    }
                    mensagem_email = render_to_string(email_template_name, c)
                    send_mail(
                        f"Nova matricula na mentoria {mentoria}",
                        mensagem_email,
                        settings.NOREPLY_EMAIL,
                        [matricula.aluno.email_aluno]
                    )
            return redirect('mentorias:mentoria_detalhe', pk=pk)
    return render(request, template_name, ctx)


@login_required
def cadastrar_materia(request):
    template_name = 'mentorias/materias/cadastrar_materia.html'
    form = CadastrarMateriaForm()
    if request.method == 'POST':
        form = CadastrarMateriaForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.mentor = request.user
            instance.save()
            messages.success(request, _('Matéria criada com sucesso!'))
            return redirect('mentorias:materias')
        else:
            messages.error(request, _('Erro ao criar matéria!'))
            form = CadastrarMateriaForm(request.POST)
    return render(request, template_name, {'form': form})


@login_required
def aluno_detalhe(request, pk):
    aluno = get_object_or_404(Alunos, pk=pk)
    if request.user != aluno.mentor:
        return redirect('usuarios:index')
    template_name = 'mentorias/alunos/aluno_detalhe.html'
    simulados_realizados = RespostasSimulados.objects.filter(
        email_aluno=aluno.email_aluno,
        simulado__in=Simulados.objects.filter(mentor=request.user)).count()
    if request.method == 'POST':
        if request.POST.get('situacao_aluno'):
            if aluno.situacao_aluno == 'at':
                aluno.situacao_aluno = 'ex'
            else:
                aluno.situacao_aluno = 'at'
            aluno.save()
            return JsonResponse({'situacao': aluno.get_situacao_aluno_display()})
        elif request.POST.get('aluno-remover'):
            Alunos.objects.get(id=int(request.POST.get('aluno-remover'))).delete()
            return JsonResponse({'redirect_to': reverse('mentorias:alunos')})

        elif request.POST.get('controle'):
            texto = request.POST.get('controle')
            if texto == 'false':
                texto = ''
            aluno.controle = texto
            aluno.save()
            return JsonResponse({'data': True})
        elif request.FILES.get('arquivo', None):
            ArquivosAluno.objects.create(
                mentor_nome=aluno.mentor.first_name,
                arquivo_aluno=request.FILES.get('arquivo', None),
                email_aluno=aluno.email_aluno,
                student_user=aluno.student_user or None,
                aluno=aluno
            )
        elif request.POST.get('arquivo-remover'):
            arquivo = ArquivosAluno.objects.get(id=int(request.POST.get('arquivo-remover')))
            os.remove(arquivo.arquivo_aluno.path)
            arquivo.delete()
            return JsonResponse({'data': True})
        else:
            return JsonResponse({'data': True})
    ctx = {
        'aluno': aluno,
        'simulados_realizados': simulados_realizados
    }
    return render(request, template_name, ctx)


@login_required
def editar_aluno(request, pk):
    aluno = get_object_or_404(Alunos, pk=pk)
    if request.user != aluno.mentor:
        return redirect('usuarios:index')
    form = CadastrarAlunoForm(instance=aluno)
    if request.method == 'POST':
        email_atual = copy.deepcopy(aluno.email_aluno)
        form = CadastrarAlunoForm(request.POST, instance=aluno)
        if form.is_valid():
            email = form.cleaned_data['email_aluno']
            if email_atual != email:
                if Alunos.objects.filter(email_aluno=email).exists():
                    messages.error(request, _('Este email já existe.'))
                    form = CadastrarAlunoForm(request.POST, instance=aluno)
                    return render(request, 'mentorias/alunos/cadastrar_aluno.html', {'form': form})
            form.save(commit=True)
            messages.success(request, _('Alterado com sucesso!'))
            return redirect('mentorias:aluno_detalhe', pk=pk)
        else:
            messages.error(request, _('Erro ao alterar dados! Tente novamente mais tarde.'))
            form = CadastrarAlunoForm(request.POST)
    return render(request, 'mentorias/alunos/cadastrar_aluno.html', {'form': form})


@login_required
def simulado_detalhe(request, pk):
    simulado = Simulados.objects.get(pk=pk)
    if request.user != simulado.mentor:
        return redirect('usuarios:index')
    template_name = 'mentorias/simulados/simulado_detalhe.html'
    ctx = {
        'simulado': simulado,
    }
    if request.method == 'POST':
        if request.POST.get('controle'):
            texto = request.POST.get('controle')
            if texto == 'false':
                texto = ''
            simulado.controle = texto
            simulado.save()
            return JsonResponse({'data': True})
        if request.FILES.get('arquivo'):
            simulado.arquivo_prova = request.FILES.get('arquivo')
            simulado.save()
            return JsonResponse({'data': True})
        if request.POST.get('titulo-novo'):
            simulado.titulo = request.POST.get('titulo-novo')
            simulado.save()
            return JsonResponse({'data': True})
        if request.POST.get('simulado-remover'):
            Simulados.objects.get(id=int(request.POST.get('simulado-remover'))).delete()
            return JsonResponse({'redirect_to': reverse('mentorias:simulados')})
    return render(request, template_name, ctx)


@login_required
def materia_detalhe(request, pk):
    materia = Materias.objects.get(pk=pk)
    if request.user != materia.mentor:
        return redirect('usuarios:index')
    template_name = 'mentorias/materias/materia_detalhe.html'
    if request.method == 'POST':
        if request.POST.get('titulo-novo'):
            materia.titulo = request.POST.get('titulo-novo')
            materia.save()
            return JsonResponse({'data': True})
        if request.POST.get('peso-novo'):
            materia.peso = request.POST.get('peso-novo')
            materia.save()
            return JsonResponse({'data': True})
    ctx = {
        'materia': materia
    }
    return render(request, template_name, ctx)


@login_required
def cadastrar_gabarito(request, pk):
    simulado = Simulados.objects.get(pk=pk)
    if request.user != simulado.mentor:
        return redirect('usuarios:index')
    template_name = 'mentorias/simulados/cadastrar_gabarito.html'
    materias = Materias.objects.filter(mentor=request.user)
    ctx = {
        'simulado': simulado,
        'materias': materias
    }
    if request.method == 'POST':
        if request.POST.get('gabaritoJson'):
            simulado.gabarito = json.loads(request.POST.get('gabaritoJson'))
            simulado.save()
            return JsonResponse({'data': True})
        if request.POST.get('gabarito-remover'):
            simulado.gabarito = None
            simulado.save()
            return JsonResponse({'data': True})
    return render(request, template_name, ctx)


@login_required
def links_externos(request, pk):
    mentoria = Mentoria.objects.get(pk=pk)
    if request.user != mentoria.mentor:
        return redirect('usuarios:index')
    template_name = 'mentorias/links_externos.html'
    form = LinksExternosForm()
    ctx = {
        'mentoria': mentoria,
        'form': form
    }
    if request.method == 'POST':
        form = LinksExternosForm(request.POST)
        instance = form.save()
        instance.save()
        mentoria.links_externos.add(instance)
        mentoria.save()
        messages.success(request, _('Link adicionado com sucesso.'))
        return redirect('mentorias:mentoria_detalhe', pk=pk)
    return render(request, template_name, ctx)


@login_required
def aplicar_simulado(request, pk):
    mentoria = Mentoria.objects.get(pk=pk)
    if request.user != mentoria.mentor:
        return redirect('usuarios:index')
    if request.method == 'POST':
        aplicacao = json.loads(request.POST.get('aplicacao'))
        simulado = Simulados.objects.get(pk=int(aplicacao['simulado']))
        data_aplicacao = aplicacao['aplicacao_agendada']
        data_aplicacao = timezone.datetime.strptime(data_aplicacao, "%Y-%m-%dT%H:%M")
        qtd = 0
        for id in aplicacao['alunos']:
            aluno = Alunos.objects.get(pk=int(id))
            matricula = mentoria.matriculas.filter(aluno=aluno, encerra_em__gte=timezone.now())[0]
            if AplicacaoSimulado.objects.filter(aluno=aluno, simulado=simulado, matricula=matricula):
                continue
            nova_aplicacao = AplicacaoSimulado.objects.create(
                aluno=aluno,
                simulado=simulado,
                aplicacao_agendada=data_aplicacao,
                matricula=matricula
            )
            mentoria.simulados_mentoria.add(nova_aplicacao)
            email_template_name = "mentorias/simulados/simulado_email.txt"
            c = {
                'domain': settings.DOMAIN,
                'site_name': settings.SITE_NAME,
                'mentor': mentoria.mentor,
                'aluno': aluno.nome_aluno,
                'protocol': settings.PROTOCOLO,
                'senha_do_aluno': matricula.senha_do_aluno,
                'matricula_id': matricula.id
            }
            mensagem_email = render_to_string(email_template_name, c)
            send_mail(
                f"Novo simulado na mentoria {mentoria}",
                mensagem_email,
                settings.NOREPLY_EMAIL,
                [aluno.email_aluno]
            )
            qtd += 1
        if qtd > 0:
            messages.success(request, _(f'Aplicação de simulado para {qtd} aluno(s) foi salva.'))
        else:
            messages.warning(request, _('Este simulado não é novo para estes aluno.'))
        return JsonResponse({'redirect_to': reverse('mentorias:mentoria_detalhe', kwargs={'pk': pk})})
    template_name = 'mentorias/simulados/aplicar_simulado.html'
    matriculas = mentoria.matriculas.filter(encerra_em__gte=date.today())
    turma = []
    for matricula in matriculas:
        turma.append(matricula.aluno)
    alunos = []
    for aluno in turma:
        aplicacao_aluno = AplicacaoSimulado.objects.filter(
            simulado__in=Simulados.objects.filter(mentor=mentoria.mentor).all()).filter(
            aluno=aluno).count()
        ultima_resposta = AplicacaoSimulado.objects.filter(
            simulado__in=Simulados.objects.filter(mentor=mentoria.mentor).all()).filter(
            aluno=aluno, resposta_alunos__isnull=False).order_by('-data_resposta').first()
        if ultima_resposta:
            ultima_resposta = ultima_resposta.data_resposta
        else:
            ultima_resposta = False
        respondeu = AplicacaoSimulado.objects.filter(
            simulado__in=Simulados.objects.filter(mentor=mentoria.mentor).all()).filter(
            aluno=aluno, resposta_alunos__isnull=False).count()
        alunos.append(({
            'pk': aluno.pk,
            'nome': aluno.nome_aluno,
            'aplicacao_aluno': aplicacao_aluno,
            'respondeu': respondeu,
            'falta_resposta': aplicacao_aluno - respondeu,
            'ultima_resposta': ultima_resposta
        }))
    simulados = Simulados.objects.filter(mentor=mentoria.mentor, gabarito__isnull=False)
    simulados_choices = []
    for simulado in simulados:
        simulados_choices.append(
            {
                'pk': simulado.pk,
                'titulo': simulado.titulo
            }
        )
    ctx = {
        'mentoria': mentoria,
        'alunos': alunos,
        'simulados': simulados
    }
    return render(request, template_name, ctx)


@login_required
def simulados_aplicados(request, pk):
    mentoria = Mentoria.objects.get(pk=pk)
    if request.user != mentoria.mentor:
        return redirect('usuarios:index')
    if request.method == 'POST':
        if request.POST.get('aplicacao-remover'):
            aplicacao = AplicacaoSimulado.objects.get(pk=int(request.POST.get('aplicacao-remover')))
            mentoria.simulados_mentoria.remove(aplicacao)
            aplicacao.delete()
            messages.success(request, _('Aplicação removida com sucesso!'))
        return JsonResponse({"data": True})
    simulados_aplicados = mentoria.simulados_mentoria.all().order_by('-id')
    ctx = {
        'mentoria': mentoria,
        'simulados_aplicados': simulados_aplicados
    }
    template_name = 'mentorias/simulados_aplicados.html'
    return render(request, template_name, ctx)


def aluno_anonimo_aplicacao(request, pk):
    # http://127.0.0.1:8000/mentor/simulados/respostas/39/
    if not request.user.is_anonymous:
        logout(request)
    # from dateutil import parser
    aplicacao = get_object_or_404(AplicacaoSimulado, pk=pk)
    if timezone.make_naive(aplicacao.aplicacao_agendada) > timezone.now():
        messages.info(request, 'Esta aplicação está agendada para o dia {}, às {}H.'.format(
            aplicacao.aplicacao_agendada.strftime("%m/%d/%Y"), aplicacao.aplicacao_agendada.strftime("%H:%M")))
        return redirect('usuarios:index')
    if request.method == 'POST':
        resposta_aplicacao = {}
        gabarito = aplicacao.simulado.gabarito
        acertos = 0
        quantidade = aplicacao.simulado.gabarito['total']['questoes']
        total_pontos = aplicacao.simulado.gabarito['total']['pontos']
        if request.session.has_key('aluno_entrou'):
            if request.POST.get('respostas'):
                resposta_aplicacao['resumo'] = {
                    'acertos': 0, 'erros': 0, 'anulada': 0,
                    'quantidade': quantidade,
                    'percentual': 0
                }
                resposta_aplicacao['questoes'] = {}
                resposta_aplicacao['analitico'] = {'questoes': {}, 'total': {}}
                resposta_aplicacao['analitico']['total'] = {
                    'pontos_ponderado': 0,
                    'total_pontos': total_pontos,
                    'percentual_pontos': 0
                }
                respostas = json.loads(request.POST.get('respostas'))
                for resposta in respostas:
                    resposta_aplicacao['questoes'][resposta] = {
                        'gabarito': gabarito['questoes'][resposta]['resposta'],
                        'resposta': respostas[resposta]
                    }
                    if respostas[resposta] == gabarito['questoes'][resposta]['resposta']:
                        acertos += 1
                        resposta_aplicacao['resumo']['acertos'] += 1
                        resposta_aplicacao['analitico']['total']['pontos_ponderado'] += int(
                            gabarito['questoes'][resposta]['peso'])
                        if gabarito['questoes'][resposta]['materia'] in resposta_aplicacao['analitico']['questoes']:
                            resposta_aplicacao['analitico']['questoes'][
                                gabarito['questoes'][resposta]['materia']]['quantidade'] += 1
                            resposta_aplicacao['analitico']['questoes'][
                                gabarito['questoes'][resposta]['materia']]['acertos'] += 1
                            resposta_aplicacao['analitico']['questoes'][gabarito['questoes'][resposta][
                                'materia']]['pontos'] += int(gabarito['questoes'][resposta]['peso'])
                            resposta_aplicacao['analitico']['questoes'][
                                gabarito['questoes'][resposta]['materia']]['percentual_acertos'] = round(
                                (resposta_aplicacao['analitico']['questoes']
                                 [gabarito['questoes'][resposta]['materia']]['acertos'] /
                                 resposta_aplicacao['analitico']['questoes']
                                 [gabarito['questoes'][resposta]['materia']]['quantidade']) * 100,
                                1)
                        else:
                            resposta_aplicacao['analitico']['questoes'][
                                gabarito['questoes'][resposta]['materia']] = {
                                'quantidade': 1,
                                    'peso': int(gabarito['questoes'][resposta]['peso']),
                                    'acertos': 1,
                                    'percentual_acertos': 0,
                                    'pontos': int(gabarito['questoes'][resposta]['peso'])
                            }
                    elif gabarito['questoes'][resposta]['resposta'] == 'X':
                        resposta_aplicacao['resumo']['anulada'] += 1
                    else:
                        if gabarito['questoes'][resposta]['materia'] in resposta_aplicacao['analitico']['questoes']:
                            resposta_aplicacao['analitico']['questoes'][
                                gabarito['questoes'][resposta]['materia']]['quantidade'] += 1
                            resposta_aplicacao['analitico']['questoes'][
                                gabarito['questoes'][resposta]['materia']]['percentual_acertos'] = round(
                                (resposta_aplicacao['analitico']['questoes']
                                 [gabarito['questoes'][resposta]['materia']]['acertos'] /
                                 resposta_aplicacao['analitico']['questoes']
                                 [gabarito['questoes'][resposta]['materia']]['quantidade']) * 100,
                                1) if resposta_aplicacao['analitico']['questoes'][
                                gabarito['questoes'][resposta]['materia']]['acertos'] > 0 else 0
                        else:
                            resposta_aplicacao['analitico']['questoes'][
                                gabarito['questoes'][resposta]['materia']] = {
                                'quantidade': 1,
                                    'peso': int(gabarito['questoes'][resposta]['peso']),
                                    'acertos': 0,
                                    'percentual_acertos': 0,
                                    'pontos': 0
                            }
                        resposta_aplicacao['resumo']['erros'] += 1

                resposta_aplicacao['resumo']['percentual'] = round(
                    (acertos / quantidade) * 100, 1) if acertos > 0 else 0
                resposta_aplicacao['analitico']['total']['percentual_pontos'] = round(
                    (resposta_aplicacao['analitico']['total']['pontos_ponderado'] / total_pontos) * 100, 1) if resposta_aplicacao['analitico']['total']['pontos_ponderado'] > 0 else 0
                salva_estatistica_matricula(aplicacao.matricula, gabarito, respostas)
                aplicacao.resposta_alunos = resposta_aplicacao
                aplicacao.data_resposta = date.today()
                aplicacao.save()
                return JsonResponse({'data': True})
        else:
            senha_enviada = request.POST.get('senha_aplicacao')
            email_enviado = request.POST.get('email')
            if (senha_enviada, email_enviado) == (aplicacao.senha_do_aluno, aplicacao.aluno.email_aluno):
                request.session['aluno_entrou'] = aplicacao.aluno.email_aluno
                return JsonResponse({'data': True})
            else:
                return JsonResponse({'data': False})
    session_ok = False
    if request.session.has_key('aluno_entrou'):
        if request.session['aluno_entrou'] == aplicacao.aluno.email_aluno:
            session_ok = True
        else:
            del request.session['aluno_entrou']
    ctx = {
        "aplicacao": aplicacao,
        "respondido": True if aplicacao.resposta_alunos else False,
        "session_ok": session_ok
    }
    template_name = 'mentorias/simulados/aluno_anonimo_aplicacao.html'
    return render(request, template_name, ctx)


@login_required
def matricula_detalhe(request, pk):
    template_name = 'mentorias/matriculas/matricula_detalhe.html'
    matricula = get_object_or_404(MatriculaAlunoMentoria, pk=pk)
    mentoria = Mentoria.objects.get(matriculas__id=pk)
    if request.method == 'POST':
        if request.POST.get('aplicacao-remover'):
            AplicacaoSimulado.objects.get(id=int(request.POST.get('aplicacao-remover'))).delete()
            print('#### removendo....')
            return JsonResponse({'data': True})
        if request.POST.get('dataMatricula'):
            data = request.POST.get('dataMatricula').split('-')
            data_resposta = data[2]+'/' + data[1]+'/'+data[0]
            data = date(int(data[0]), int(data[1]), int(data[2]))
            matricula.encerra_em = data
            matricula.save()
            return JsonResponse({'data': data_resposta})
        if request.POST.get('gerarSenha'):
            letters = string.ascii_lowercase
            result_str = ''.join(random.choice(letters) for i in range(6))
            matricula.senha_do_aluno = result_str
            matricula.save()
            email_template_name = "mentorias/matriculas/nova_senha_na_matricula.txt"
            c = {
                'domain': settings.DOMAIN,
                'site_name': settings.SITE_NAME,
                'mentor': mentoria.mentor,
                'aluno': matricula.aluno.nome_aluno,
                'protocol': settings.PROTOCOLO,
                'senha_do_aluno': matricula.senha_do_aluno,
                'matricula_id': matricula.id
            }
            mensagem_email = render_to_string(email_template_name, c)
            send_mail(
                f"Alteração de senha na mentoria {mentoria}",
                mensagem_email,
                settings.NOREPLY_EMAIL,
                [matricula.aluno.email_aluno]
            )
            return JsonResponse({'data': matricula.senha_do_aluno})
    aplicacoes = AplicacaoSimulado.objects.filter(matricula=matricula)
    if request.user != mentoria.mentor:
        return redirect('usuarios:index')
    ctx = {
        'matricula': matricula,
        'mentoria': mentoria,
        'aplicacoes': aplicacoes,
    }
    return render(request, template_name, ctx)


@login_required
def resultado_detalhe(request, pk):
    aplicacao = get_object_or_404(AplicacaoSimulado, pk=pk)
    mentoria = Mentoria.objects.filter(simulados_mentoria__id=pk)[0]
    if request.user != mentoria.mentor:
        return redirect('usuarios:index')
    template_name = 'mentorias/matriculas/resultado_detalhe.html'
    ctx = {
        'aplicacao': aplicacao
    }
    return render(request, template_name, ctx)


@login_required
def aplicacao_individual(request, pk):
    matricula = MatriculaAlunoMentoria.objects.get(pk=pk)
    mentoria = Mentoria.objects.filter(matriculas__id=matricula.id)[0]
    if request.user != matricula.aluno.mentor:
        return redirect('usuarios:index')
    if request.method == 'POST':
        aplicacao = json.loads(request.POST.get('aplicacao'))
        simulado = Simulados.objects.get(pk=aplicacao['simulado'])
        data_aplicacao = aplicacao['aplicacao_agendada']
        data_aplicacao = timezone.datetime.strptime(data_aplicacao, "%Y-%m-%dT%H:%M")
        if not AplicacaoSimulado.objects.filter(aluno=matricula.aluno, simulado=simulado, matricula=matricula):
            nova_aplicacao = AplicacaoSimulado.objects.create(
                aluno=matricula.aluno,
                simulado=simulado,
                aplicacao_agendada=data_aplicacao,
                matricula=matricula
            )
            mentoria.simulados_mentoria.add(nova_aplicacao)
            email_template_name = "mentorias/simulados/simulado_email.txt"
            c = {
                'domain': settings.DOMAIN,
                'site_name': settings.SITE_NAME,
                'mentor': mentoria.mentor,
                'aluno': matricula.aluno.nome_aluno,
                'protocol': settings.PROTOCOLO,
                'senha_do_aluno': matricula.senha_do_aluno,
                'matricula_id': matricula.id
            }
            mensagem_email = render_to_string(email_template_name, c)
            send_mail(
                f"Novo simulado na mentoria {mentoria}",
                mensagem_email,
                settings.NOREPLY_EMAIL,
                [matricula.aluno.email_aluno]
            )
            messages.success(request, _(f'Aplicação de simulado para o aluno foi salva.'))
        else:
            messages.warning(request, _('Este simulado já foi aplicado a este aluno, nesta matrícula.'))
        return JsonResponse({'redirect_to': reverse('mentorias:matricula_detalhe', kwargs={'pk': pk})})
    template_name = 'mentorias/simulados/aplicacao_individual.html'

    simulados = Simulados.objects.filter(mentor=mentoria.mentor, gabarito__isnull=False)
    simulados_choices = []
    for simulado in simulados:
        simulados_choices.append(
            {
                'pk': simulado.pk,
                'titulo': simulado.titulo
            }
        )
    ctx = {
        'matricula': matricula,
        'simulados': simulados
    }
    return render(request, template_name, ctx)


def matricula_aluno_anonimo(request, pk):
    template_name = 'mentorias/alunos/matricula_aluno_anonimo.html'
    matricula = get_object_or_404(MatriculaAlunoMentoria, pk=pk)
    # if arquivos e link s e ondeleteSETNULL...
    if request.method == 'POST':
        senha_enviada = request.POST.get('senha_aplicacao')
        if senha_enviada == matricula.senha_do_aluno:
            request.session['aluno_entrou'] = matricula.aluno.email_aluno
            return JsonResponse({'data': True})
        else:
            return JsonResponse({'data': False})
    mentoria = Mentoria.objects.get(matriculas__id=pk)
    aplicacoes = AplicacaoSimulado.objects.filter(matricula=matricula)
    session_ok = False
    if request.session.has_key('aluno_entrou'):
        if request.session['aluno_entrou'] == matricula.aluno.email_aluno:
            session_ok = True
        else:
            del request.session['aluno_entrou']
    # del request.session['aluno_entrou']
    ctx = {
        'matricula': matricula,
        'mentoria': mentoria,
        'aplicacoes': aplicacoes,
        "session_ok": session_ok
    }
    return render(request, template_name, ctx)


# Funções que não são views, não são rotas
def salva_estatistica_matricula(matricula, gabarito, dicio):
    # Atualiza e salva a estatística da matricula, após simulado ser respondido.
    hoje = timezone.now().strftime('%d/%m/%y')
    estatistica = matricula.estatisticas
    if estatistica == None:
        estatistica = {}
    for index in dicio:
        materia = gabarito['questoes'][index]['materia']
        qtd_questoes = gabarito['resumo'][materia]['quantidade']
        if materia in estatistica:
            if gabarito['questoes'][index]['resposta'] == dicio[index]:
                if hoje in estatistica[materia]:
                    estatistica[materia][hoje] = (
                        (estatistica[materia][hoje] * qtd_questoes) + 100) / qtd_questoes
                else:
                    estatistica[materia][hoje] = round((1 / qtd_questoes)*100, 1)
        else:
            estatistica[materia] = {}
            if gabarito['questoes'][index]['resposta'] == dicio[index]:
                estatistica[materia][hoje] = round((1 / qtd_questoes) * 100, 1)
            else:
                estatistica[materia][hoje] = 0
    matricula.estatisticas = estatistica
    matricula.save()
    return


class LineChartJSONView(BaseLineChartView):

    def setup(self, *args, **kwargs):
        self.maior_tamanho = ['', 0]
        matricula = MatriculaAlunoMentoria.objects.get(pk=kwargs['pk'])
        self.estats = matricula.estatisticas
        for key in self.estats:
            if (len(self.estats[key]) > self.maior_tamanho[1]):
                self.maior_tamanho[1] = len(self.estats[key])
                self.maior_tamanho[0] = key
        super().setup(*args, **kwargs)

    def get_labels(self):
        """Return labels for the x-axis."""
        labels = []
        for key in self.estats:
            for dia in self.estats[key]:
                if key == self.maior_tamanho[0]:
                    labels.append(dia)
        return labels

    def get_providers(self):
        """Return names of datasets."""
        datasets = []
        for key in self.estats:
            datasets.append(key)
        return datasets

    def get_data(self):
        data = []
        for key in self.estats:
            if (len(self.estats[key]) > self.maior_tamanho[1]):
                self.maior_tamanho[1] = len(self.estats[key])
                self.maior_tamanho[0] = key
        for key in self.estats:
            valores = []
            for dia in self.estats[key]:
                valores.append(self.estats[key][dia])
            data.append(valores)
        return data
