from django.contrib import admin
from .models import (
    Programas,
    ArquivosPrograma,
    Turmas,
    Alunos,
    ArquivosAluno,
    Simulados,
    Gabaritos,
    RespostasSimulados,
    Materias
)
# Register your models here.
admin.site.register(Programas)
admin.site.register(ArquivosPrograma)
admin.site.register(Turmas)
admin.site.register(Alunos)
admin.site.register(ArquivosAluno)
admin.site.register(Simulados)
admin.site.register(Gabaritos)
admin.site.register(RespostasSimulados)
admin.site.register(Materias)
