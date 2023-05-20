from django.urls import path
from .views import (
    HomeView,
    CadastroView,
    index_view,
    check_user_email,
    EditProfileView,
    edit_user_email,
    ProfileView,
    EditPreferencesView,
    change_password_method
)

app_name = 'usuarios'

urlpatterns = [
    path('', index_view, name='index'),
    path('usuario/',
         HomeView.as_view(), name='home'),
    path('cadastro/', CadastroView.as_view(), name='cadastro'),
    path('check/email/<str:uri_key>/', check_user_email,
         name='check_user_email'),
    path('usuario/<str:slug>/editar/', EditProfileView.as_view(), name='edit_profile'),
    path('usuario/editar/email/', edit_user_email, name="edit_user_email"),
    path('usuario/editar/preferencias/<int:pk>/', EditPreferencesView.as_view(), name="edit_preferences"),
    path('usuario/editar/password/', change_password_method, name="change_password"),
    path('usuario/profile/', ProfileView.as_view(), name="profile_view")
]
