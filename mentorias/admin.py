from django.contrib import admin
from .models import (
    Mentorias,
    ArquivosMentoria,
    Alunos,
    ArquivosAluno,
    Simulados,
    RespostasSimulados,
    Materias,
    MatriculaAlunoMentoria, 
    LinksExternos,
    AplicacaoSimulado
)
# Register your models here.
admin.site.register(Mentorias)
admin.site.register(ArquivosMentoria)
admin.site.register(Alunos)
admin.site.register(ArquivosAluno)
admin.site.register(Simulados)
admin.site.register(RespostasSimulados)
admin.site.register(Materias)
admin.site.register(MatriculaAlunoMentoria)
admin.site.register(LinksExternos)
admin.site.register(AplicacaoSimulado)
