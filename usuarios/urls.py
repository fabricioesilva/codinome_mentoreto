from django.urls import path
from .views import HomeView, CadastroView, index_view, check_user_email

app_name = 'usuarios'

urlpatterns = [
    path('', index_view, name='index'),
    path('usuario/',
         HomeView.as_view(), name='home'),
    path('cadastro', CadastroView.as_view(), name='cadastro'),
    path('check/email/<str:uri_key>', check_user_email,
         name='check_user_email'),
]
