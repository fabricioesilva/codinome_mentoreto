from django.contrib import admin
from django.conf import settings
from django_summernote.admin import SummernoteModelAdmin
from django.db.models import Q
from datetime import datetime, date, timedelta
# from dateutil import relativedelta
# import zoneinfo
# Register your models here.
from mentorias.models import MatriculaAlunoMentoria, AplicacaoSimulado, Mentoria
from .models import *




admin.site.register(PrecosAssinatura)
admin.site.register(Descontos)
admin.site.register(OfertasPlanos)
admin.site.register(FaturasMentores)
# admin.site.register(AssinaturasMentor)


@admin.action(description="Fechar faturas dos mentores")
def fecha_fatura_mentores(modeladmin, request, queryset):
    # data_atual = datetime.now()
    data_atual = date.today()
    # mes_anterior = data_atual + relativedelta.relativedelta(months=-1)
    inicio_mes_atual = data_atual.replace(day=1) 
    mes_anterior = inicio_mes_atual - timedelta(days=1)
    inicio_mes_anterior = mes_anterior.replace(day=1)
    assinaturas = queryset.filter(encerra_em__gte=inicio_mes_anterior).exclude(inicia_vigencia__gte=inicio_mes_anterior)
    # data_atual = datetime.datetime.now(tz=zoneinfo.ZoneInfo(settings.TIME_ZONE))
    for assinatura in assinaturas:
        mentorias = Mentoria.objects.filter(mentor=assinatura.mentor)
        matriculas = MatriculaAlunoMentoria.objects.filter(
            Q(mentoria__in=mentorias) & Q(criada_em__lt=inicio_mes_atual) & (
                Q(ativa=True) | ( Q(data_desativada__gte=inicio_mes_anterior)))
                )
        # aplicacoes = AplicacaoSimulado.objects.filter(matricula__in=matriculas, data_resposta__isnull=False).filter(
        # data_resposta__month=mes_anterior.month, data_resposta__year=mes_anterior.year)
        # distintos = aplicacoes.distinct('aluno_id').order_by('aluno_id')
        precos = assinatura.log_precos_contratados['display']
        total = matriculas.count()
        quantidades = {
            "quantidade": 0,
            "relacao": {},
            "valor_total": 0,
            "matriculas_consideradas": {}
        }
        for matricula in matriculas:
            quantidades['matriculas_consideradas'][str(matricula.pk)] = {}
            # quantidades['matriculas_consideradas']['matricula_pk'] = matricula.pk
            quantidades['matriculas_consideradas'][str(matricula.pk)]['matricula_aluno'] = matricula.aluno.nome_aluno
            quantidades['matriculas_consideradas'][str(matricula.pk)]['matricula_mentoria'] = matricula.mentoria.titulo
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
                quantidades['mes_isento'] = {"sim": "Mês com isenção total!"}
            mes_isento = True
            zerada = True
        else:
            zerada = False
            quantidades['mes_isento'] = {"nao":"Normal"}
            if valor_total == 0:
                zerada = True
            mes_isento = False
        quantidades['valor_por_aluno'] = 0 if valor_total == 0 else round(valor_total / total, 2)
        quantidades['quantidade'] = total
        quantidades['valor_total'] = valor_total
        FaturasMentores.objects.create(
            mentor = assinatura.mentor,
            assinatura = assinatura,
            demonstrativo = quantidades,
            mes_referencia = F"{mes_anterior.month}/{mes_anterior.year}",
            gastos_no_mes = valor_total,
            vencimento = data_atual.replace(day=15),
            mentor_cpf = assinatura.mentor.cpf_usuario,
            mes_isento = mes_isento,
            total_a_pagar = 0.00 if zerada else valor_total,
            foi_paga = zerada,
            data_pagamento = data_atual.replace(day=15) if zerada else None,
            numero_transacao = "0000000" if zerada else None
        )


class AssinaturasMentorAdmin(admin.ModelAdmin):
    actions = [fecha_fatura_mentores]
    list_display = ['mentor', 'resumo', 'criada_em', 'inicia_vigencia', 'encerra_em', 'ativa']   

admin.site.register(AssinaturasMentor, AssinaturasMentorAdmin)

class TermosDeUsoAdmin(SummernoteModelAdmin):
    model = TermosDeUso
    summernote_fields = ('text',)
    readonly_fields = ['criada_em', 'user', 'user_email', 'termo_user_id']

    def save_model(self, request, obj, form, change):
        if obj.active:
            try:
                atual = TermosDeUso.objects.get(
                    language=obj.language, active=True)
                atual.active = False
                atual.save()
            except TermosDeUso.DoesNotExist:
                atual = None
        obj.user = request.user
        obj.user_email = obj.user.email
        obj.termo_user_id = obj.user.pk
        super().save_model(request, obj, form, change)
        if change:
            AlteracoesTermos.objects.create(
                user_email=obj.user.email,
                termo_user_id=obj.user.pk,
                termo_title=obj.termo_title,
                termo_status=str(obj.active),
                termo_content=obj.text,
                termo_pkey=obj.pk,
                action='Changed'
            )
        else:
            AlteracoesTermos.objects.create(
                user_email=obj.user.email,
                termo_user_id=obj.user.pk,
                termo_title=obj.termo_title,
                termo_status=str(obj.active),
                termo_content=obj.text,
                termo_pkey=obj.pk,
                action='Created'
            )

    def delete_model(self, request, obj):
        AlteracoesTermos.objects.create(
            user_email=obj.user.email,
            termo_user_id=obj.user.pk,
            termo_title=obj.termo_title,
            termo_status=str(obj.active),
            termo_content=obj.text,
            termo_pkey=obj.pk,
            action='Deleted'
        )
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            AlteracoesTermos.objects.create(
                user_email=obj.user.email,
                termo_user_id=obj.user.pk,
                termo_title=obj.termo_title,
                termo_status=str(obj.active),
                termo_content=obj.text,
                termo_pkey=obj.pk,
                action='Deleted'
            )
        queryset.delete()
        # super().delete_queryset(request, queryset)


class TermosAceitosAdmin(admin.ModelAdmin):
    readonly_fields = ['user', 'user_email',
                       'profile_id', 'acept_date', 'termo']


class AlteracoesTermosAdmin(admin.ModelAdmin):
    readonly_fields = ['user_email', 'termo_user_id', 'termo_status',
                       'termo_content', 'termo_pkey', 'mod_date', 'action']


admin.site.register(TermosDeUso, TermosDeUsoAdmin)
admin.site.register(TermosAceitos, TermosAceitosAdmin)
admin.site.register(AlteracoesTermos, AlteracoesTermosAdmin)
# admin.site.register(TermosAceitos)




