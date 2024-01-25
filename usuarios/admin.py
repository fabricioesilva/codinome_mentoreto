from django.contrib import admin
from datetime import date, timedelta
from .models import CustomUser, UserEmailCheck, Preferences, DeletedUser, PerfilCobranca
from assinaturas.models import AssinaturasMentor, OfertasPlanos



@admin.action(description="Contrata assinatura com novo plano para geral")
def contrata_assinatura_geral(modeladmin, request, queryset):
    oferta = OfertasPlanos.objects.get(ativa=True)
    for mentor in queryset:
        assinatura = AssinaturasMentor.objects.filter(mentor=mentor, encerra_em__gte=date.today()).first()
        hoje = date.today()
        if not assinatura:
            AssinaturasMentor.objects.create(
            mentor=mentor,
            oferta_contratada=oferta,
            encerra_em=date(year=hoje.year+1, month=hoje.month, day=hoje.day)
            )
        else:
            sessenta_dias_adiante = date.today() + timedelta(days=60)
            encerramento_matricula = assinatura.encerra_em
            if encerramento_matricula > sessenta_dias_adiante:                
                continue            
            AssinaturasMentor.objects.create(
                mentor=mentor,
                oferta_contratada=oferta,
                encerra_em=date(year=encerramento_matricula.year+1, month=encerramento_matricula.month, day=encerramento_matricula.day)
            )
       

class CustomUserAdmin(admin.ModelAdmin):
    actions=[contrata_assinatura_geral]
    list_display = ('pk', 'username', 'email', 'email_checked')

# Register your models here.
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserEmailCheck)
admin.site.register(Preferences)
admin.site.register(DeletedUser)
admin.site.register(PerfilCobranca)
