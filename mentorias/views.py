from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.utils.translation import gettext as _
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, BadHeaderError, EmailMessage, get_connection
from django.utils import timezone
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth import logout
from django.utils.timezone import make_aware
from django.db.models import Case, When # Ordenar queryset segundo uma lista
from dateutil import relativedelta
from datetime import timedelta

import zoneinfo
from chartjs.views.lines import BaseLineChartView
import copy
from statistics import mean
import json
import os
from datetime import date, datetime
import threading

from utils.resources import confere_pagagmentos, POLICY_LANGUAGES
from .models import (
    Mentoria, Materias, Alunos, LoginAlunos, Simulados, LinksExternos, AplicacaoSimulado, PreMatrículaAlunos,
    ArquivosMentoria, MatriculaAlunoMentoria, RegistrosMentor, TermosAceitosAluno, get_random_string
)
from assinaturas.models import TermosDeUso
from .forms import (
    CriarMentoriaForm, CadastrarAlunoForm, CadastrarSimuladoForm, CadastrarMateriaForm, MatriculaAlunoMentoriaForm,
    ConfirmMentorPasswordForm, LinksExternosForm, SummernoteFormSimple, LoginAlunosForm, SenhaAlunoLoginForm
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
    form = CriarMentoriaForm(request.user)
    if request.method == 'POST':
        form = CriarMentoriaForm(request.user, data=request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.mentor = request.user
            instance.save()
            messages.success(request, _('Mentoria criada com sucesso!'))
            return redirect('usuarios:home_mentor')
        else:
            form = CriarMentoriaForm(request.user, data=request.POST)
    return render(request, template_name, {'form': form})


@login_required
def mentoria_detalhe(request, pk):
    mentoria = get_object_or_404(Mentoria, pk=pk)
    form = SummernoteFormSimple(instance=mentoria)
    if request.user != mentoria.mentor:
        return redirect('usuarios:index')
    # alunos_atuais = mentoria.matriculas_mentoria.filter(encerra_em__gte=date.today(), ativa=True)
    alunos_atuais = mentoria.matriculas_mentoria.filter(ativa=True)
    for aluno in alunos_atuais:
        if aluno.encerra_em < date.today():
            aluno.ativa = False
            aluno.save()
    if request.method == 'POST':
        if request.POST.get('resumo_mentoria'):
            form = SummernoteFormSimple(request.POST, instance=mentoria)             
            if form.is_valid():
                mentoria = form.save()
            else:
                messages.error(request, _('Erro ao salvar alteração no conteúdo da apresentação! Tente novamente mais tarde!'))
        if request.POST.get('link-remover'):
            link_remover = LinksExternos.objects.get(pk=int(request.POST.get('link-remover')))
            mentoria.links_externos.remove(link_remover)
            mentoria.save()
            link_remover.delete()
            return JsonResponse({'data': True})
        if request.POST.get('matricula-remover'):
            matricula_a_remover = alunos_atuais.filter(pk=int(request.POST.get('matricula-remover')))[0]
            # RegistrosMentor.objects.create(matricula=matricula_a_remover, atividade='apag')
            matricula_a_remover.delete()
            return JsonResponse({'data': True})
        if request.FILES.get('arquivo', None):
            titulo_existe = ArquivosMentoria.objects.filter(mentoria=mentoria, titulo_arquivo=request.POST.get('tagId2')).exists()
            if titulo_existe:
                msg = _('Já existe arquivo com este mesmo título!')
                return JsonResponse({'success': False, 'tag': 'errorSpan', 'msg': msg})
            ArquivosMentoria.objects.create(
                mentoria=mentoria,
                mentor=request.user,
                arquivo_mentoria=request.FILES.get('arquivo', None),
                titulo_arquivo=request.POST.get('tagId2')
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
            titulo_novo = request.POST.get('titulo-novo')
            mentoria_existe = Mentoria.objects.filter(mentor=request.user, titulo__iexact=titulo_novo)
            if mentoria_existe:                
                return JsonResponse({'data': False, 'msg': _(f"Mentoria o título { titulo_novo } já existe!")})
            mentoria.titulo = titulo_novo
            mentoria.save()
            return JsonResponse({'data': True})
        if request.POST.get('inteiro-novo'):
            mentoria.periodo_duracao = request.POST.get('inteiro-novo')
            mentoria.save()
            return JsonResponse({'data': True})        
        if request.POST.get('dataEncerramento'):
            data = request.POST.get('dataEncerramento').split('-')
            data_resposta = data[2]+'/' + data[1]+'/'+data[0]            
            # data = datetime(int(data[0]), int(data[1]), int(data[2]), hour=datetime.now().hour, minute=datetime.now().minute, tzinfo=zoneinfo.ZoneInfo(settings.TIME_ZONE))
            data = date(int(data[0]), int(data[1]), int(data[2]))
            if date.today() > data:              
                return JsonResponse({'data': data_resposta, "alterada": False, "msg": _("Data de encerramento não pode ser anterior ao dia de hoje.")})
            mentoria.encerra_em = data
            mentoria.save()
            return JsonResponse({'data': data_resposta, 'alterada': True, "msg": _("Data de encerramento alterada.")})        
    ex_alunos = mentoria.matriculas_mentoria.filter(ativa=False)
    # matriculas nesta mentoria
    # matriculas = mentoria.matriculas_mentoria.only('id').all()
    # Quantos alunos distintos reponderam simulado nesta mentoria
    # aplicacoes = AplicacaoSimulado.objects.filter(matricula__in=matriculas).exclude(data_resposta__isnull=True).values('aluno_id').distinct('aluno_id').order_by('aluno_id')    
    ctx = {
        'mentoria': mentoria,
        'alunos_atuais': alunos_atuais,
        'ex_alunos': ex_alunos,
        'form': form
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
    form = CadastrarAlunoForm(request.user)
    if request.method == 'POST':
        form = CadastrarAlunoForm(request.user, data=request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            email = form.cleaned_data['email_aluno']
            if Alunos.objects.filter(mentor=request.user, email_aluno=email).exists():
                messages.error(request, _('Já existe aluno cadastrado com este email.'))
                form = CadastrarAlunoForm(request.user, data=request.POST)
                return render(request, 'mentorias/alunos/cadastrar_aluno.html', {'form': form})               
            instance.mentor = request.user
            instance.save()
            if request.POST.get('mentoria'):
                if int(request.POST.get('mentoria')) > 0:
                    mentoria = Mentoria.objects.get(pk=int(request.POST.get('mentoria')))
                    MatriculaAlunoMentoria.objects.create(aluno=instance, mentoria=mentoria)
                    messages.info(request, _('Matrícula efetuada1'))
            messages.success(request, _('Aluno criado com sucesso!'))
            return redirect('usuarios:home_mentor')
        else:
            form = CadastrarAlunoForm(request.user, data=request.POST)
    
    mentorias = Mentoria.objects.filter(mentor=request.user, ativa=True)
    ctx = {
        'form': form,
        'mentorias': mentorias
        }
    return render(request, 'mentorias/alunos/cadastrar_aluno.html', ctx)


def cadastrar_pre_matricular(request, pk):
    form = CadastrarAlunoForm(request.user)
    if request.method == 'POST':
        mentoria = get_object_or_404(Mentoria, pk=pk)
        form = CadastrarAlunoForm(request.user, data=request.POST)
        if form.is_valid():
            email_enviado = form.cleaned_data['email_aluno']
            if PreMatrículaAlunos.objects.filter(mentoria_pre_matriculada=mentoria, email_aluno=email_enviado).exists():
                messages.error(request, _('Solicitação enviada!'))
                return render(request, 'mentorias/alunos/cadastrar_aluno.html', {'form': form})  
            else:
                PreMatrículaAlunos.objects.create(
                    mentoria_pre_matriculada=mentoria,
                    nome_aluno=form.cleaned_data['nome_aluno'],
                    email_aluno=form.cleaned_data['email_aluno'],
                    telefone_aluno=form.cleaned_data['telefone_aluno']
                )
            # if aluno_existente:
            #     messages.error(request, _('Matrícula efetuada!'))                
            #     return render(request, 'mentorias/alunos/cadastrar_aluno.html', {'form': form})            
            # else:
            #     instance.save()           
            #     messages.error(request, _('Matrícula efetuada!')) 

            # MatriculaAlunoMentoria.objects.create(aluno=instance, mentoria=mentoria)
            return redirect('usuarios:index')
        else:
            form = CadastrarAlunoForm(request.user, data=request.POST)
    
    mentoria = get_object_or_404(Mentoria, pk=pk)
    ctx = {
        'form': form,
        'mentoria': mentoria
        }
    return render(request, 'mentorias/cadastrar_pre_matricular.html', ctx)


@login_required
def cadastrar_simulado(request):
    template_name = 'mentorias/simulados/cadastrar_simulado.html'
    form = CadastrarSimuladoForm(request.user)
    if request.method == 'POST':
        form = CadastrarSimuladoForm(request.user, data=request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.mentor = request.user
            instance.save()
            messages.success(request, _('Simulado criado com sucesso!'))
            return redirect('usuarios:home_mentor')
        else:
            form = CadastrarSimuladoForm(request.user, data=request.POST)
    return render(request, template_name, {'form': form})


@login_required
def aluno_matricular(request, pk):
    mentoria = Mentoria.objects.get(pk=pk)
    if request.user != mentoria.mentor:
        return redirect('usuarios:index')
    template_name = 'mentorias/aluno_matricular.html'
    form = MatriculaAlunoMentoriaForm(mentoria)
    ctx = {
        'form': form,
        'mentoria': mentoria
    }
    if request.method == 'POST':
        form = MatriculaAlunoMentoriaForm(mentoria, data=request.POST)
        if form.is_valid():
            mail_trheading = threading.Thread(target=email_theading_matricula, args=(form, mentoria, request))
            mail_trheading.start()
            messages.success(request, _("Matrícula efetivada! Um email será enviado ao aluno com as instruções de acesso ao portal!"))
            return redirect('mentorias:mentoria_detalhe', pk=pk)
    return render(request, template_name, ctx)


@login_required
def cadastrar_materia(request):
    template_name = 'mentorias/materias/cadastrar_materia.html'
    form = CadastrarMateriaForm(mentor=request.user)
    if request.method == 'POST':
        form = CadastrarMateriaForm(mentor=request.user, data=request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.mentor = request.user
            instance.save()
            messages.success(request, _('Matéria criada com sucesso!'))
            return redirect('mentorias:materias')
        else:
            # messages.error(request, _('Erro ao criar matéria!'))
            form = CadastrarMateriaForm(mentor=request.user, data=request.POST)
    return render(request, template_name, {'form': form})


@login_required
def aluno_detalhe(request, pk):
    aluno = get_object_or_404(Alunos, pk=pk)
    if request.user != aluno.mentor:
        return redirect('usuarios:index')
    template_name = 'mentorias/alunos/aluno_detalhe.html'
    simulados_realizados = AplicacaoSimulado.objects.filter(
        aluno=aluno)
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
            mentoria = Mentoria.objects.filter(pk=int(request.POST.get('pk'))).first()
            if not mentoria:                
                return JsonResponse({'data': False, 'message': 'Mentoria não encontrada!'})
            titulo_existe = ArquivosMentoria.objects.filter(mentoria=mentoria, titulo_arquivo=request.POST.get('tagId2')).exists()
            if titulo_existe:
                msg = _('Já existe arquivo com este mesmo título!')
                return JsonResponse({'data': True, 'success': False, 'tag': 'tituloArquivo', 'msg': msg})
            ArquivosMentoria.objects.create(
                mentoria=mentoria,
                mentor=request.user,
                mentor_nome=request.user.first_name,
                titulo_arquivo=request.POST.get('tagId2'),
                arquivo_mentoria=request.FILES.get('arquivo', None),
                aluno=aluno
            )
            messages.success(request, _('Novo arquivo salvo com sucesso!'))
            return JsonResponse({'data': True, 'success': True})
        elif request.POST.get('arquivo-remover'):
            arquivo = ArquivosMentoria.objects.get(id=int(request.POST.get('arquivo-remover')))
            os.remove(arquivo.arquivo_mentoria.path)
            arquivo.delete()
            return JsonResponse({'data': True})
        else:
            return JsonResponse({'data': True})
    matriculas = MatriculaAlunoMentoria.objects.filter(aluno=aluno)
    ctx = {
        'aluno': aluno,
        'simulados_realizados': simulados_realizados,
        'matriculas': matriculas
    }
    return render(request, template_name, ctx)


@login_required
def editar_aluno(request, pk):
    aluno = get_object_or_404(Alunos, pk=pk)
    if request.user != aluno.mentor:
        return redirect('usuarios:index')
    form = CadastrarAlunoForm(request.user, instance=aluno)
    if request.method == 'POST':
        email_atual = copy.deepcopy(aluno.email_aluno)
        form = CadastrarAlunoForm(request.user, data=request.POST, instance=aluno)
        if form.is_valid():
            email = form.cleaned_data['email_aluno']
            if email_atual != email:
                if Alunos.objects.filter(mentor=request.user, email_aluno=email).exists():
                    messages.error(request, _('Este email já existe.'))
                    form = CadastrarAlunoForm(request.user, data=request.POST, instance=aluno)
                    return render(request, 'mentorias/alunos/cadastrar_aluno.html', {'form': form})
            form.save(commit=True)
            messages.success(request, _('Alterado com sucesso!'))
            return redirect('mentorias:aluno_detalhe', pk=pk)
        else:
            messages.error(request, _('Erro ao alterar dados! Tente novamente mais tarde.'))
            form = CadastrarAlunoForm(request.user, data=request.POST)
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
            if simulado.pdf_prova:
                if os.path.exists(simulado.pdf_prova.arquivo_mentoria.path):
                    os.remove(simulado.pdf_prova.arquivo_mentoria.path)
                    simulado.pdf_prova.delete()
            created = ArquivosMentoria.objects.create(
                mentor=request.user,
                arquivo_mentoria=request.FILES.get('arquivo', None)
            )
            if created:
                simulado.pdf_prova = created
                simulado.save() 
                return JsonResponse({'success': True, 'data': str(simulado.pdf_prova.__str__()), 'link': str(simulado.pdf_prova.arquivo_mentoria.url)})
            else:
                return JsonResponse({'success': False})
        if request.POST.get('titulo-novo'):
            titulo_novo = request.POST.get('titulo-novo')
            simulado_existe = Simulados.objects.filter(mentor=request.user, titulo__iexact=titulo_novo)
            if simulado_existe:                
                return JsonResponse({"data": False, "msg": _(f"Simulado com o título {titulo_novo} já existe!")})
            simulado.titulo = titulo_novo
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
        if request.POST.get('materia-remover'):
            Materias.objects.get(id=int(request.POST.get('materia-remover'))).delete()
            return JsonResponse({'redirect_to': reverse('mentorias:materias')})
        if request.POST.get('titulo-novo'):
            titulo_novo = request.POST.get('titulo-novo')
            materia_existe = Materias.objects.filter(mentor=request.user, titulo__iexact=titulo_novo)
            if materia_existe:
                return JsonResponse({"data": False, "msg": _(f"Matéria com o título { titulo_novo } já existe!")})
            materia.titulo = titulo_novo
            materia.save()
            return JsonResponse({'data': True})
        if request.POST.get('inteiro-novo'):
            materia.peso = request.POST.get('inteiro-novo')
            materia.save()
            return JsonResponse({'data': True})
        if request.POST.get('emUso'):
            if materia.em_uso:
                materia.em_uso = False
            else:
                materia.em_uso = True
            materia.save()
            return JsonResponse({'data': True})
    simulados = Simulados.objects.filter(gabarito__resumo__icontains=materia.titulo)
    ctx = {
        'materia': materia,
        'simulados': simulados       
    }
    return render(request, template_name, ctx)


@login_required
def cadastrar_gabarito(request, pk):
    simulado = Simulados.objects.get(pk=pk)
    if request.user != simulado.mentor:
        return redirect('usuarios:index')
    template_name = 'mentorias/simulados/cadastrar_gabarito.html'
    comparativo = {}
    if simulado.gabarito:
        # ordenar queryset segundo uma lista
        preenchimento = simulado.gabarito['preenchimento']
        lista_materias = []
        for chave, valor in preenchimento.items():
            for k, v in valor.items():
                comparativo[k] = v
                lista_materias.append(k)
        preferred = Case(
             *(When(titulo=materia, then=pos) for pos, materia in enumerate(lista_materias, start=1))
        )
        materias = Materias.objects.filter(mentor=request.user, em_uso=True).order_by(preferred)    
    else:
        materias = Materias.objects.filter(mentor=request.user, em_uso=True)
    ctx = {
        'simulado': simulado,
        'materias': materias,
        'comparativo': comparativo
    }
    if request.method == 'POST':
        if request.POST.get('gabaritoJson'):       
            simulado.gabarito = json.loads(request.POST.get('gabaritoJson'))
            simulado.save()
            for titulo in simulado.gabarito['resumo']:
                materia = materias.filter(mentor=request.user, titulo=titulo).first()
                materia.simulados.add(simulado)
                materia.save()
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
        data_aplicacao = make_aware(timezone.datetime.strptime(data_aplicacao, "%Y-%m-%dT%H:%M"))
        mailing_thread = threading.Thread(
            target=multiemail_threading,
            args=(aplicacao, pk, mentoria,simulado, request, data_aplicacao)
        )
        mailing_thread.start()
    template_name = 'mentorias/simulados/aplicar_simulado.html'
    matriculas = mentoria.matriculas_mentoria.filter(encerra_em__gte=date.today())
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
    simulados = Simulados.objects.filter(mentor=mentoria.mentor, gabarito__isnull=False).exclude(pdf_prova=None)
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
    alternativas = retorna_estatistica_alternativa(aplicacao.simulado)

    # if timezone.make_naive(aplicacao.aplicacao_agendada) > timezone.now():
    if aplicacao.aplicacao_agendada > timezone.now():
        messages.info(request, 'Esta aplicação está agendada para o dia {}, às {}H.'.format(
            aplicacao.aplicacao_agendada.strftime("%m/%d/%Y"), aplicacao.aplicacao_agendada.strftime("%H:%M")))
        return redirect('usuarios:index')
    if request.method == 'POST':
        gabarito = aplicacao.simulado.gabarito
        acertos = 0
        quantidade = aplicacao.simulado.gabarito['total']['questoes']
        total_pontos = aplicacao.simulado.gabarito['total']['pontos']
        if request.session.has_key('aluno_entrou'):
            if request.POST.get('respostas'):
                dicionario_base = {}
                dicionario_base['resumo'] = {
                    'acertos': 0, 'erros': 0, 'anuladas': 0,
                    'quantidade': quantidade,
                    'percentual': 0
                }
                dicionario_base['questoes'] = {}
                dicionario_base['analitico'] = {'materias': {}, 'total': {}}
                dicionario_base['analitico']['total'] = {
                    'pontos_atingidos': 0,
                    'total_pontos': total_pontos,
                    'percentual_pontos': 0.00
                }
                respostas_enviadas = json.loads(request.POST.get('respostas'))
                for resposta in respostas_enviadas:
                    dicionario_base['questoes'][resposta] = {
                        'gabarito': gabarito['questoes'][resposta]['resposta'],
                        'resposta': respostas_enviadas[resposta]
                    }
                    if respostas_enviadas[resposta] == gabarito['questoes'][resposta]['resposta']:
                        acertos += 1
                        dicionario_base['resumo']['acertos'] += 1
                        dicionario_base['analitico']['total']['pontos_atingidos'] += int(
                            gabarito['questoes'][resposta]['peso'])
                        if gabarito['questoes'][resposta]['materia'] in dicionario_base['analitico']['materias']:
                            dicionario_base['analitico']['materias'][
                                gabarito['questoes'][resposta]['materia']]['quantidade'] += 1
                            dicionario_base['analitico']['materias'][
                                gabarito['questoes'][resposta]['materia']]['acertos'] += 1
                            dicionario_base['analitico']['materias'][gabarito['questoes'][resposta][
                                'materia']]['pontos'] += int(gabarito['questoes'][resposta]['peso'])
                            dicionario_base['analitico']['materias'][
                                gabarito['questoes'][resposta]['materia']]['percentual_acertos'] = round(
                                (dicionario_base['analitico']['materias']
                                [gabarito['questoes'][resposta]['materia']]['acertos'] /
                                dicionario_base['analitico']['materias']
                                [gabarito['questoes'][resposta]['materia']]['quantidade']) * 100,
                                2) if dicionario_base['analitico']['materias'][gabarito['questoes'][resposta]['materia']]['acertos'] > 0 else 0.00
                        else:
                            dicionario_base['analitico']['materias'][
                                gabarito['questoes'][resposta]['materia']] = {
                                'quantidade': 1,
                                'peso': int(gabarito['questoes'][resposta]['peso']),
                                'acertos': 1,
                                'percentual_acertos':100.00,
                                'pontos': int(gabarito['questoes'][resposta]['peso'])
                            }
                    elif gabarito['questoes'][resposta]['resposta'] == 'X':
                        dicionario_base['resumo']['anuladas'] += 1
                    else:
                        if gabarito['questoes'][resposta]['materia'] in dicionario_base['analitico']['materias']:
                            dicionario_base['analitico']['materias'][
                                gabarito['questoes'][resposta]['materia']]['quantidade'] += 1                                                  
                            dicionario_base['analitico']['materias'][
                                gabarito['questoes'][resposta]['materia']]['percentual_acertos'] = round(
                                (dicionario_base['analitico']['materias']
                                 [gabarito['questoes'][resposta]['materia']]['acertos'] /
                                 dicionario_base['analitico']['materias']
                                 [gabarito['questoes'][resposta]['materia']]['quantidade']) * 100,
                                2) if dicionario_base['analitico']['materias'][
                                gabarito['questoes'][resposta]['materia']]['acertos'] > 0 else 0
                        else:
                            dicionario_base['analitico']['materias'][
                                gabarito['questoes'][resposta]['materia']] = {
                                    'quantidade': 1,
                                    'peso': int(gabarito['questoes'][resposta]['peso']),
                                    'acertos': 0,
                                    'percentual_acertos': 0.00,
                                    'pontos': 0
                                }
                        dicionario_base['resumo']['erros'] += 1

                dicionario_base['resumo']['percentual'] = round(
                    (acertos / quantidade) * 100, 2) if acertos > 0 else 0
                dicionario_base['analitico']['total']['percentual_pontos'] = round(
                    (dicionario_base['analitico']['total']['pontos_atingidos'] / total_pontos) * 100, 2) if dicionario_base['analitico']['total']['pontos_atingidos'] > 0 else 0              
                aplicacao.resposta_alunos = dicionario_base
                aplicacao.data_resposta = date.today()
                aplicacao.save()
                RegistrosMentor.objects.create(
                    log_mentor_id = aplicacao.matricula.mentoria.mentor.id,
                    log_mentor_email = aplicacao.matricula.mentoria.mentor.email,
                    log_mentor_nome = f"{aplicacao.matricula.mentoria.mentor.first_name} {aplicacao.matricula.mentoria.mentor.last_name}",
                    log_mentoria_id = aplicacao.matricula.mentoria.id,
                    log_mentoria_titulo = aplicacao.matricula.mentoria.titulo,
                    log_matricula_id = aplicacao.matricula.id,
                    log_matricula_email = aplicacao.matricula.aluno.email_aluno,
                    log_matricula_encerra_em = aplicacao.matricula.encerra_em,
                    log_matricula_ativa = aplicacao.matricula.ativa,
                    data_resposta = aplicacao.data_resposta,
                    log_simulado = aplicacao.simulado.id,
                    atividade='resp'
                )
                return JsonResponse({'data': True})
    session_ok = False
    if request.session.has_key('aluno_entrou'):
        if request.session['aluno_entrou'] == aplicacao.aluno.email_aluno:
            session_ok = True
        else:
            del request.session['aluno_entrou']
    else:
        return redirect('mentorias:login_alunos')
    ctx = {
        "aplicacao": aplicacao,
        "respondido": True if aplicacao.resposta_alunos else False,
        "session_ok": session_ok,
        "alternativas": alternativas
    }
    template_name = 'mentorias/simulados/aluno_anonimo_aplicacao.html'
    return render(request, template_name, ctx)


@login_required
def matricula_detalhe(request, pk):
    template_name = 'mentorias/matriculas/matricula_detalhe.html'
    matricula = get_object_or_404(MatriculaAlunoMentoria, pk=pk)
    mentoria = Mentoria.objects.get(matriculas_mentoria__id=pk)
    # no_prazo = True if matricula.encerra_em.astimezone() > datetime.now(tz=zoneinfo.ZoneInfo(settings.TIME_ZONE)) else False 
    no_prazo = True if matricula.encerra_em > date.today() else False 
    if matricula.ativa and not no_prazo:
        matricula.ativa = False
        matricula.data_desativada = date.today()
        matricula.save()
    if request.method == 'POST':
        if request.POST.get('aplicacao-remover'):
            AplicacaoSimulado.objects.get(id=int(request.POST.get('aplicacao-remover'))).delete()
            return JsonResponse({'data': True})
        elif request.POST.get('dataEncerramento'):
            data = request.POST.get('dataEncerramento').split('-')
            data_resposta = data[2]+'/' + data[1]+'/'+data[0]            
            # data = datetime(int(data[0]), int(data[1]), int(data[2]), hour=datetime.now().hour, minute=datetime.now().minute, tzinfo=zoneinfo.ZoneInfo(settings.TIME_ZONE))
            data = date(int(data[0]), int(data[1]), int(data[2]))
            if matricula.encerra_em > data:                
                return JsonResponse({'data': data_resposta, "alterada": False, "msg": _("Data de encerramento não pode ser anterior à data já cadastrada.")})
            matricula.encerra_em = data
            matricula.save()
            return JsonResponse({'data': data_resposta, 'alterada': True, "msg": _("Data de encerramento alterada.")})
        elif request.POST.get("situacaoMatricula"):
            situacao = "Ativa"
            if matricula.ativa:
                matricula.data_desativada = date.today()
                matricula.ativa = False
                situacao = "Inativa"
            else:
                if not no_prazo:
                    return JsonResponse({'situacao': 'Impedida', 'msg': 'Antes de ativar esta matrícula, insira uma data futura de encerramento!' })
                if matricula.data_reativada:
                    dias_corridos = date.today() - matricula.data_desativada
                    if dias_corridos < timedelta(days=25):
                        matricula.data_reativada = date.today()
                        matricula.ativa = True
                    else:
                        return JsonResponse({'situacao': 'Impedida', 'msg': 'Prazo para reativação encerrado(mais de 25 dias corridos, da desativação).' })
                else:
                    matricula.data_reativada = date.today()
                    matricula.ativa = True
            matricula.save()
            return JsonResponse({'situacao': situacao })            
        elif request.POST.get('gerarSenha'):
            result_str = get_random_string()
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
            try:
                send_mail(
                    f"Alteração de senha na mentoria {mentoria}",
                    mensagem_email,
                    f'{ mentoria.mentor } <{settings.NOREPLY_EMAIL}>',
                    [matricula.aluno.email_aluno]
                )
            except BadHeaderError:
                messages.warning(request, _('Erro ao enviar emails.'))
            return JsonResponse({'data': matricula.senha_do_aluno})         
        elif request.FILES.get('arquivo', None):
            if not mentoria:                
                return JsonResponse({'data': False, 'message': 'Mentoria não encontrada!'})
            titulo_existe = ArquivosMentoria.objects.filter(matricula=matricula, titulo_arquivo=request.POST.get('tagId2')).exists()
            if len(request.POST.get('tagId2')) > 100:                   
                msg = _('Título do arquivo deve conter até 100 caractéres.')
                return JsonResponse({'data': True, 'success': False, 'tag': 'errorSpan', 'msg': msg})
            if titulo_existe:
                msg = _('Já existe arquivo com este mesmo título!')
                return JsonResponse({'data': True, 'success': False, 'tag': 'errorSpan', 'msg': msg})
            ArquivosMentoria.objects.create(
                mentoria=mentoria,
                mentor=request.user,
                mentor_nome=request.user.first_name,
                titulo_arquivo=request.POST.get('tagId2'),
                arquivo_mentoria=request.FILES.get('arquivo', None),
                matricula=matricula
            )
            messages.success(request, _('Novo arquivo salvo com sucesso!'))
            return JsonResponse({'data': True, 'success': True})
        elif request.POST.get('arquivo-remover'):
            arquivo = ArquivosMentoria.objects.get(id=int(request.POST.get('arquivo-remover')))
            os.remove(arquivo.arquivo_mentoria.path)
            arquivo.delete()
            return JsonResponse({'data': True})        
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
def desempenho_matricula(request, pk):
    template_name = 'mentorias/matriculas/desempenho_matricula.html'
    matricula = get_object_or_404(MatriculaAlunoMentoria, pk=pk)
    mentoria = Mentoria.objects.get(matriculas_mentoria__id=pk)
    # no_prazo = True if matricula.encerra_em.astimezone() > datetime.now(tz=zoneinfo.ZoneInfo(settings.TIME_ZONE)) else False 
    no_prazo = True if matricula.encerra_em > date.today() else False 
    if matricula.ativa and not no_prazo:
        matricula.data_desativada = date.today()
        matricula.ativa = False
        matricula.save()
    if request.method == 'POST':
        if request.POST.get('aplicacao-remover'):
            AplicacaoSimulado.objects.get(id=int(request.POST.get('aplicacao-remover'))).delete()
            return JsonResponse({'data': True})
        elif request.POST.get('gerarSenha'):
            result_str = get_random_string()
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
            try:
                send_mail(
                    f"Alteração de senha na mentoria {mentoria}",
                    mensagem_email,
                    f'{ mentoria.mentor } <{settings.NOREPLY_EMAIL}>',
                    [matricula.aluno.email_aluno]
                )
            except BadHeaderError:
                messages.warning(request, _('Erro ao enviar emails.'))
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
    mentoria = Mentoria.objects.filter(simulados_mentoria__id=pk).first()
    alternativas = retorna_estatistica_alternativa(aplicacao.simulado)
    if request.user != mentoria.mentor:
        return redirect('usuarios:index')
    template_name = 'mentorias/matriculas/resultado_detalhe.html'
    ctx = {
        'aplicacao': aplicacao,
        "alternativas": alternativas
    }
    return render(request, template_name, ctx)


@login_required
def aplicacao_individual(request, pk):
    matricula = MatriculaAlunoMentoria.objects.get(pk=pk)    
    if request.user != matricula.aluno.mentor:
        messages.info(request, 'Página não encontrada!')
        return redirect('usuarios:index')
    mentoria = matricula.mentoria    
    # no_prazo = True if matricula.encerra_em.astimezone() > datetime.now(tz=zoneinfo.ZoneInfo(settings.TIME_ZONE)) else False 
    no_prazo = True if matricula.encerra_em > date.today() else False 
    if matricula.ativa and not no_prazo:
        matricula.ativa = False
        matricula.save()
        messages.error(request, _("Esta matrícula está encerrada!"))
        return redirect('usuarios:index')
    if request.method == 'POST':
        aplicacao = json.loads(request.POST.get('aplicacao'))
        simulado = Simulados.objects.get(pk=aplicacao['simulado'])
        data_aplicacao = aplicacao['aplicacao_agendada']
        data_aplicacao = make_aware(timezone.datetime.strptime(data_aplicacao, "%Y-%m-%dT%H:%M"))
        if not AplicacaoSimulado.objects.filter(aluno=matricula.aluno, simulado=simulado, matricula=matricula):
            if AplicacaoSimulado.objects.filter(aluno=matricula.aluno, simulado=simulado):
                antigo = AplicacaoSimulado.objects.filter(aluno=matricula.aluno, simulado=simulado)[0]
                antigo.pk = None
                antigo.matricula = matricula
                antigo.save()
                mentoria.simulados_mentoria.add(antigo)
                messages.info(request, _('Aluno já realizou este simulado em outra situação! Se aluno já respondeu o simulado, tais respostas serão aproveitadas.'))
                return JsonResponse({'redirect_to': reverse('mentorias:matricula_detalhe', kwargs={'pk': pk})})
            if not confere_pagagmentos(request):
                # CLiente inadimplente não consegue aplicar simulado.
                messages.info(request, "Não econtrado o pagamento da fatura!")
                return JsonResponse({'redirect_to': reverse('assinaturas:faturas_mentor')})
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
            }
            mensagem_email = render_to_string(email_template_name, c)
            mailing_thread = threading.Thread(
                target=email_theading,
                args=(mentoria, matricula, mensagem_email, request)
            )
            mailing_thread.start()
            messages.success(request, _(f'Aplicação de simulado para o aluno foi salva.'))
        else:
            messages.warning(request, _('Este simulado já foi aplicado a este aluno, nesta matrícula.'))
        return JsonResponse({'redirect_to': reverse('mentorias:matricula_detalhe', kwargs={'pk': pk})})
    template_name = 'mentorias/simulados/aplicacao_individual.html'

    simulados = Simulados.objects.filter(mentor=mentoria.mentor, gabarito__isnull=False).exclude(pdf_prova=None)
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
    login_aluno = get_object_or_404(LoginAlunos, email_aluno_login=matricula.aluno.email_aluno)
    mentoria = Mentoria.objects.get(matriculas_mentoria__id=pk)
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
        'login_aluno': login_aluno,
        "session_ok": session_ok
    }
    if request.method == 'POST':
        if request.POST.get('email_aluno_login'):
            email_enviado = request.POST.get('email_aluno_login')
        else:
            return render(request, 'mentorias/alunos/login_alunos.html', ctx)
        if request.POST.get('senha_aluno_login'):
            senha_enviada = request.POST.get('senha_aluno_login')
        else:
            return render(request, 'mentorias/alunos/login_alunos.html', ctx)            
        login_aluno_existe = LoginAlunos.objects.filter(email_aluno_login=email_enviado)
        if login_aluno_existe:
            termo_de_uso = TermosAceitosAluno.objects.filter(login_aluno=login_aluno_existe.first())
            if not termo_de_uso:
                return redirect('mentorias:apresentacao_termo_alunos', pk=login_aluno_existe.first().pk)
            aluno_encontrado = login_aluno_existe.first()
            if aluno_encontrado.senha_aluno_login == senha_enviada:
                request.session['aluno_entrou'] = email_enviado
                request.session['session_ok'] = True
                return redirect('mentorias:aluno_matriculas', pk=aluno_encontrado.pk)    
            else:
                messages.error(request, _('Email ou senha inválido.'))
                return redirect('mentorias:login_alunos') 
    return render(request, template_name, ctx)

def retorna_estatistica_alternativa(simulado):
    aplicacoes = AplicacaoSimulado.objects.filter(simulado=simulado).order_by('data_resposta')    
    alternativas = {}
    for apl in aplicacoes:
        if apl.resposta_alunos:
            estatisticas = apl.resposta_alunos
        else:
            aplicacoes = aplicacoes.exclude(id=apl.id)
            continue
        for index in estatisticas["questoes"]:            
            if simulado.questao_tipo == 2:
                alternativas[str(index)] = {
                    "A":0.00, "B":0.00, "C":0.00, "D":0.00, "E": 0.00
                }
            else:
                alternativas[str(index)] = {
                    "A":0.00, "B":0.00, "C":0.00, "D":0.00
                }             
    for apl in aplicacoes:
        if apl.resposta_alunos:
            estatisticas = apl.resposta_alunos
        else:
            continue                
        for index in alternativas:
            alternativas[str(index)][estatisticas["questoes"][str(index)]['resposta']] += 1
    for index in alternativas:
        if alternativas[str(index)][estatisticas["questoes"][str(index)]['resposta']] > 0:
            if simulado.questao_tipo == 2:
                for letra in 'ABCDE':
                    alternativas[str(index)][letra] = round((
                        alternativas[str(index)][letra] / len(aplicacoes))*100, 2)
    return alternativas


def retorna_estatistica_mentoria(mentoria):
    aplicacoes = AplicacaoSimulado.objects.filter(matricula__in=MatriculaAlunoMentoria.objects.filter(mentoria=mentoria)).order_by('data_resposta')
    labels = []
    dados_lista = []
    dados_resumo = []
    datasets = []      
    media_mensal = {}
    for apl in aplicacoes:
        estatistica = apl.resposta_alunos
        if apl.data_resposta:
            mes_ano = f'Simulado Nº{apl.simulado.id}'
            if not mes_ano in media_mensal:
                media_mensal[mes_ano] = [estatistica["resumo"]["percentual"]]
            else:
                media_mensal[mes_ano].append(estatistica["resumo"]["percentual"])
    for periodo, medias in media_mensal.items():
        labels.append(periodo)
        dados_resumo.append(round(mean(medias), 2))
    
    dados_materias = {}
    for apl in aplicacoes:
        estatistica = apl.resposta_alunos
        if apl.data_resposta:
            mes_ano = f'Simulado Nº{apl.simulado.id}'
        else:
            continue
        for materia in estatistica['analitico']['materias']:
            if not materia in dados_materias:
                dados_materias[materia] = {
                    mes_ano: [estatistica['analitico']['materias'][materia]['percentual_acertos']]
                }
            else:
                if not mes_ano in dados_materias[materia]:
                    dados_materias[materia][mes_ano] = [estatistica['analitico']['materias'][materia]['percentual_acertos']]
                else:
                    dados_materias[materia][mes_ano].append(estatistica['analitico']['materias'][materia]['percentual_acertos'])
    
    for chave, valor in dados_materias.items():
        datasets.append(chave)
        for periodo, medias in valor.items():
            if not periodo in labels:
                labels.append(periodo)
            if len(dados_lista) < datasets.index(chave)+1:
                dados_lista = [*dados_lista, [round(mean(medias), 2)]]
            else:
                dados_lista[datasets.index(chave)].append(round(mean(medias), 2))
    dados_lista = [dados_resumo] + dados_lista
    datasets = ['Média Geral'] +  datasets
    return labels, dados_lista, datasets

def retorna_estatistica_matricula(matricula):     
    aplicacoes = AplicacaoSimulado.objects.filter(matricula=matricula).order_by('data_resposta')
    labels = []
    dados_lista = []
    dados_resumo = []
    datasets = []      
    media_mensal = {}
    for apl in aplicacoes:
        estatistica = apl.resposta_alunos        
        if apl.data_resposta:
            mes_ano = f'Simulado Nº{apl.simulado.id}'    
            if not mes_ano in media_mensal:
                media_mensal[mes_ano] = [estatistica["resumo"]["percentual"]]
            else:
                media_mensal[mes_ano].append(estatistica["resumo"]["percentual"])
    for periodo, medias in media_mensal.items():
        labels.append(periodo)
        dados_resumo.append(round(mean(medias), 2))
    
    dados_materias = {}
    for apl in aplicacoes:
        estatistica = apl.resposta_alunos
        if apl.data_resposta:
            mes_ano = f'Simulado Nº{apl.simulado.id}'    
        else:
            continue
        for materia in estatistica['analitico']['materias']:
            if not materia in dados_materias:
                dados_materias[materia] = {
                    mes_ano: [estatistica['analitico']['materias'][materia]['percentual_acertos']]
                }
            else:
                if not mes_ano in dados_materias[materia]:
                    dados_materias[materia][mes_ano] = [estatistica['analitico']['materias'][materia]['percentual_acertos']]
                else:
                    dados_materias[materia][mes_ano].append(estatistica['analitico']['materias'][materia]['percentual_acertos'])
    
    for chave, valor in dados_materias.items():
        datasets.append(chave)
        for periodo, medias in valor.items():
            if not periodo in labels:
                labels.append(periodo)
            if len(dados_lista) < datasets.index(chave)+1:
                dados_lista = [*dados_lista, [round(mean(medias), 2)]]
            else:
                dados_lista[datasets.index(chave)].append(round(mean(medias), 2))
    dados_lista = [dados_resumo] + dados_lista
    datasets = ['Média Geral'] +  datasets    
    return labels, dados_lista, datasets


def retorna_estatistica_simulado(simulado):
    aplicacoes = AplicacaoSimulado.objects.filter(simulado=simulado).order_by('data_resposta')
    labels = []
    dados_lista = []
    dados_resumo = []
    datasets = []      
    media_mensal = {}
    for apl in aplicacoes:
        estatistica = apl.resposta_alunos
        if apl.data_resposta:
            mes_ano = f'{apl.data_resposta.month}/{apl.data_resposta.year}'    
            if not mes_ano in media_mensal:
                media_mensal[mes_ano] = [estatistica["resumo"]["percentual"]]
            else:
                media_mensal[mes_ano].append(estatistica["resumo"]["percentual"])
    for periodo, medias in media_mensal.items():
        labels.append(periodo)
        dados_resumo.append(round(mean(medias), 2))
    
    dados_materias = {}
    for apl in aplicacoes:
        estatistica = apl.resposta_alunos
        if apl.data_resposta:
            mes_ano = f'{apl.data_resposta.month}/{apl.data_resposta.year}'
        else:
            continue
        for materia in estatistica['analitico']['materias']:
            if not materia in dados_materias:
                dados_materias[materia] = {
                    mes_ano: [estatistica['analitico']['materias'][materia]['percentual_acertos']]
                }
            else:
                if not mes_ano in dados_materias[materia]:
                    dados_materias[materia][mes_ano] = [estatistica['analitico']['materias'][materia]['percentual_acertos']]
                else:
                    dados_materias[materia][mes_ano].append(estatistica['analitico']['materias'][materia]['percentual_acertos'])
    
    for chave, valor in dados_materias.items():
        datasets.append(chave)
        for periodo, medias in valor.items():
            if not periodo in labels:
                labels.append(periodo)
            if len(dados_lista) < datasets.index(chave)+1:
                dados_lista = [*dados_lista, [round(mean(medias), 2)]]
            else:
                dados_lista[datasets.index(chave)].append(round(mean(medias), 2))
    dados_lista = [dados_resumo] + dados_lista
    datasets = ['Média Geral'] +  datasets    
    return labels, dados_lista, datasets

def retorna_estatistica_aplicacao(aplicacao):
    labels = []
    dados_lista = []
    dados_resumo = []
    datasets = []      
    media_mensal = {}
    estatistica = aplicacao.resposta_alunos
    if aplicacao.data_resposta:
        mes_ano = f'{aplicacao.data_resposta.month}/{aplicacao.data_resposta.year}'    
        if not mes_ano in media_mensal:
            media_mensal[mes_ano] = [estatistica["resumo"]["percentual"]]
        else:
            media_mensal[mes_ano].append(estatistica["resumo"]["percentual"])
    for periodo, medias in media_mensal.items():
        labels.append(periodo)
        dados_resumo.append(round(mean(medias), 2))

    dados_materias = {}
    if aplicacao.data_resposta:
        mes_ano = f'{aplicacao.data_resposta.month}/{aplicacao.data_resposta.year}'
    else:
        return 
    for materia in estatistica['analitico']['materias']:
        if not materia in dados_materias:
            dados_materias[materia] = {
                mes_ano: [estatistica['analitico']['materias'][materia]['percentual_acertos']]
            }
        else:
            if not mes_ano in dados_materias[materia]:
                dados_materias[materia][mes_ano] = [estatistica['analitico']['materias'][materia]['percentual_acertos']]
            else:
                dados_materias[materia][mes_ano].append(estatistica['analitico']['materias'][materia]['percentual_acertos'])
    
    for chave, valor in dados_materias.items():
        datasets.append(chave)
        for periodo, medias in valor.items():
            if not periodo in labels:
                labels.append(periodo)
            if len(dados_lista) < datasets.index(chave)+1:
                dados_lista = [*dados_lista, [round(mean(medias), 2)]]
            else:
                dados_lista[datasets.index(chave)].append(round(mean(medias), 2))
    dados_lista = [dados_resumo] + dados_lista
    datasets = ['Média Geral'] +  datasets       
    return labels, dados_lista, datasets


class BaseLineChartViewCustom(BaseLineChartView):
    def get_colors(self):
        return next_color()

class LineChartMentoriaView(BaseLineChartViewCustom):
    def setup(self, *args, **kwargs):
        mentoria = Mentoria.objects.get(pk=kwargs['pk'])
        self.labels, self.dados_lista, self.datasets = retorna_estatistica_mentoria(mentoria)
        super().setup(*args, **kwargs)

    def get_labels(self):
        """Return labels for the x-axis."""
        return self.labels

    def get_providers(self):
        """Return names of datasets."""
        return self.datasets

    def get_data(self):
        return self.dados_lista


class LineChartMatriculaaView(BaseLineChartViewCustom):
    def setup(self, *args, **kwargs):
        matricula = MatriculaAlunoMentoria.objects.get(pk=kwargs['pk'])
        self.labels, self.dados_lista, self.datasets = retorna_estatistica_matricula(matricula)
        super().setup(*args, **kwargs)

    def get_labels(self):
        """Return labels for the x-axis."""
        return self.labels

    def get_providers(self):
        """Return names of datasets."""
        return self.datasets

    def get_data(self):
        return self.dados_lista


class LineChartSimuladoaView(BaseLineChartViewCustom):
    def setup(self, *args, **kwargs):
        simulado = Simulados.objects.get(pk=kwargs['pk'])
        self.labels, self.dados_lista, self.datasets = retorna_estatistica_simulado(simulado)
        super().setup(*args, **kwargs)

    def get_labels(self):
        """Return labels for the x-axis."""
        return self.labels

    def get_providers(self):
        """Return names of datasets."""
        return self.datasets

    def get_data(self):
        return self.dados_lista


class BarChartAplicacaoView(BaseLineChartViewCustom):
    def setup(self, *args, **kwargs):
        aplicacao = AplicacaoSimulado.objects.get(pk=kwargs['pk'])
        self.labels, self.dados_lista, self.datasets = retorna_estatistica_aplicacao(aplicacao)
        super().setup(*args, **kwargs)

    def get_labels(self):
        """Return labels for the x-axis."""
        return self.labels

    def get_providers(self):
        """Return names of datasets."""
        return self.datasets

    def get_data(self):
        return self.dados_lista
    
def multiemail_threading(aplicacao, pk, mentoria, simulado, request, data_aplicacao):
    qtd=0
    try:
        with get_connection(
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            use_tls=settings.EMAIL_USE_TLS
        ) as connection:        
            for id in aplicacao['alunos']:
                aluno = Alunos.objects.get(pk=int(id))
                matricula = mentoria.matriculas_mentoria.filter(aluno=aluno, encerra_em__gte=timezone.now()).first()
                # no_prazo = True if matricula.encerra_em.astimezone() > datetime.now(tz=zoneinfo.ZoneInfo(settings.TIME_ZONE)) else False 
                no_prazo = True if matricula.encerra_em > date.today() else False 
                if AplicacaoSimulado.objects.filter(aluno=aluno, simulado=simulado, matricula=matricula):
                    if matricula.ativa and not no_prazo:
                        matricula.ativa = False
                        matricula.data_desativada = date.today()
                        matricula.save()
                        messages.info(request, _("Simulado não será aplicado em matrícula com prazo encerrado."))
                    continue
                
                if not confere_pagagmentos(request):
                    # CLiente inadimplente não consegue aplicar simulado.
                    messages.info(request, "Não econtrado o pagamento da fatura!")
                    return JsonResponse({'redirect_to': reverse('assinaturas:faturas_mentor')})
                
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
                }
                mensagem_email = render_to_string(email_template_name, c)  
                EmailMessage(f"Novo simulado na mentoria {mentoria}", mensagem_email, f'{mentoria.mentor} <{settings.NOREPLY_EMAIL}>',
                    [aluno.email_aluno], connection=connection).send()
                qtd += 1
            if qtd > 0:
                messages.success(request, _(f'Aplicação de simulado para {qtd} aluno(s) foi salva.'))
            else:
                messages.warning(request, _('Este simulado não é novo para estes aluno.'))
            return JsonResponse({'redirect_to': reverse('mentorias:mentoria_detalhe', kwargs={'pk': pk})})
    except BadHeaderError:
        messages.warning(request, _('Erro ao enviar emails.'))
        return JsonResponse({'redirect_to': reverse('mentorias:mentoria_detalhe', kwargs={'pk': pk})})        

def email_theading(mentoria, matricula, mensagem_email, request):
    try:
        with get_connection(
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            use_tls=settings.EMAIL_USE_TLS
        ) as connection:
            subject = f"Novo simulado na mentoria {mentoria}"
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [matricula.aluno.email_aluno]
            message = mensagem_email
            EmailMessage(subject, message, f'{mentoria.mentor} <{email_from}>',
                recipient_list, connection=connection).send()
    except BadHeaderError:
        messages.warning(request, _('Erro ao enviar emails.'))


def email_theading_matricula(form, mentoria, request):
    try:
        with get_connection(
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            use_tls=settings.EMAIL_USE_TLS
        ) as connection:
            for aluno in form.cleaned_data.get('aluno'):
                nova_matricula = True
                existente = mentoria.matriculas_mentoria.filter(aluno=aluno)
                if existente:
                    for item in existente:
                        if item.encerra_em > datetime.now(tz=zoneinfo.ZoneInfo(settings.TIME_ZONE)):
                            messages.warning(request, _(
                                f"O aluno {item.aluno} já possui matrícula com vencimento vigente, {item.encerra_em}."))
                            nova_matricula = False
                if nova_matricula:

                    matricula = MatriculaAlunoMentoria.objects.create(aluno=aluno, mentoria=mentoria)
                    email_template_name = "mentorias/matriculas/matricula_email.txt"
                    c = {
                        'domain': settings.DOMAIN,
                        'site_name': settings.SITE_NAME,
                        'mentor': mentoria.mentor,
                        'aluno': matricula.aluno.nome_aluno,
                        'protocol': settings.PROTOCOLO,
                    }
                    mensagem_email = render_to_string(email_template_name, c)
                    EmailMessage(f"Nova matricula na mentoria {mentoria}", mensagem_email, f'{mentoria.mentor} <{settings.NOREPLY_EMAIL}>',
                        [matricula.aluno.email_aluno], connection=connection).send()
    except BadHeaderError:
        messages.warning(request, _('Erro ao enviar emails.'))

def tratamento_pre_matricula(request):
    if request.POST.get('action') == 'confirmar':
        pre_matricula = PreMatrículaAlunos.objects.get(pk=int(request.POST.get('pk')))
        email_aluno_existente = Alunos.objects.filter(mentor=pre_matricula.mentoria_pre_matriculada.mentor, email_aluno=pre_matricula.email_aluno)
        if email_aluno_existente:
            MatriculaAlunoMentoria.objects.create(aluno=email_aluno_existente.first(), mentoria=pre_matricula.mentoria_pre_matriculada)
            pre_matricula.delete()
        else:
            login_aluno = get_object_or_404(LoginAlunos, email_aluno_login=pre_matricula.email_aluno)
            aluno = Alunos.objects.create(
                mentor=pre_matricula.mentoria_pre_matriculada.mentor,
                nome_aluno=pre_matricula.nome_aluno, 
                email_aluno=pre_matricula.email_aluno,
                telefone_aluno=pre_matricula.telefone_aluno,
                login_aluno = login_aluno
                )
            MatriculaAlunoMentoria.objects.create(aluno=aluno, mentoria=pre_matricula.mentoria_pre_matriculada)            
            pre_matricula.delete()
        return JsonResponse({})
    else:
        pre_matricula = PreMatrículaAlunos.objects.get(pk=int(request.POST.get('pk')))        
        pre_matricula.delete()
        return JsonResponse({'data': True})


def login_alunos(request):
    ctx ={}
    if request.method == 'POST':
        if request.POST.get('email_aluno_login'):
            email_enviado = request.POST.get('email_aluno_login')
        else:
            return render(request, 'mentorias/alunos/login_alunos.html', ctx)
        if request.POST.get('senha_aluno_login'):
            senha_enviada = request.POST.get('senha_aluno_login')
        else:
            return render(request, 'mentorias/alunos/login_alunos.html', ctx)            
        login_aluno_existe = LoginAlunos.objects.filter(email_aluno_login=email_enviado)
        if login_aluno_existe:
            termo_de_uso = TermosAceitosAluno.objects.filter(login_aluno=login_aluno_existe.first())
            if not termo_de_uso:
                return redirect('mentorias:apresentacao_termo_alunos', pk=login_aluno_existe.first().pk)
            aluno_encontrado = login_aluno_existe.first()
            if aluno_encontrado.senha_aluno_login == senha_enviada:
                request.session['aluno_entrou'] = email_enviado
                request.session['session_ok'] = True
                return redirect('mentorias:aluno_matriculas', pk=aluno_encontrado.pk)
            else:
                messages.error(request, _('Email ou senha inválido.'))
                return render(request, 'mentorias/alunos/login_alunos.html', ctx)
        else:
            return render(request, 'mentorias/alunos/login_alunos.html', ctx)

    return render(request, 'mentorias/alunos/login_alunos.html', ctx)


def apresentacao_termo_alunos(request, pk):
    if request.LANGUAGE_CODE in POLICY_LANGUAGES:
        termo_de_uso = TermosDeUso.objects.filter(    
                language=request.user.policy_lang, begin_date__lt=datetime.now(
                zoneinfo.ZoneInfo(settings.TIME_ZONE)), end_date=None, publico_allvo='aluno').first()        
    else:
        termo_de_uso = TermosDeUso.objects.filter(    
            language='pt', begin_date__lt=datetime.now(
                zoneinfo.ZoneInfo(settings.TIME_ZONE)), end_date=None, publico_allvo='aluno').first()                   
    context={'termo': termo_de_uso}
    if request.method == 'POST':
        login_aluno = get_object_or_404(LoginAlunos, pk=pk)
        TermosAceitosAluno.objects.create(
            login_aluno=login_aluno,
            termo=termo_de_uso            
        )
        request.session['aluno_entrou'] = login_aluno.email_aluno_login
        request.session['session_ok'] = True
        return redirect('mentorias:aluno_matriculas', pk=login_aluno.pk)
    return render(request, 'mentorias/alunos/aceitacao_termo_de_uso.html', context)


def aluno_matriculas(request, pk):
    login_aluno = get_object_or_404(LoginAlunos, pk=pk)    
    matriculas = MatriculaAlunoMentoria.objects.filter(aluno__email_aluno=login_aluno.email_aluno_login)
    if not request.session.has_key('aluno_entrou'):
        return redirect('mentorias:login_alunos')
    # request.session['aluno_entrou'] = login_aluno.email_aluno_login
    # request.session['session_ok'] = True
    # del request.session['aluno_entrou']
    # request.session['session_ok'] = False
    ctx ={
        'login_aluno':login_aluno,
        'matriculas': matriculas
    }
    return render(request, 'mentorias/alunos/aluno_matriculas.html', ctx)


def editar_dados_acesso_aluno_login(request, pk):
    login_aluno = get_object_or_404(LoginAlunos, pk=pk)
    form = LoginAlunosForm(instance=login_aluno)
    ctx={
        'login_aluno':login_aluno,
        'form':form
    }
    if request.method == 'POST':
        form = LoginAlunosForm(instance=login_aluno, data=request.POST)
        login_aluno_alterado = form.save()          
        ctx['form']=form
        return render(request, 'mentorias/alunos/editar_dados_acesso_aluno_login.html', ctx)
    
    return render(request, 'mentorias/alunos/editar_dados_acesso_aluno_login.html', ctx)

def alterar_senha_aluno_login(request, pk):
    login_aluno = get_object_or_404(LoginAlunos, pk=pk)
    form = SenhaAlunoLoginForm()
    ctx={
        'login_aluno': login_aluno,
        'form': form
    }
    if request.method == 'POST':
        form = SenhaAlunoLoginForm(request.POST)
        if form.is_valid():
            if not login_aluno.senha_aluno_login == request.POST.get('senha_atual'):
                messages.error(request, _('Senha não confere!'))
                return render(request, 'mentorias/alunos/alterar_senha_aluno_login.html', ctx)
            login_aluno.senha_aluno_login = request.POST.get('senha_um')
            login_aluno.save()         
        else:
            ctx['form'] = SenhaAlunoLoginForm(request.POST)
            return render(request, 'mentorias/alunos/alterar_senha_aluno_login.html', ctx)
    return render(request, 'mentorias/alunos/alterar_senha_aluno_login.html', ctx)

def aluno_esqueceu_senha(request):
    if request.method == 'POST':
        email_enviado = request.POST.get('email-acesso')
        login_existente = get_object_or_404(LoginAlunos, email_aluno_login=email_enviado)
        if login_existente:
            login_existente.senha_aluno_login = get_random_string()
            login_existente.save()
            thread_task = threading.Thread(target=email_theading_login_aluno, args=(request, login_existente))
            thread_task.start()            
    ctx = {}
    return render(request, 'mentorias/alunos/aluno_esqueceu_senha.html', ctx)

def email_theading_login_aluno(request, login_aluno):
    try:
        with get_connection(
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            use_tls=settings.EMAIL_USE_TLS
        ) as connection:
            subject = f"Nova senha de acesso à matrículas {settings.SITE_NAME}"
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [login_aluno.email_aluno_login]
            email_template_name = "mentorias/alunos/login_aluno_email_template.txt"
            c = {
                'domain': settings.DOMAIN,
                'site_name': settings.SITE_NAME,                   
                'protocol': settings.PROTOCOLO,
                'senha_do_aluno': login_aluno.senha_aluno_login,
                'login_aluno':login_aluno,
            }
            mensagem_email = render_to_string(email_template_name, c)
            EmailMessage(subject, mensagem_email, email_from,
                recipient_list, connection=connection).send()
    except BadHeaderError:
        messages.warning(request, _('Erro ao enviar emails.'))

def alunos_sair_sessao(request):
    if request.method == 'POST':
        del request.session['aluno_entrou']
        request.session['session_ok'] = False
        return redirect('mentorias:login_alunos')
    
# Funções que não são views, não são rotas
# def salva_estatisticas_matricula(matricula, gabarito, respostas_enviadas, dicionario_base):
#     # Atualiza e salva a estatística da matricula, após simulado ser respondido.
#     hoje = timezone.now().strftime('%d/%m/%y')
#     estatistica = matricula.estatisticas
#     if estatistica == None:
#         estatistica = {
#             "itens": {},
#             "resumo": {
#                 'acertos': dicionario_base['resumo']['acertos'],
#                 'quantidade': dicionario_base['resumo']['quantidade'],
#                 'percentual': dicionario_base['resumo']['percentual']
#             }
#         }
#     else:    
#         estatistica['resumo']['acertos'] += dicionario_base['resumo']['acertos']
#         estatistica['resumo']['quantidade'] += dicionario_base['resumo']['quantidade']
#         if estatistica['resumo']['acertos'] > 0:
#             estatistica['resumo']['percentual'] = round((estatistica['resumo']['acertos'] / estatistica['resumo']['quantidade'])*100, 2) 

#     for index in respostas_enviadas:
#         materia = gabarito['questoes'][index]['materia']
#         qtd_questoes = gabarito['resumo'][materia]['quantidade']
#         if materia in estatistica['itens']:
#             if gabarito['questoes'][index]['resposta'] == respostas_enviadas[index]:
#                 estatistica['itens'][materia]["acertos"] += 1
#             estatistica['itens'][materia]["total"] += 1
#             estatistica['itens'][materia]["respostas"][hoje] = round((
#                 estatistica['itens'][materia]["acertos"] / estatistica['itens'][materia]["total"]
#             )*100,2) if estatistica['itens'][materia]["acertos"] > 0 else 0.00
#         else:
#             estatistica['itens'][materia] = {
#                 "respostas": {},
#                 "acertos": 0,
#                 "total": 1,
#                 "media": 0.00,
#             }
#             if gabarito['questoes'][index]['resposta'] == respostas_enviadas[index]:
#                 estatistica['itens'][materia]["respostas"][hoje] = round((1 / qtd_questoes) * 100, 2)
#                 estatistica['itens'][materia]["acertos"] = 1
#             else:
#                 estatistica['itens'][materia]["respostas"][hoje] = 0.00
#         if estatistica['itens'][materia]["acertos"] > 0:
#             estatistica['itens'][materia]["media"] = round((estatistica['itens'][materia]["acertos"] / estatistica['itens'][materia]["total"]) * 100, 2)
#     matricula.estatisticas = estatistica
#     matricula.save()
#     return

# def salva_estatisticas_simulado(simulado, gabarito, respostas_enviadas, dicionario_base):
#     estatisticas = simulado.estatisticas
#     mes_ano = f'{timezone.now().month}/{timezone.now().year}'
#     created = False
#     materia_utilizada = None
#     if estatisticas == None:
#         estatisticas = {
#             "resumo": {},
#             "questoes": {},
#             "materias": {}
#         }
#         estatisticas["resumo"] = {
#             "acertos": dicionario_base['resumo']["acertos"],
#             "erros": dicionario_base['resumo']["erros"],
#             "quantidade": dicionario_base['resumo']["quantidade"],
#             "media_historica": {
#                 mes_ano: {
#                     "acertos": dicionario_base['resumo']["acertos"],
#                     "quantidade": dicionario_base['resumo']["quantidade"],
#                     "percentual": round((dicionario_base['resumo']["acertos"] / dicionario_base['resumo']["quantidade"])*100, 2) if dicionario_base['resumo']["acertos"] > 0 else 0.00
#                 }
#             }
#         }
#     else:
#         estatisticas["resumo"]["acertos"] += dicionario_base['resumo']["acertos"]
#         estatisticas["resumo"]["erros"] += dicionario_base['resumo']["erros"]
#         estatisticas["resumo"]["quantidade"] += dicionario_base['resumo']["quantidade"]
#         if mes_ano in estatisticas["resumo"]["media_historica"]:
#             estatisticas["resumo"]["media_historica"][mes_ano]['acertos'] += dicionario_base['resumo']["acertos"]
#             estatisticas["resumo"]["media_historica"][mes_ano]['quantidade'] += dicionario_base['resumo']["quantidade"]
#             estatisticas["resumo"]["media_historica"][mes_ano]['percentual'] = round((
#                 estatisticas["resumo"]["media_historica"][mes_ano]['acertos'] / estatisticas["resumo"]["media_historica"][mes_ano]['quantidade'])*100, 2
#                 ) if estatisticas["resumo"]["media_historica"][mes_ano]['acertos'] > 0 else 0.00
#         else:
#             estatisticas["resumo"]["media_historica"][mes_ano] = {
#                 "acertos": dicionario_base['resumo']["acertos"],
#                 "quantidade": dicionario_base['resumo']["quantidade"],
#                 "percentual": round((
#                      dicionario_base['resumo']["acertos"] / dicionario_base['resumo']["quantidade"]
#                 )*100, 2) if dicionario_base['resumo']["acertos"] > 0 else 0.00
#             }

#     for index in respostas_enviadas:
#         if not index in estatisticas["questoes"]:
#             if simulado.questao_tipo == 2:
#                 estatisticas["questoes"][index] = {
#                     "gabarito": gabarito['questoes'][index]['resposta'],
#                     "alternativas" : {
#                         "A":0, "B":0, "C":0, "D":0, "E": 0
#                     }
#                 }
#             else:
#                 estatisticas["questoes"][index] = {
#                     "gabarito": gabarito['questoes'][index]['resposta'],
#                     "alternativas": {
#                         "A":0, "B":0, "C":0, "D":0
#                     }
#                 }
#             estatisticas["questoes"][index]["alternativas"][respostas_enviadas[index]] += 1
#         else:
#             estatisticas["questoes"][index]["alternativas"][respostas_enviadas[index]] += 1   
        
#         materia = gabarito['questoes'][index]['materia']    
#         if materia_utilizada != materia:
#             created = False            
#         if not materia in estatisticas["materias"]:
#             created = True
#             estatisticas["materias"][materia] = { 
#                    "media_historica": {
#                         mes_ano: {
#                             "acertos": dicionario_base['analitico']['materias'][materia]['acertos'],
#                             "quantidade": dicionario_base['analitico']['materias'][materia]['quantidade'],
#                             "percentual": round((
#                                 dicionario_base['analitico']['materias'][materia]['acertos'] / dicionario_base['analitico']['materias'][materia]['quantidade'])*100, 2
#                             ) if dicionario_base['analitico']['materias'][materia]['acertos'] > 0 else 0.00
#                     }
#                 }
#             }
#         else:       
#             if mes_ano in estatisticas["materias"][materia]["media_historica"]:
#                 if not created:
#                     estatisticas["materias"][materia]["media_historica"][mes_ano]["acertos"] += dicionario_base['analitico']['materias'][materia]['acertos']
#                     estatisticas["materias"][materia]["media_historica"][mes_ano]["quantidade"] += dicionario_base['analitico']['materias'][materia]['quantidade']
#                     estatisticas["materias"][materia]["media_historica"][mes_ano]["percentual"] = round((
#                         estatisticas["materias"][materia]["media_historica"][mes_ano]["acertos"] / estatisticas["materias"][materia]["media_historica"][mes_ano]["quantidade"]
#                     )*100, 2) if estatisticas["materias"][materia]["media_historica"][mes_ano]["acertos"] > 0 else 0.00
#             else:
#                 estatisticas["materias"][materia]["media_historica"][mes_ano] = {
#                     "acertos": dicionario_base['analitico']['materias'][materia]['acertos'],
#                     "quantidade": dicionario_base['analitico']['materias'][materia]['quantidade'],
#                     "percentual": round((
#                         dicionario_base['analitico']['materias'][materia]['acertos']/ dicionario_base['analitico']['materias'][materia]['acertos']
#                     )*100, 2) if dicionario_base['analitico']['materias'][materia]['acertos'] > 0 else 0.00
#                 }
#         created = True
#         materia_utilizada = materia
#     simulado.estatisticas = estatisticas
#     simulado.save()
#     return

# def salva_estatisticas_mentoria(mentoria, gabarito, respostas_enviadas, dicionario_base):
#     estatisticas = mentoria.estatisticas
#     mes_ano = f'{timezone.now().month}/{timezone.now().year}'
#     created = False
#     materia_utilizada = None
#     if not estatisticas:        
#         estatisticas = {
#             'resumo': {},
#             'materias': {}
#         }
#         estatisticas['resumo']={
#             "questoes_respondidas": dicionario_base['resumo']['quantidade'],
#             "questoes_corretas": dicionario_base['resumo']['acertos'],            
#             "media_histórica":{
#                 mes_ano: {
#                     'acertos': dicionario_base['resumo']['acertos'], 
#                     'quantidade': dicionario_base['resumo']['quantidade'], 
#                     'percentual': round((dicionario_base['resumo']['acertos'] / dicionario_base['resumo']['quantidade'])*100, 2) if dicionario_base['resumo']['acertos'] > 0 else 0.00
#                 }
#             },
#         }
#     else:
#         estatisticas['resumo']["questoes_respondidas"] += dicionario_base['resumo']['quantidade']
#         estatisticas['resumo']["questoes_corretas"] += dicionario_base['resumo']['acertos']        
#         if not mes_ano in estatisticas['resumo']["media_histórica"]:
#             estatisticas['resumo']['media_histórica'][mes_ano] = {
#                 'acertos': dicionario_base['resumo']['acertos'],
#                 'quantidade': dicionario_base['resumo']['quantidade'],
#                 'percentual': round((dicionario_base['resumo']['acertos']/dicionario_base['resumo']['quantidade'])*100, 2) if dicionario_base['resumo']['acertos'] > 0 else 0.00
#                 }            
#         else:
#             estatisticas['resumo']["media_histórica"][mes_ano]['acertos'] += dicionario_base['resumo']['acertos']
#             estatisticas['resumo']["media_histórica"][mes_ano]['quantidade'] += dicionario_base['resumo']['quantidade']
#             estatisticas['resumo']["media_histórica"][mes_ano]['percentual'] = round((
#                 estatisticas['resumo']["media_histórica"][mes_ano]['acertos'] / estatisticas['resumo']["media_histórica"][mes_ano]['quantidade'])*100, 2
#                 ) if estatisticas['resumo']["media_histórica"][mes_ano]['acertos'] > 0 else 0.00

#     for index in respostas_enviadas:
#         materia = gabarito['questoes'][index]['materia']
#         if materia_utilizada != materia:
#             created = False            
#         if not materia in estatisticas['materias']:
#             created = True
#             estatisticas['materias'][materia]={                
#                 "questoes_corretas": dicionario_base['analitico']['materias'][materia]['acertos'],                
#                 "questoes_respondidas": dicionario_base['analitico']['materias'][materia]['quantidade'],
#                 "media_historica": {
#                     mes_ano: {
#                         'acertos': dicionario_base['analitico']['materias'][materia]['acertos'],
#                         'quantidade': dicionario_base['analitico']['materias'][materia]['quantidade'],
#                         'percentual': round((
#                 dicionario_base['analitico']['materias'][materia]['acertos']/ dicionario_base['analitico']['materias'][materia]['quantidade'])*100, 2
#                 ) if dicionario_base['analitico']['materias'][materia]['acertos'] > 0 else 0.00
#                     } 
#                 }
#             }
#         else:
#             if not created:
#                 estatisticas['materias'][materia]["questoes_corretas"] += dicionario_base['analitico']['materias'][materia]['acertos']
#                 estatisticas['materias'][materia]["questoes_respondidas"] += dicionario_base['analitico']['materias'][materia]['quantidade']                 
#             if mes_ano in estatisticas['materias'][materia]["media_historica"]:
#                 if not created:
#                     estatisticas['materias'][materia]["media_historica"][mes_ano]['acertos'] += dicionario_base['analitico']['materias'][materia]['acertos']
#                     estatisticas['materias'][materia]["media_historica"][mes_ano]['quantidade'] += dicionario_base['analitico']['materias'][materia]['quantidade']
#                     if estatisticas['materias'][materia]["media_historica"][mes_ano]['acertos'] > 0:
#                         estatisticas['materias'][materia]["media_historica"][mes_ano]['percentual'] = round((
#                             estatisticas['materias'][materia]["media_historica"][mes_ano]['acertos'] / estatisticas['materias'][materia]["media_historica"][mes_ano]['quantidade']
#                         )*100, 2)
#             else:
#                 created = True
#                 estatisticas['materias'][materia]["media_historica"][mes_ano] = {
#                     'acertos': dicionario_base['analitico']['materias'][materia]['acertos'],
#                     'quantidade': dicionario_base['analitico']['materias'][materia]['quantidade'],
#                     'percentual':  round((
#                         dicionario_base['analitico']['materias'][materia]['acertos'] / dicionario_base['analitico']['materias'][materia]['quantidade']
#                     )*100, 2) if dicionario_base['analitico']['materias'][materia]['acertos'] > 0 else 0.00
#                 }
#         created = True
#         materia_utilizada = materia
#     mentoria.estatisticas = estatisticas
#     mentoria.save()
#     return



# class LineChartJSONView(BaseLineChartView):

#     def setup(self, *args, **kwargs):        
#         self.maior_tamanho = ['', 0]
#         matricula = MatriculaAPainel do desempenho
#             print('Tipo None não é iterável', e)
#         return labels

#     def get_providers(self):
#         """Return names of datasets."""
#         datasets = []
#         try:
#             for key in self.estats['itens']:
#                 datasets.append(key)
#         except TypeError:
#             print('Tipo None não é iterável.')
#         return datasets

#     def get_data(self):
#         data = []
#         try:
#             for key in self.estats['itens']:
#                 if (len(self.estats['itens'][key]) > self.maior_tamanho[1]):
#                     self.maior_tamanho[1] = len(self.estats['itens'][key])
#                     self.maior_tamanho[0] = key
#             for key in self.estats['itens']:
#                 valores = []
#                 for dia in self.estats['itens'][key]:
#                     valores.append(self.estats['itens'][key][dia])
#                 data.append(valores)
#         except TypeError:
#             print('Tipo None não é iterável.')
#         return data



COLORS = [
    (226, 124, 124), 
    (168, 100, 100),  
    (0, 63, 92),  
    (68, 78, 134),
    (149, 81, 150),
    (221, 81, 130),    
    (202, 201, 197),  # Light gray
    (171, 9, 0),  # Red
    (166, 78, 46),  # Light orange
    (255, 190, 67),  # Yellow
    (163, 191, 63),  # Light green
    (122, 159, 191),  # Light blue
    (140, 5, 84),  # Pink
    (166, 133, 93),  # Light brown
    (75, 64, 191),  # Red blue
    (237, 124, 60),  # orange
]

def next_color(color_list=COLORS):
    """Create a different color from a base color list.

    >>> color_list = (
    ...    (122, 159, 191),  # Light blue
    ...    (202, 201, 197),  # Light gray,
    ... )
    >>> g = next_color(color_list)
    >>> next(g)
    [122, 159, 191]
    >>> next(g)
    [202, 201, 197]
    >>> next(g)
    [63, 100, 132]
    >>> next(g)
    [143, 142, 138]
    >>> next(g)
    [4, 41, 73]
    >>> next(g)
    [84, 83, 79]
    """
    step = 0
    while True:
        for color in color_list:
            yield list(map(lambda base: (base + step) % 256, color))
        step += 197
        


