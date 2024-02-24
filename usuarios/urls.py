from django.urls import path
from .views import (
    home_view,
    HomeMentorView,    
    CadastroView,
    index_view,
    check_user_email,
    EditProfileView,
    edit_user_email,
    ProfileView,
    EditPreferencesView,
    change_password_method,
    delete_user,
    buscar_geral,
    simulacao_precos
)
from mentorias.views import login_alunos, cadastrar_pre_matricular
from politicas.views import fazer_contato

app_name = 'usuarios'

urlpatterns = [
    path('', index_view, name='index'),
    # path('home/',
    #      home_view, name='home'),
    # path('usuario/estudante/', HomeStudentView.as_view(), name="home_student"),
    path('usuario/mentor/', HomeMentorView.as_view(), name="home_mentor"),
    path('cadastro/', CadastroView.as_view(), name='cadastro'),
    path('check/email/<str:uri_key>/', check_user_email,
         name='check_user_email'),
    path('usuario/<str:slug>/editar/', EditProfileView.as_view(), name='edit_profile'),
    path('usuario/editar/email/', edit_user_email, name="edit_user_email"),
    path('usuario/editar/preferencias/<int:pk>/', EditPreferencesView.as_view(), name="edit_preferences"),
    path('usuario/editar/password/', change_password_method, name="change_password"),
    path('usuario/profile/', ProfileView.as_view(), name="profile_view"),
    path('delete/<str:username>/', delete_user, name='remove_account'),
    path('busca/resultados/', buscar_geral, name="buscar_geral"),
    path('aluno/login/', login_alunos, name="login_alunos"),
    path('prematricula/<int:pk>/', cadastrar_pre_matricular, name="cadastrar_pre_matricular"),
    path('contato/', fazer_contato, name="contato"),
    path('simulacao/', simulacao_precos, name="simulacao_precos"),
    
]
