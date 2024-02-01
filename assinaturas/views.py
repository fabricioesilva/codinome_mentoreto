from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.utils.translation import gettext as _
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from datetime import datetime, date, timedelta
from dateutil import relativedelta
import zoneinfo

from utils.resources import POLICY_LANGUAGES
from .models import AssinaturasMentor, FaturasMentores, PrecosAssinatura, OfertasPlanos, TermosAceitos, TermosDeUso
from mentorias.models import Mentoria, MatriculaAlunoMentoria, RegistrosMentor
from usuarios.forms import PerfilCobrancaForm

# Create your views here.
def oferta_detalhe(request):
    template_name = 'assinaturas/oferta_detalhe.html'
    oferta_disponivel = OfertasPlanos.objects.filter(ativa=True, tipo=2)[0]
    if oferta_disponivel:
        oferta_percentual = oferta_disponivel.desconto_incluido.percentual_desconto
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
        'valor_total': "{:.2f}".format(valor_total),
        'oferta_disponivel': oferta_disponivel,
        'oferta_percentual': oferta_percentual
    }
    return render(request, template_name, ctx)


def faturas_mentor(request):
    if request.user.is_anonymous:
        return redirect('usuarios:index')   
    template_name = 'assinaturas/faturas_mentor.html'
    assinatura = AssinaturasMentor.objects.filter(mentor=request.user, encerra_em__gte=date.today())
    if not assinatura:
        contrata_assinatura(request.user)
    mes_atual = date.today()
    mes_seguinte = mes_atual + relativedelta.relativedelta(months=1)
    mes_seguinte = mes_seguinte.replace(day=15)
    faturas = FaturasMentores.objects.filter(mentor=request.user, )
    ctx = {
        'mes_atual': mes_atual.strftime("%b"),
        'mes_seguinte': mes_seguinte,
        'faturas': faturas
        }
    return render(request, template_name, ctx)


def proxima_fatura(request):
    if request.user.is_anonymous:
        return redirect('usuarios:index')
    template_name = 'assinaturas/proxima_fatura.html'
    data_atual = date.today()
    inicio_mes_atual = data_atual.replace(day=1) 
    mes_anterior = inicio_mes_atual - timedelta(days=1)
    inicio_mes_anterior = mes_anterior.replace(day=1)
    assinatura = AssinaturasMentor.objects.filter(mentor=request.user, encerra_em__gte=inicio_mes_anterior).exclude(inicia_vigencia__gte=inicio_mes_anterior).first()
    if not assinatura:
        assinatura = contrata_assinatura(request.user)        
    mentorias = Mentoria.objects.filter(mentor=request.user)
    matriculas = MatriculaAlunoMentoria.objects.filter(
            Q(mentoria__in=mentorias) & (
                Q(ativa=True) | ( Q(data_desativada__gte=inicio_mes_atual)))
                ) 
    mes_seguinte = data_atual + relativedelta.relativedelta(months=1)
    mes_seguinte = mes_seguinte.replace(day=15)
    total, quantidades, valor_total = get_faixa_cobrancas(matriculas, assinatura)
    ctx = {
        'mes_seguinte': mes_seguinte,
        'assinatura': assinatura,
        'total': total, 
        'quantidades': quantidades, 
        'valor_total': valor_total,
        'valor_por_aluno': "0,00" if total == 0 else round(valor_total / total, 2),
        'matriculas': matriculas,
        'mes_isento': 'sim' if assinatura.log_meses_isencao_restante > 0 else 'nao'
        }
    return render(request, template_name, ctx)


def fatura_detalhe(request, pk):
    if request.user.is_anonymous:
        return redirect('usuarios:index')
    fatura = get_object_or_404(FaturasMentores, pk=pk)
    template_name = 'assinaturas/fatura_detalhe.html'
    ctx = {
        'demonstrativo': fatura.demonstrativo,
        'fatura': fatura
        }
    return render(request, template_name, ctx)


def assinatura_detalhe(request):
    template_name="assinaturas/assinatura_detalhe.html"
    assinaturas_mentor = AssinaturasMentor.objects.filter(mentor=request.user).order_by('-pk')
    assinatura_atual = assinaturas_mentor.filter(ativa=True, encerra_em__gte=datetime.now(tz=zoneinfo.ZoneInfo(settings.TIME_ZONE))).order_by('-pk')
    if assinatura_atual:
        assinatura_atual = assinatura_atual[0]
    else:
        return redirect('assinaturas:oferta_detalhe')
    faixas = []
    precos_dicio = dict(assinatura_atual.log_precos_contratados['display'])
    for faixa in precos_dicio:        
        faixas.append(precos_dicio[faixa][2])
    total_matriculas_exemplo, quantidades_exemplo, valor_total_exemplo = get_faixa_de_exemplo(15, assinatura_atual)
    ctx={
        'assinaturas_mentor': assinaturas_mentor,
        'assinatura_atual': assinatura_atual,
        'faixas': faixas,
        'valor_por_aluno': "0,00" if total_matriculas_exemplo == 0 else str(format(round(float(valor_total_exemplo.replace(',', '.')) / total_matriculas_exemplo, 2), '.2f').replace('.', ',')),
        'valor_total': valor_total_exemplo,
        'total':total_matriculas_exemplo,
        'quantidades': quantidades_exemplo
    }
    if request.method == 'POST':
        total_matriculas_exemplo, quantidades_exemplo, valor_total_exemplo = get_faixa_de_exemplo(int(request.POST.get("quantidadaEnviada")), assinatura_atual)
        new_ctx = {}
        new_ctx['valor_por_aluno'] = "0,00" if total_matriculas_exemplo == 0 else str(format(round(float(valor_total_exemplo.replace(',', '.')) / total_matriculas_exemplo, 2), '.2f')).replace('.', ',')
        new_ctx['valor_total'] = valor_total_exemplo
        new_ctx['total'] = total_matriculas_exemplo
        new_ctx['quantidades'] = quantidades_exemplo    
        return JsonResponse(new_ctx)
    return render(request, template_name, ctx)

def get_faixa_cobrancas(matriculas, assinatura):    
    total = matriculas.count()
    precos = assinatura.log_precos_contratados['display']    
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
            quantidades[letra].append(str(format(quantidades[letra][0] * float(quantidades[letra][2].replace(',', '.')), '.2f')).replace('.', ','))
        else:
            quantidades[letra].append("0,00")
        limite_anterior = int(precos[letra][0])
        valor_total += 0.00 if quantidades[letra][3] == '0,00' else float(quantidades[letra][3].replace(',', '.'))
    return total, quantidades, round(valor_total, 2)


def get_faixa_de_exemplo(quantidade, assinatura):    
    total = quantidade
    precos = assinatura.log_precos_contratados['display']    
    quantidades = {}  
    limite_anterior = 0
    valor_total = 0.00
    for letra in precos:
        quantidades[letra]=[]        
        if total == int(precos[letra][0]):
            quantidades[letra].append(total - limite_anterior)
        elif total > float(precos[letra][0]):
            quantidades[letra].append((int(precos[letra][0]) - limite_anterior))
        else:
            if (total - limite_anterior) > 0:
                quantidades[letra].append(total - limite_anterior)
            else:
                quantidades[letra].append(0)
        # [2, 'Tarifa A(máximo duas)', '0.00', '0.00']
        quantidades[letra].append(precos[letra][1])
        quantidades[letra].append(format(precos[letra][2]))
        if quantidades[letra][0] > 0:
            quantidades[letra].append(str(format(quantidades[letra][0] * float(str(quantidades[letra][2]).replace(',', '.')), '.2f')).replace('.', ','))
        else:
            quantidades[letra].append("0,00")
        limite_anterior = int(precos[letra][0])        
        valor_total += 0.00 if quantidades[letra][3] == "0,00" else float(quantidades[letra][3].replace(',', '.'))
    return total, quantidades, str(round(valor_total, 2)).replace('.', ',')



def assinar_plano(request):
    if request.user.is_anonymous:
        return redirect('usuarios:cadastro')
    assinaturas_mentor = AssinaturasMentor.objects.filter(mentor=request.user, ativa=True, encerra_em__gte=datetime.now(tz=zoneinfo.ZoneInfo(settings.TIME_ZONE)))
    if assinaturas_mentor:
        return redirect('assinaturas:assinatura_detalhe')
    template_name = 'assinaturas/assinar_plano.html'
    form = PerfilCobrancaForm()
    oferta_disponivel = OfertasPlanos.objects.filter(ativa=True, tipo=2)[0]
    if oferta_disponivel:
        oferta_percentual = oferta_disponivel.desconto_incluido.percentual_desconto
    else:
        oferta_percentual = None
    plano_disponivel = PrecosAssinatura.objects.get(ativo=True)

    if request.method == 'POST':
        ano_seguinte = datetime.now(tz=zoneinfo.ZoneInfo(settings.TIME_ZONE))+timedelta(days=365)
        form = PerfilCobrancaForm(request.POST)
        if form.is_valid():
            perfil = form.save(commit=False)
            perfil.usuario = request.user
            perfil.perfil_pagamento = request.POST.get('perfil_pagamento')
            perfil.save()
            AssinaturasMentor.objects.create(
                mentor=request.user,
                oferta_contratada=oferta_disponivel,
                encerra_em=ano_seguinte,                
            )
            termo=TermosDeUso.objects.filter(
                language=request.user.policy_lang, active=True)
            if not termo:
                termo=TermosDeUso.objects.get(
                language='pt', active=True)
            else:
                termo = termo[0]
            TermosAceitos.objects.create(
            user=request.user,
            termo=termo
            )
            messages.success(request, _('Parabéns! Seu cadastro foi efetivado e o acesso aos recursos foi liberado!'))
            return redirect("assinaturas:assinatura_detalhe")
        else:
            form = PerfilCobrancaForm(request.POST)
        
    ctx = {
        'plano_disponivel': plano_disponivel,
        'oferta_disponivel': oferta_disponivel,
        'oferta_percentual': oferta_percentual,
        'form': form
    }
    return render(request, template_name, ctx)


# Create your views here.
def termo_de_uso(request):
    if request.method == 'GET':
        if request.LANGUAGE_CODE in POLICY_LANGUAGES:
            context = {'termo': TermosDeUso.objects.get(
                language=request.LANGUAGE_CODE, active=True)}
        else:
            context = {'termo': TermosDeUso.objects.get(
                language='en', active=True)}
        return render(request, 'assinaturas/termo_de_uso.html', context)
    else:
        return redirect('assinaturas:assinar_plano')


def contrata_assinatura(user):
    oferta = OfertasPlanos.objects.get(ativa=True)
    if not oferta:
        oferta = OfertasPlanos.objects.first()
    assinatura = AssinaturasMentor.objects.filter(mentor=user).first()
    hoje = date.today()
    if not assinatura:
        AssinaturasMentor.objects.create(
        mentor=user,
        oferta_contratada=oferta,
        inicia_vigencia=date.today(),
        encerra_em=date(year=hoje.year+1, month=hoje.month, day=28)
        )
    else:
        encerramento_matricula = assinatura.encerra_em
        AssinaturasMentor.objects.create(
            mentor=user,
            oferta_contratada=oferta,
            inicia_vigencia=encerramento_matricula+timedelta(days=1),
            encerra_em=date(year=encerramento_matricula.year+1, month=encerramento_matricula.month, day=28)
        )
    return assinatura

@login_required
def historico_matriculas(request):
    template_name = 'assinaturas/historico_matriculas.html'
    periodo = datetime.now(zoneinfo.ZoneInfo(settings.TIME_ZONE)) - timedelta(days=90)  
    if request.user.is_anonymous:
        return redirect('usuarios:index')
    registros=RegistrosMentor.objects.filter(log_mentor_id=request.user.id, data_registro__gte=periodo)
    paginate =  Paginator(registros, 20)
    registros_pages = paginate.get_page(request.GET.get("page"))
    ctx = {
        'registros_pages': registros_pages
        }
    return render(request, template_name, ctx)

