from django.urls import path
from .views import assinaturas_mentor

app_name = 'assinaturas'

urlpatterns = [
    path('assinaturas/mentor/', assinaturas_mentor, name="assinaturas_mentor"),
]