from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
import datetime
from dateutil import relativedelta
import zoneinfo

from .models import AssinaturasMentor, FaturasMentores
from mentorias.models import AplicacaoSimulado, Mentoria, MatriculaAlunoMentoria

# Create your views here.


def assinaturas_mentor(request):
    template_name = 'assinatura/assinaturas_mentor.html'
    return render(request, template_name, {})


def faturas_mentor(request):
    if request.user.is_anonymous:
        return redirect('usuarios:index')
    template_name = 'assinaturas/faturas_mentor.html'
    assinatura = AssinaturasMentor.objects.get(mentor=request.user, encerra_em__gte=datetime.datetime.now(tz=zoneinfo.ZoneInfo(settings.TIME_ZONE)))
    mentorias = Mentoria.objects.filter(mentor=request.user)
    matriculas = MatriculaAlunoMentoria.objects.filter(mentoria__in=mentorias)
    mes_atual = datetime.date.today().month
    ano_atual = datetime.date.today().year    
    mes_seguinte = datetime.date.today() + relativedelta.relativedelta(months=1)
    mes_seguinte = mes_seguinte.replace(day=15)    
    aplicacoes = AplicacaoSimulado.objects.filter(matricula__in=matriculas, data_resposta__isnull=False).filter(
        data_resposta__month=mes_atual, data_resposta__year=ano_atual)
    distintos = aplicacoes.distinct('aluno_id').order_by('aluno_id')
    total, quantidades, valor_total = get_faixa_cobrancas(distintos, assinatura)
    faturas = FaturasMentores.objects.filter(mentor=request.user, )
    ctx = {
        'mes_seguinte': mes_seguinte,
        'assinatura': assinatura, 
        'aplicacoes': aplicacoes, 
        'total': total, 
        'quantidades': quantidades, 
        'valor_total': valor_total,
        'faturas': faturas
        }
    return render(request, template_name, ctx)


def proxima_fatura(request):
    if request.user.is_anonymous:
        return redirect('usuarios:index')
    template_name = 'assinaturas/proxima_fatura.html'
    assinatura = AssinaturasMentor.objects.get(mentor=request.user, encerra_em__gte=datetime.datetime.now(tz=zoneinfo.ZoneInfo(settings.TIME_ZONE)))
    mentorias = Mentoria.objects.filter(mentor=request.user)
    matriculas = MatriculaAlunoMentoria.objects.filter(mentoria__in=mentorias)
    mes_atual = datetime.date.today().month    
    ano_atual = datetime.date.today().year    
    mes_seguinte = datetime.date.today() + relativedelta.relativedelta(months=1)
    mes_seguinte = mes_seguinte.replace(day=15)
    aplicacoes = AplicacaoSimulado.objects.filter(matricula__in=matriculas, data_resposta__isnull=False).filter(
        data_resposta__month=mes_atual, data_resposta__year=ano_atual)
    distintos = aplicacoes.distinct('aluno_id').order_by('aluno_id')
    total, quantidades, valor_total = get_faixa_cobrancas(distintos, assinatura)
    ctx = {
        'mes_seguinte': mes_seguinte,
        'assinatura': assinatura, 
        'aplicacoes': aplicacoes, 
        'total': total, 
        'quantidades': quantidades, 
        'valor_total': valor_total,
        }
    return render(request, template_name, ctx)


def fatura_detalhe(request, pk):
    if request.user.is_anonymous:
        return redirect('usuarios:index')
    fatura = get_object_or_404(FaturasMentores, pk=pk)
    mes_referencia, ano_referencia = fatura.mes_referencia.split('/')
    template_name = 'assinaturas/fatura_detalhe.html'
    assinatura = AssinaturasMentor.objects.get(mentor=request.user, encerra_em__gte=datetime.datetime.now(tz=zoneinfo.ZoneInfo(settings.TIME_ZONE)))
    mentorias = Mentoria.objects.filter(mentor=request.user)
    matriculas = MatriculaAlunoMentoria.objects.filter(mentoria__in=mentorias) 
    aplicacoes = AplicacaoSimulado.objects.filter(matricula__in=matriculas, data_resposta__isnull=False).filter(
        data_resposta__month=mes_referencia, data_resposta__year=ano_referencia)

    ctx = {
        'demonstrativo': fatura.demonstrativo,
        'aplicacoes': aplicacoes, 
        'fatura': fatura
        }
    return render(request, template_name, ctx)


def assinatura_detalhe(request):
    template_name="assinaturas/assinatura_detalhe.html"
    assinatura_detalhe = AssinaturasMentor.objects.filter(mentor=request.user).order_by('-pk')[0]
    ctx={
        'assinatura_detalhe': assinatura_detalhe
    }
    return render(request, template_name, ctx)

def get_faixa_cobrancas(aplicacoes, assinatura):
    precos = assinatura.log_precos_contratados['display']
    total = aplicacoes.count()
    quantidades = {}  
    limite_anterior = 0
    valor_total = 0
    for letra in precos:
        quantidades[letra]=[]        
        if total == int(precos[letra][0]):
            quantidades[letra].append(total - limite_anterior)
        elif total > int(precos[letra][0]):
            quantidades[letra].append(int(precos[letra][0]) - limite_anterior)
        else:
            if (total - limite_anterior) > 0:
                quantidades[letra].append(total - limite_anterior)
            else:
                quantidades[letra].append(0)
        quantidades[letra].append(precos[letra][1])
        quantidades[letra].append(precos[letra][2])
        if quantidades[letra][0] > 0:            
            quantidades[letra].append(quantidades[letra][0] * quantidades[letra][2])
        else:
            quantidades[letra].append(0.00)
        limite_anterior = int(precos[letra][0])
        valor_total += quantidades[letra][3]
    return total, quantidades, round(valor_total, 2)
