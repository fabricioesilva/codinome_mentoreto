from django.contrib import admin
from .models import (
    Mentorias,
    ArquivosMentor,
    ArquivosMentoria,
    Alunos,
    ArquivosAluno,
    Simulados,
    RespostasSimulados,
    Materias,
    MatriculaAlunoMentoria
)
# Register your models here.
admin.site.register(Mentorias)
admin.site.register(ArquivosMentoria)
admin.site.register(ArquivosMentor)
admin.site.register(Alunos)
admin.site.register(ArquivosAluno)
admin.site.register(Simulados)
admin.site.register(RespostasSimulados)
admin.site.register(Materias)
admin.site.register(MatriculaAlunoMentoria)
