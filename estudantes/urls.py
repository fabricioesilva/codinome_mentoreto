from django.urls import path
from .views import estudante_login

app_name = 'estudantes'

urlpatterns = [
    path('login/', estudante_login, name="estudante_login"),
]