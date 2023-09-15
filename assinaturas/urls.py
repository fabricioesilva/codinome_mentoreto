from django.urls import path
from .views import contratar_assinatura, faturas_mentor, fatura_detalhe, proxima_fatura, assinatura_detalhe

app_name = 'assinaturas'

urlpatterns = [
    path('assinatura/extrato/planos/', contratar_assinatura, name='contratar_assinatura'),  
    path('assinaturas/mentor/plano/', assinatura_detalhe, name="assinatura_detalhe"),
	path('assinatura/extrato/', faturas_mentor, name='faturas_mentor'),    
    path('assinatura/extrato/previsao/', proxima_fatura, name='proxima_fatura'),    
    path('assinatura/extrato/detalhar/<int:pk>/', fatura_detalhe, name='fatura_detalhe'),
]