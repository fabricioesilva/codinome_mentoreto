from django.contrib import admin
from .models import (
    Mentoria,
    ArquivosMentoria,
    Alunos,
    LoginAlunos,
    Simulados,
    Materias,
    MatriculaAlunoMentoria,
    LinksExternos,
    AplicacaoSimulado,
    RegistrosMentor,
    PreMatrículaAlunos,    
)

class MatriculaAlunoMentoriaAdmin(admin.ModelAdmin):
    list_display = ['pk', 'mentoria', 'aluno', 'ativa', 'criada_em', 'data_desativada' ]

# Register your models here.
admin.site.register(Mentoria)
admin.site.register(ArquivosMentoria)
admin.site.register(Alunos)
admin.site.register(Simulados)
admin.site.register(Materias)
admin.site.register(MatriculaAlunoMentoria, MatriculaAlunoMentoriaAdmin)
admin.site.register(LinksExternos)
admin.site.register(AplicacaoSimulado)
admin.site.register(RegistrosMentor)
admin.site.register(PreMatrículaAlunos)
admin.site.register(LoginAlunos)
