from django import forms
from .models import (
    Mentorias, Alunos, Simulados, Gabaritos, ArquivosMentor, Materias
)


class CriarMentoriaForm(forms.ModelForm):
    class Meta:
        model = Mentorias
        fields = ['titulo', 'controle']


class CadastrarAlunoForm(forms.ModelForm):
    class Meta:
        model = Alunos
        fields = ['nome_aluno', 'email_aluno', 'telefone_aluno', 'controle']


class CadastrarSimuladoForm(forms.ModelForm):
    data_aplicacao = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'date'}
        )
    )

    class Meta:
        model = Simulados
        fields = ['titulo', 'questao_tipo', 'questao_qtd', 'instrucao']


class CadastrarGabaritoForm(forms.ModelForm):
    class Meta:
        model = Gabaritos
        fields = ['titulo', 'questao_qtd', 'respostas_gabarito']


class CadastrarMateriaForm(forms.ModelForm):
    class Meta:
        model = Materias
        fields = ['titulo', 'peso']


class EnviarArquivoForm(forms.ModelForm):
    class Meta:
        model = ArquivosMentor
        fields = ['titulo_arquivo', 'arquivo_mentor']
