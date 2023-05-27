from django.urls import path

from .views import (
    MentoriasView, criar_mentoria, detalhe_mentoria, alunos_mentor,
    simulados_mentor, arquivos_mentor, gabaritos_mentor, materias_mentor,
    cadastrar_aluno, cadastrar_simulado, cadastrar_gabarito, enviar_arquivo,
    cadastrar_materia, alunos_detalhar
)


app_name = 'mentorias'

urlpatterns = [
    path('', MentoriasView.as_view(), name='mentorias_home'),
    path('criar/', criar_mentoria, name='criar_mentoria'),
    path('mentorias/<int:pk>/', detalhe_mentoria, name='detalhar_mentoria'),
    path('alunos/<int:pk>/', alunos_detalhar, name="detalhar_alunos"),
    path('alunos/', alunos_mentor, name='alunos'),
    path('simulados/', simulados_mentor, name='simulados'),
    path('gabaritos/', gabaritos_mentor, name='gabaritos'),
    path('arquivos/', arquivos_mentor, name='arquivos'),
    path('materias/', materias_mentor, name='materias'),
    path('alunos/cadastrar/', cadastrar_aluno, name='cadastrar_aluno'),
    path('simulados/cadastrar/', cadastrar_simulado, name='cadastrar_simulado'),
    path('gabaritos/cadastrar/', cadastrar_gabarito, name='cadastrar_gabarito'),
    path('arquivos/enviar/', enviar_arquivo, name='enviar_arquivo'),
    path('materias/cadastrar/', cadastrar_materia, name='cadastrar_materia'),
]
