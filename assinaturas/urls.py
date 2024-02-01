from django.urls import path
from .views import (
    oferta_detalhe, faturas_mentor, fatura_detalhe, proxima_fatura, assinatura_detalhe, 
    assinar_plano, termo_de_uso, historico_matriculas
)

app_name = 'assinaturas'

urlpatterns = [
    path('oferta/detalhe/', oferta_detalhe, name='oferta_detalhe'),  
    path('extrato/plano/', assinatura_detalhe, name="assinatura_detalhe"),
	path('faturas/', faturas_mentor, name='faturas_mentor'),    
    path('extrato/previsao/', proxima_fatura, name='proxima_fatura'),    
    path('extrato/detalhar/<int:pk>/', fatura_detalhe, name='fatura_detalhe'),
    path('assinar/termo_de_uso/', termo_de_uso, name='termo_de_uso'),
    path('assinar/', assinar_plano, name='assinar_plano'),
    path('historico/matriculas/', historico_matriculas , name='historico_matriculas'),
]