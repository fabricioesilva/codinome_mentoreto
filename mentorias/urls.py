from django.urls import path

from .views import (
	MentoriasView, criar_mentoria, mentoria_detalhe, alunos_mentor, simulados_mentor, materias_mentor, 
    cadastrar_aluno, login_alunos, aluno_matriculas, editar_dados_acesso_aluno_login, alterar_senha_aluno_login,
	cadastrar_simulado, cadastrar_materia, aluno_detalhe, editar_aluno, aluno_matricular, simulados_aplicados,
	mentoria_apagar, simulado_detalhe, materia_detalhe, cadastrar_gabarito, links_externos, aplicar_simulado,
	aluno_login_aplicacao, matricula_detalhe, desempenho_matricula, resultado_detalhe, aplicacao_individual, 
	cadastrar_pre_matricular, matricula_aluno_login, tratamento_pre_matricula, aluno_esqueceu_senha, 
    aceitacao_termo_de_uso, alunos_sair_sessao, LineChartMentoriaView, LineChartMatriculaaView, 
    LineChartSimuladoaView, BarChartAplicacaoView
)


app_name = 'mentorias'

urlpatterns = [
	path('mentorias/', MentoriasView.as_view(), name='mentorias_mentor'),
	path('criar/', criar_mentoria, name='criar_mentoria'),
	path('mentorias/<int:pk>/', mentoria_detalhe, name='mentoria_detalhe'),
	path('matriculas/detalhe/<int:pk>/', matricula_detalhe, name='matricula_detalhe'),
	path('matriculas/desempenho/<int:pk>/', desempenho_matricula, name='desempenho_matricula'),
	path('alunos/<int:pk>/', aluno_detalhe, name="aluno_detalhe"),
	path('alunos/editar/<int:pk>/', editar_aluno, name="editar_aluno"),
	path('alunos/', alunos_mentor, name='alunos'),
	path('alunos/login/', login_alunos, name='login_alunos'),
	path('alunos/dados/editar/<int:pk>/', editar_dados_acesso_aluno_login, name='editar_dados_acesso_aluno_login'),
	path('alunos/matriculas/<int:pk>/', aluno_matriculas, name='aluno_matriculas'),
	path('alunos/senha/alterar/<int:pk>/', alterar_senha_aluno_login, name='alterar_senha_aluno_login'),
	path('alunos/senha/redefinir/', aluno_esqueceu_senha, name='aluno_esqueceu_senha'),
    path('alunos/sair/sessao/', alunos_sair_sessao, name='alunos_sair_sessao'),
    path('alunos/termodeuso/<int:pk>/', aceitacao_termo_de_uso, name='aceitacao_termo_de_uso'),    
	path('links/<int:pk>/', links_externos, name="links_externos"),
	path('matricular/<int:pk>/', aluno_matricular, name="aluno_matricular"),
	path('apagar/<int:pk>/', mentoria_apagar, name='mentoria_apagar'),
	path('simulados/', simulados_mentor, name='simulados'),
	path('simulados/aplicar/<int:pk>/', aplicar_simulado, name="aplicar_simulado"),
	path('simulados/aplicados/<int:pk>/', simulados_aplicados, name='simulados_aplicados'),
	path('simulados/aplicar/individual/<int:pk>/', aplicacao_individual, name='aplicacao_individual'),
	path('matriculas/simulado/resultado/<int:pk>/', resultado_detalhe, name='resultado_detalhe'),
	path('matricula/versao/aluno/<int:pk>/', matricula_aluno_login, name="matricula_aluno_login"),
	path('materias/', materias_mentor, name='materias'),
	path('materias/<int:pk>/', materia_detalhe, name="materia_detalhe"),
	path('alunos/cadastrar/', cadastrar_aluno, name='cadastrar_aluno'),
	path('mentoria/aluno/prematricular/<int:pk>/', cadastrar_pre_matricular, name='cadastrar_pre_matricular'),
	path('simulados/cadastrar/', cadastrar_simulado, name='cadastrar_simulado'),
	path('simulados/<int:pk>/', simulado_detalhe, name="simulado_detalhe"),
	path('simulados/<int:pk>/gabarito/cadastrar/', cadastrar_gabarito, name="cadastrar_gabarito"),
	path('simulados/respostas/<int:pk>/', aluno_login_aplicacao, name='aluno_login_aplicacao'),
	path('materias/cadastrar/', cadastrar_materia, name='cadastrar_materia'),
    path('chartJS/mentoria/<int:pk>/', LineChartMentoriaView.as_view(), name='line_chart_mentoria'),
    path('chartJS/matricula/<int:pk>/', LineChartMatriculaaView.as_view(), name='line_chart_matricula'),        
	path('chartJS/simulado/<int:pk>/', LineChartSimuladoaView.as_view(), name='line_chart_simulado'),        
	path('chartJS/aplicacao/<int:pk>/', BarChartAplicacaoView.as_view(), name='bar_chart_aplicacao'),   
    path('mentoria/prematricula/tratamento/', tratamento_pre_matricula, name='tratamento_pre_matricula'),
         
]
