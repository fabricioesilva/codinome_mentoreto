from django.urls import path

from .views import MentoriasView, criar_programa, detalhe_mentoria


app_name = 'mentorias'

urlpatterns = [
    path('', MentoriasView.as_view(), name='mentorias_home'),
    path('criar/', criar_programa, name='criar_programa'),
    path('detalhar/<int:pk>/', detalhe_mentoria, name='detalhar_mentoria'),
]
