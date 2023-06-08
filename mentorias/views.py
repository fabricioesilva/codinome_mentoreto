from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.utils.translation import gettext as _
from django.contrib import messages
import json

import copy
from django.utils import timezone
from datetime import date, datetime

from .models import (
    Mentorias, Materias, Alunos, Simulados, LinksExternos, AplicacaoSimulado,
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
            Mentorias.objects.get(pk=int(request.POST.get('mentoria-remover'))).delete()
            return JsonResponse({'data': True})

    def get(self, request, *args, **kwargs):
        ctx = {
            'mentorias': Mentorias.objects.filter(mentor=request.user)
        }
        return render(request, self.template_name, ctx)


def criar_mentoria(request):
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


def mentoria_detalhe(request, pk):
    mentoria = get_object_or_404(Mentorias, pk=pk)
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
            ArquivosMentoria.objects.get(id=int(request.POST.get('arquivo-remover'))).delete()
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


def mentoria_apagar(request, pk):
    mentoria = Mentorias.objects.get(pk=pk)
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
                return redirect('mentorias:mentorias_home')
            else:
                messages.error(request, _('Senha incorreta!'))
    return render(request, template_name, ctx)


def alunos_mentor(request):
    if request.method == 'POST':
        if request.POST.get('aluno-remover'):
            # Alunos.objects.get(id=int(request.POST.get('aluno-remover'))).delete()
            ...
        return JsonResponse({'data': True})
    ctx = {
        'alunos': Alunos.objects.filter(mentor=request.user)
    }
    return render(request, 'mentorias/alunos/alunos_mentor.html', ctx)


def simulados_mentor(request):
    ctx = {
        'simulados': Simulados.objects.filter(mentor=request.user)
    }
    return render(request, 'mentorias/simulados/simulados_mentor.html', ctx)


def materias_mentor(request):
    if request.method == 'POST':
        Materias.objects.get(id=int(request.POST.get('materia-remover'))).delete()
        return JsonResponse({'data': True})
    ctx = {
        'materias': Materias.objects.filter(mentor=request.user)
    }
    return render(request, 'mentorias/materias/materias_mentor.html', ctx)


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


def aluno_matricular(request, pk):
    template_name = 'mentorias/aluno_matricular.html'
    form = MatriculaAlunoMentoriaForm(mentor=request.user)
    mentoria = Mentorias.objects.get(pk=pk)
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
                    matriculado = MatriculaAlunoMentoria.objects.create(aluno=aluno,
                                                                        encerra_em=form.cleaned_data.get('encerra_em'))
                    mentoria.matriculas.add(matriculado)
            return redirect('mentorias:mentoria_detalhe', pk=pk)
    return render(request, template_name, ctx)


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


def aluno_detalhe(request, pk):
    template_name = 'mentorias/alunos/aluno_detalhe.html'
    aluno = get_object_or_404(Alunos, pk=pk)
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
            ArquivosAluno.objects.get(id=int(request.POST.get('arquivo-remover'))).delete()
            return JsonResponse({'data': True})
        else:
            return JsonResponse({'data': True})
    ctx = {
        'aluno': aluno,
        'simulados_realizados': simulados_realizados
    }
    return render(request, template_name, ctx)


def editar_aluno(request, pk):
    aluno = get_object_or_404(Alunos, pk=pk)
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


def simulado_detalhe(request, pk):
    template_name = 'mentorias/simulados/simulado_detalhe.html'
    simulado = Simulados.objects.get(pk=pk)
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


def materia_detalhe(request, pk):
    template_name = 'mentorias/materias/materia_detalhe.html'
    materia = Materias.objects.get(pk=pk)
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


def cadastrar_gabarito(request, pk):
    template_name = 'mentorias/simulados/cadastrar_gabarito.html'
    simulado = Simulados.objects.get(pk=pk)
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


def links_externos(request, pk):
    mentoria = Mentorias.objects.get(pk=pk)
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


def aplicar_simulado(request, pk):
    mentoria = Mentorias.objects.get(pk=pk)
    if request.method == 'POST':
        aplicacao = json.loads(request.POST.get('aplicacao'))
        simulado = Simulados.objects.get(pk=int(aplicacao['simulado']))
        data_aplicacao = aplicacao['aplicacao_agendada']
        data_aplicacao = timezone.datetime.strptime(data_aplicacao, "%Y-%m-%dT%H:%M")
        print(data_aplicacao)
        qtd = 0
        for id in aplicacao['alunos']:
            estudante = Alunos.objects.get(pk=int(id))
            if AplicacaoSimulado.objects.filter(aluno=estudante, simulado=simulado):
                messages.info(request, _(f'Aplicação já foi feita no aluno {estudante.nome_aluno}.'))
                continue
            qtd += 1
            nova_aplicacao = AplicacaoSimulado.objects.create(
                aluno=estudante,
                simulado=simulado,
                aplicacao_agendada=data_aplicacao
            )
            mentoria.simulados_mentoria.add(nova_aplicacao)
        if qtd > 0:
            messages.success(request, _(f'Aplicação de simulado para {qtd} aluno(s) foi salva.'))
        else:
            messages.warning(request, _('Este simulado não é novo para nenhum aluno.'))
        return JsonResponse({'redirect_to': reverse('mentorias:mentoria_detalhe', kwargs={'pk': pk})})
    template_name = 'mentorias/aplicar_simulado.html'
    matriculas = mentoria.matriculas.filter(encerra_em__gte=date.today())
    estudante = []
    for matricula in matriculas:
        estudante.append(matricula.aluno)
    alunos = []
    for aluno in estudante:
        aplicacao_aluno = AplicacaoSimulado.objects.filter(
            simulado__in=Simulados.objects.filter(mentor=mentoria.mentor).all()).filter(
            aluno=aluno).count()
        ultima_resposta = AplicacaoSimulado.objects.filter(
            simulado__in=Simulados.objects.filter(mentor=mentoria.mentor).all()).filter(
            aluno=aluno, respostas_alunos__isnull=False).order_by('-data_resposta').first()
        if ultima_resposta:
            ultima_resposta = ultima_resposta.data_resposta
        else:
            ultima_resposta = False
        respondeu = AplicacaoSimulado.objects.filter(
            simulado__in=Simulados.objects.filter(mentor=mentoria.mentor).all()).filter(
            aluno=aluno, respostas_alunos__isnull=False).count()
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


def simulados_aplicados(request, pk):
    mentoria = Mentorias.objects.get(pk=pk)
    if request.method == 'POST':
        if request.POST.get('aplicacao-remover'):
            aplicacao = AplicacaoSimulado.objects.get(pk=int(request.POST.get('aplicacao-remover')))
            mentoria.simulados_mentoria.remove(aplicacao)
            aplicacao.delete()
            messages.success(request, _('Aplicação removida com sucesso!'))
        return JsonResponse({"data": True})
    simulados_aplicados = mentoria.simulados_mentoria.all()
    ctx = {
        'mentoria': mentoria,
        'simulados_aplicados': simulados_aplicados
    }
    template_name = 'mentorias/simulados_aplicados.html'
    return render(request, template_name, ctx)
