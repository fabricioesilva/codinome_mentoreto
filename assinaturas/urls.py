from django.urls import path
from .views import contratar_assinatura, faturas_mentor, fatura_detalhe, proxima_fatura, assinatura_detalhe, assinar_plano, termo_de_uso

app_name = 'assinaturas'

urlpatterns = [
    path('contratar/planos/', contratar_assinatura, name='contratar_assinatura'),  
    path('extrato/plano/', assinatura_detalhe, name="assinatura_detalhe"),
	path('faturas/', faturas_mentor, name='faturas_mentor'),    
    path('extrato/previsao/', proxima_fatura, name='proxima_fatura'),    
    path('extrato/detalhar/<int:pk>/', fatura_detalhe, name='fatura_detalhe'),
    path('assinar/', assinar_plano, name='assinar_plano'),
    path('assinar/termo_de_uso/', termo_de_uso, name='termo_de_uso'),
]