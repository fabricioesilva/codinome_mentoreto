from django.urls import path

from .views import (
    MentoriasView, criar_mentoria, detalhe_mentoria, alunos_mentor,
    simulados_mentor, arquivos_mentor, materias_mentor,
    cadastrar_aluno, cadastrar_simulado, enviar_arquivo,
    cadastrar_materia, aluno_detalhar, editar_aluno, aluno_matricular
)


app_name = 'mentorias'

urlpatterns = [
    path('', MentoriasView.as_view(), name='mentorias_home'),
    path('criar/', criar_mentoria, name='criar_mentoria'),
    path('mentorias/<int:pk>/', detalhe_mentoria, name='detalhar_mentoria'),
    path('alunos/<int:pk>/', aluno_detalhar, name="aluno_detalhar"),
    path('alunos/editar/<int:pk>/', editar_aluno, name="editar_aluno"),
    path('alunos/', alunos_mentor, name='alunos'),
    path('matricular/<int:pk>/', aluno_matricular, name="aluno_matricular"),
    path('simulados/', simulados_mentor, name='simulados'),
    path('arquivos/', arquivos_mentor, name='arquivos'),
    path('materias/', materias_mentor, name='materias'),
    path('alunos/cadastrar/', cadastrar_aluno, name='cadastrar_aluno'),
    path('simulados/cadastrar/', cadastrar_simulado, name='cadastrar_simulado'),
    path('arquivos/enviar/', enviar_arquivo, name='enviar_arquivo'),
    path('materias/cadastrar/', cadastrar_materia, name='cadastrar_materia'),

    # path('gabaritos/cadastrar/', cadastrar_gabarito, name='cadastrar_gabarito'),
    # path('gabaritos/', gabaritos_mentor, name='gabaritos'),
]
