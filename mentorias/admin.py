from django.contrib import admin
from .models import (
    Mentorias,
    ArquivosMentor,
    ArquivosMentoria,
    Turmas,
    Alunos,
    ArquivosAluno,
    Simulados,
    Gabaritos,
    RespostasSimulados,
    Materias
)
# Register your models here.
admin.site.register(Mentorias)
admin.site.register(ArquivosMentoria)
admin.site.register(ArquivosMentor)
admin.site.register(Turmas)
admin.site.register(Alunos)
admin.site.register(ArquivosAluno)
admin.site.register(Simulados)
admin.site.register(Gabaritos)
admin.site.register(RespostasSimulados)
admin.site.register(Materias)
