from django.urls import path
from .views import assinaturas_mentor, extrato_mentor

app_name = 'assinaturas'

urlpatterns = [
    path('assinaturas/mentor/', assinaturas_mentor, name="assinaturas_mentor"),
	path('assinatura/extrato/', extrato_mentor, name='extrato_mentor'),    
]