from django.urls import path
from .views import HomeView

app_name = 'usuarios'

urlpatterns = [
    path('',
         HomeView.as_view(), name='home'),
]
