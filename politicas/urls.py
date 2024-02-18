from django.urls import path
from .views import show_policy, about_us

urlpatterns = [
    path('', about_us, name='about'),
    path('conteudo/', show_policy, name='show_policy'),
]
