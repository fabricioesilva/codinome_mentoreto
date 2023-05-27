from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.utils.translation import gettext as _
from django.contrib import messages

from .models import (
    Mentorias, Materias, Alunos, Simulados, Gabaritos, ArquivosMentor,
    ArquivosMentoria, RespostasSimulados, ArquivosAluno
)
from .forms import (
    CriarMentoriaForm, CadastrarAlunoForm, EnviarArquivoForm,
    CadastrarGabaritoForm, CadastrarSimuladoForm, CadastrarMateriaForm
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


def detalhe_mentoria(request, pk):
    mentoria = get_object_or_404(Mentorias, pk=pk)
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
            return JsonResponse({'data': True})
    ctx = {
        'mentoria': mentoria
    }
    return render(request, 'mentorias/mentoria_detalhe.html', ctx)


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


def gabaritos_mentor(request):
    ctx = {
        'gabaritos': Gabaritos.objects.filter(mentor=request.user)
    }
    return render(request, 'mentorias/gabaritos_mentor.html', ctx)


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


def cadastrar_gabarito(request):
    template_name = 'mentorias/cadastrar_gabarito.html'
    form = CadastrarGabaritoForm()
    if request.method == 'POST':
        form = CadastrarGabaritoForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.mentor = request.user
            instance.save()
            messages.success(request, _('Gabarito criado com sucesso!'))
            return redirect('usuarios:home_mentor')
        else:
            messages.error(request, _('Erro ao criar gabarito!'))
            form = CadastrarGabaritoForm(request.POST)
    return render(request, template_name, {'form': form})


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
            return redirect('usuarios:home_mentor')
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


def alunos_detalhar(request, pk):
    template_name = 'mentorias/aluno_detalhe.html'
    aluno = get_object_or_404(Alunos, pk=pk)
    # mentorias_matriculadas = Mentorias.objects
    simulados_realizados = RespostasSimulados.objects.filter(
        email_aluno=aluno.email_aluno,
        simulado__in=Simulados.objects.filter(mentor=request.user)).count()
    if request.method == 'POST':
        if request.POST.get('situacao_matricula'):
            if aluno.situacao_matricula == 'ok':
                aluno.situacao_matricula = 'ex'
            else:
                aluno.situacao_matricula = 'ok'
            aluno.save()
            return JsonResponse({'situacao': aluno.get_situacao_matricula_display()})
        if request.POST.get('nome_aluno'):
            aluno.nome_aluno = request.POST.get('nome_aluno')
            aluno.save()
            return JsonResponse({'data': True})
        if request.POST.get('email_aluno'):
            aluno.email_aluno = request.POST.get('email_aluno')
            aluno.save()
            return JsonResponse({'data': True})
        if request.POST.get('telefone_aluno'):
            aluno.telefone_aluno = request.POST.get('telefone_aluno')
            aluno.save()
            return JsonResponse({'data': True})

        if request.POST.get('aluno-remover'):
            Alunos.objects.get(id=int(request.POST.get('aluno-remover'))).delete()
            return JsonResponse({'data': True})

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
    ctx = {
        'aluno': aluno,
        'simulados_realizados': simulados_realizados
    }
    return render(request, template_name, ctx)
