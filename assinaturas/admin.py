from django.contrib import admin
import datetime
from dateutil import relativedelta
# Register your models here.
from usuarios.models import CustomUser
from mentorias.models import MatriculaAlunoMentoria, AplicacaoSimulado, Mentoria
from .models import *




admin.site.register(PrecosAssinatura)
admin.site.register(Descontos)
admin.site.register(OfertasPlanos)
admin.site.register(FaturasMentores)
# admin.site.register(AssinaturasMentor)


@admin.action(description="Fechar faturas dos mentores")
def fecha_fatura_mentores(AssinaturasMentor, reqyest, queryset):
    data_atual = datetime.datetime.now()
    mes_anterior = data_atual + relativedelta.relativedelta(months=-1)
    assinaturas = queryset.filter(encerra_em__gte=datetime.datetime.now())
    for assinatura in assinaturas:
        mentorias = Mentoria.objects.filter(mentor=assinatura.mentor)
        matriculas = MatriculaAlunoMentoria.objects.filter(mentoria__in=mentorias)
        aplicacoes = AplicacaoSimulado.objects.filter(matricula__in=matriculas, data_resposta__isnull=False).filter(
        data_resposta__month=mes_anterior.month, data_resposta__year=mes_anterior.year)
        distintos = aplicacoes.distinct('aluno_id').order_by('aluno_id')
        precos = assinatura.log_precos_contratados['display']
        total = aplicacoes.count()
        quantidades = {
            "quantidade": 0,
            "relacao": {}
        }
        limite_anterior = 0
        valor_total = 0
        for letra in precos:
            quantidades['relacao'][letra]=[]
            if total == int(precos[letra][0]):
                quantidades['relacao'][letra].append(total - limite_anterior)
            elif total > int(precos[letra][0]):
                quantidades['relacao'][letra].append(int(precos[letra][0]) - limite_anterior)
            else:
                if (total - limite_anterior) > 0:
                    quantidades['relacao'][letra].append(total - limite_anterior)
                else:
                    quantidades['relacao'][letra].append(0)
            quantidades['relacao'][letra].append(precos[letra][1])
            quantidades['relacao'][letra].append(precos[letra][2])
            if quantidades['relacao'][letra][0] > 0:            
                quantidades['relacao'][letra].append(quantidades['relacao'][letra][0] * quantidades['relacao'][letra][2])
            else:
                quantidades['relacao'][letra].append(0.00)
            limite_anterior = int(precos[letra][0])
            valor_total += quantidades['relacao'][letra][3]
        
        if assinatura.log_meses_isencao_restante > 0:
            if valor_total > 0:
                assinatura.log_meses_isencao_restante-=1
                assinatura.save()
            mes_isento = True
            foi_paga = True
        else:
            foi_paga = False
            if valor_total == 0:
                foi_paga = True
            mes_isento = False
        quantidades['quantidade'] = total
        FaturasMentores.objects.create(
            mentor = assinatura.mentor,
            assinatura = assinatura,
            demonstrativo = quantidades,
            mes_referencia = F"{mes_anterior.month}/{mes_anterior.year}",
            gastos_no_mes = valor_total,
            vencimento = data_atual.replace(day=15),
            mentor_cpf = assinatura.mentor.cpf_usuario,
            mes_isento = mes_isento,
            total_a_pagar = 0.00 if foi_paga else valor_total,
            foi_paga = foi_paga,
            data_pagamento = data_atual.replace(day=15) if foi_paga else None,
            numero_transacao = "Não se aplica" if foi_paga else None
        )
        # return total, quantidades, round(valor_total, 2)


class AssinaturasMentorAdmin(admin.ModelAdmin):
    actions = [fecha_fatura_mentores]


admin.site.register(AssinaturasMentor, AssinaturasMentorAdmin)