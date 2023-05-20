from django.urls import path

from .views import MentoriasView


app_name = 'mentorias'

urlpatterns = [
    path('', MentoriasView.as_view(), name='mentorias_home')
]
