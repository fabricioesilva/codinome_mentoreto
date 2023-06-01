from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.utils.translation import gettext as _
from django.contrib import messages
import json

import copy
from datetime import date

from .models import (
    Mentorias, Materias, Alunos, Simulados, ArquivosMentor,
    ArquivosMentoria, RespostasSimulados, ArquivosAluno, MatriculaAlunoMentoria
)
from .forms import (
    CriarMentoriaForm, CadastrarAlunoForm, EnviarArquivoForm,
    CadastrarSimuladoForm, CadastrarMateriaForm, MatriculaAlunoMentoriaForm,
    ConfirmMentorPasswordForm
)

# Create your views here.


class MentoriasView(View):
    template_name = 'mentorias/mentorias_mentor.html'

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
    ex_alunos = mentoria.matriculas.filter(encerra_em__lt=date.today())
    if request.method == 'POST':
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
            mentoria.controle = request.POST.get('controle')
            mentoria.save()
        if request.POST.get('titulo-novo'):
            mentoria.titulo = request.POST.get('titulo-novo')
            mentoria.save()
            return JsonResponse({'data': True})
    ctx = {
        'mentoria': mentoria,
        'alunos_atuais': alunos_atuais,
        'ex_alunos': ex_alunos
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
    ctx = {
        'alunos': Alunos.objects.filter(mentor=request.user)
    }
    return render(request, 'mentorias/alunos_mentor.html', ctx)


def simulados_mentor(request):
    ctx = {
        'simulados': Simulados.objects.filter(mentor=request.user)
    }
    return render(request, 'mentorias/simulados_mentor.html', ctx)


def arquivos_mentor(request):
    ctx = {
        'arquivos': ArquivosMentor.objects.filter(mentor=request.user)
    }
    return render(request, 'mentorias/arquivos_mentor.html', ctx)


def materias_mentor(request):
    ctx = {
        'materias': Materias.objects.filter(mentor=request.user)
    }
    return render(request, 'mentorias/materias_mentor.html', ctx)


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
    return render(request, 'mentorias/cadastrar_aluno.html', {'form': form})


def cadastrar_simulado(request):
    template_name = 'mentorias/cadastrar_simulado.html'
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
                matriculado = MatriculaAlunoMentoria.objects.create(aluno=aluno,
                                                                    encerra_em=form.cleaned_data.get('encerra_em'))
                mentoria.matriculas.add(matriculado)
    return render(request, template_name, ctx)


def cadastrar_materia(request):
    template_name = 'mentorias/cadastrar_materia.html'
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


def enviar_arquivo(request):
    template_name = 'mentorias/enviar_arquivo.html'
    form = EnviarArquivoForm()
    if request.method == 'POST':
        form = EnviarArquivoForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.mentor = request.user
            instance.save()
            messages.success(request, _('Arquivo salvo no seu diretório.'))
            return redirect('usuarios:home_mentor')
        else:
            messages.error(request, _('Erro ao enviar o arquivo!'))
            form = EnviarArquivoForm(request.POST)
    return render(request, template_name, {'form': form})


def aluno_detalhe(request, pk):
    template_name = 'mentorias/aluno_detalhe.html'
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
            aluno.controle = request.POST.get('controle')
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
                    return render(request, 'mentorias/cadastrar_aluno.html', {'form': form})
            form.save(commit=True)
            messages.success(request, _('Alterado com sucesso!'))
            return redirect('mentorias:aluno_detalhe', pk=pk)
        else:
            messages.error(request, _('Erro ao alterar dados! Tente novamente mais tarde.'))
            form = CadastrarAlunoForm(request.POST)
    return render(request, 'mentorias/cadastrar_aluno.html', {'form': form})


def simulado_detalhe(request, pk):
    template_name = 'mentorias/simulado_detalhe.html'
    simulado = Simulados.objects.get(pk=pk)
    ctx = {
        'simulado': simulado,
    }
    if request.method == 'POST':
        if request.POST.get('controle'):
            simulado.controle = request.POST.get('controle')
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
    return render(request, template_name, ctx)


def materia_detalhe(request, pk):
    template_name = 'mentorias/materia_detalhe.html'
    materia = Materias.objects.get(pk=pk)
    ctx = {
        'materia': materia,
    }
    if request.method == 'POST':
        if request.POST.get('controle'):
            materia.controle = request.POST.get('controle')
            materia.save()
            return JsonResponse({'data': True})
        if request.POST.get('titulo-novo'):
            materia.titulo = request.POST.get('titulo-novo')
            materia.save()
            return JsonResponse({'data': True})
    return render(request, template_name, ctx)


def cadastrar_gabarito(request, pk):
    template_name = 'mentorias/cadastrar_gabarito.html'
    simulado = Simulados.objects.get(pk=pk)
    materias = Materias.objects.filter(mentor=request.user)
    ctx = {
        'simulado': simulado,
        'range': range(1, simulado.questao_qtd + 1),
        'materias': materias
    }
    if request.method == 'POST':
        print('##########gabaritojson##########', request.POST.get('gabaritoJson'))
        simulado.gabarito = json.loads(request.POST.get('gabaritoJson'))
        simulado.save()
    return render(request, template_name, ctx)


# def gabaritos_mentor(request):
#     ctx = {
#         'gabaritos': Gabaritos.objects.filter(mentor=request.user)
#     }
#     return render(request, 'mentorias/gabaritos_mentor.html', ctx)

# def cadastrar_gabarito(request):
#     template_name = 'mentorias/cadastrar_gabarito.html'
#     form = CadastrarGabaritoForm()
#     if request.method == 'POST':
#         form = CadastrarGabaritoForm(request.POST)
#         if form.is_valid():
#             instance = form.save(commit=False)
#             instance.mentor = request.user
#             instance.save()
#             messages.success(request, _('Gabarito criado com sucesso!'))
#             return redirect('usuarios:home_mentor')
#         else:
#             messages.error(request, _('Erro ao criar gabarito!'))
#             form = CadastrarGabaritoForm(request.POST)
#     return render(request, template_name, {'form': form})
