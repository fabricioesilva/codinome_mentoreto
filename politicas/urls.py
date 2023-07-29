from django.urls import path
from .views import show_policy, about_us, fazer_contato

urlpatterns = [
    path('', about_us, name='about'),
    path('conteudo/', show_policy, name='show_policy'),
    path('contato/', fazer_contato, name='contato'),
]
