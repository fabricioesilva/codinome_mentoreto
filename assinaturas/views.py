from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
import datetime
from dateutil import relativedelta
import zoneinfo

from .models import AssinaturasMentor, FaturasMentores, PrecosAssinatura, OfertasPlanos, TermosAceitos, TermosDeUso
from mentorias.models import AplicacaoSimulado, Mentoria, MatriculaAlunoMentoria
from usuarios.forms import PerfilCobrancaForm

# Create your views here.
def contratar_assinatura(request):
    template_name = 'assinaturas/contratar_assinatura.html'
    oferta_disponivel = OfertasPlanos.objects.filter(ativa=True, tipo=2)
    if oferta_disponivel:
        oferta_percentual = oferta_disponivel[0].desconto_incluido.percentual_desconto
    else:
        oferta_percentual = None
    plano_disponivel = PrecosAssinatura.objects.get(ativo=True)
    faixas = []
    precos_dicio = dict(plano_disponivel.precos['display'])
    for faixa in precos_dicio:        
        faixas.append(precos_dicio[faixa][2])    
    valor_total = float(faixas[0].replace(',', '.'))+float(faixas[1].replace(',', '.'))+(3*float(faixas[2].replace(',', '.')))+(5*float(faixas[3].replace(',', '.')))+(5*float(faixas[4].replace(',', '.')))
    ctx = {
        'plano_disponivel': plano_disponivel,
        'faixas': faixas,
        'valor_total': valor_total,
        'oferta_disponivel': oferta_disponivel[0],
        'oferta_percentual': oferta_percentual
    }
    return render(request, template_name, ctx)


def faturas_mentor(request):
    if request.user.is_anonymous:
        return redirect('usuarios:index')
    
    template_name = 'assinaturas/faturas_mentor.html'
    assinatura = AssinaturasMentor.objects.filter(mentor=request.user, encerra_em__gte=datetime.datetime.now(tz=zoneinfo.ZoneInfo(settings.TIME_ZONE)))
    if assinatura:
        assinatura = assinatura[0]
    else:
        return redirect('assinaturas:contratar_assinatura')
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


def assinar_plano(request):
    template_name = 'assinaturas/assinar_plano.html'
    form = PerfilCobrancaForm()
    oferta_disponivel = OfertasPlanos.objects.filter(ativa=True, tipo=2)
    if oferta_disponivel:
        oferta_percentual = oferta_disponivel[0].desconto_incluido.percentual_desconto
    else:
        oferta_percentual = None
    plano_disponivel = PrecosAssinatura.objects.get(ativo=True)
    faixas = []
    precos_dicio = dict(plano_disponivel.precos['display'])
    for faixa in precos_dicio:        
        faixas.append(precos_dicio[faixa][2]) 
    ctx = {
        'plano_disponivel': plano_disponivel,
        'faixas': faixas,        
        'oferta_disponivel': oferta_disponivel[0],
        'oferta_percentual': oferta_percentual,
        'form': form
    }
    TermosAceitos.objects.create(
    user=request.user,
    termo=TermosDeUso.objects.get(
        language=request.user.policy_lang, active=True)
    )
    return render(request, template_name, ctx)

