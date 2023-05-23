from django import forms
from .models import Programas


class CriarProgramasForm(forms.ModelForm):
    class Meta:
        model = Programas
        fields = ['titulo', 'controle']
