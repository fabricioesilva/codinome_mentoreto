from django.contrib import admin
from .models import (
    Mentoria,
    ArquivosMentoria,
    Alunos,
    Simulados,
    Materias,
    MatriculaAlunoMentoria,
    LinksExternos,
    AplicacaoSimulado,
    RegistrosMentor
)
# Register your models here.
admin.site.register(Mentoria)
admin.site.register(ArquivosMentoria)
admin.site.register(Alunos)
admin.site.register(Simulados)
admin.site.register(Materias)
admin.site.register(MatriculaAlunoMentoria)
admin.site.register(LinksExternos)
admin.site.register(AplicacaoSimulado)
admin.site.register(RegistrosMentor)
