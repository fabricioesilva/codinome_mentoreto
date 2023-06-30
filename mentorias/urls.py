from django.urls import path

from .views import (
    MentoriasView, criar_mentoria, mentoria_detalhe, alunos_mentor, simulados_mentor, materias_mentor, cadastrar_aluno,
    cadastrar_simulado, cadastrar_materia, aluno_detalhe, editar_aluno, aluno_matricular, simulados_aplicados,
    mentoria_apagar, simulado_detalhe, materia_detalhe, cadastrar_gabarito, links_externos, aplicar_simulado,
    aluno_anonimo_aplicacao, matricula_detalhe, resultado_detalhe
)


app_name = 'mentorias'

urlpatterns = [
    path('mentorias/', MentoriasView.as_view(), name='mentorias_mentor'),
    path('criar/', criar_mentoria, name='criar_mentoria'),
    path('mentorias/<int:pk>/', mentoria_detalhe, name='mentoria_detalhe'),
    path('matriculas/detalhe/<int:pk>/', matricula_detalhe, name='matricula_detalhe'),
    path('alunos/<int:pk>/', aluno_detalhe, name="aluno_detalhe"),
    path('alunos/editar/<int:pk>/', editar_aluno, name="editar_aluno"),
    path('alunos/', alunos_mentor, name='alunos'),
    path('links/<int:pk>/', links_externos, name="links_externos"),
    path('matricular/<int:pk>/', aluno_matricular, name="aluno_matricular"),
    path('apagar/<int:pk>/', mentoria_apagar, name='mentoria_apagar'),
    path('simulados/', simulados_mentor, name='simulados'),
    path('simulados/aplicar/<int:pk>/', aplicar_simulado, name="aplicar_simulado"),
    path('simulados/aplicados/<int:pk>/', simulados_aplicados, name='simulados_aplicados'),
    path('matriculas/simulado/resultado/<int:pk>/', resultado_detalhe, name='resultado_detalhe'),
    path('materias/', materias_mentor, name='materias'),
    path('materias/<int:pk>/', materia_detalhe, name="materia_detalhe"),
    path('alunos/cadastrar/', cadastrar_aluno, name='cadastrar_aluno'),
    path('simulados/cadastrar/', cadastrar_simulado, name='cadastrar_simulado'),
    path('simulados/<int:pk>/', simulado_detalhe, name="simulado_detalhe"),
    path('simulados/<int:pk>/gabarito/cadastrar/', cadastrar_gabarito, name="cadastrar_gabarito"),
    path('simulados/respostas/<int:pk>/', aluno_anonimo_aplicacao, name='aluno_anonimo_aplicacao'),
    path('materias/cadastrar/', cadastrar_materia, name='cadastrar_materia'),
]
