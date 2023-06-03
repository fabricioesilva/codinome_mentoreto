from django import forms
from django.utils.translation import gettext_lazy as _
from .models import (
    Mentorias, Alunos, Simulados, ArquivosMentor, Materias
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
    # data_aplicacao = forms.DateField(
    #     widget=forms.DateInput(
    #         attrs={'type': 'date'}
    #     )
    # )

    class Meta:
        model = Simulados
        fields = ['titulo',]


class CadastrarMateriaForm(forms.ModelForm):
    class Meta:
        model = Materias
        fields = ['titulo', 'peso']


class EnviarArquivoForm(forms.ModelForm):
    class Meta:
        model = ArquivosMentor
        fields = ['titulo_arquivo', 'arquivo_mentor']


class MatriculaAlunoMentoriaForm(forms.Form):
    def aluno_list(self):
        enviar_alunos = Alunos.objects.filter(
            mentor=self.mentor, situacao_aluno='at'
        ).all()
        return enviar_alunos

    encerra_em = forms.DateField(
        label=_('Data do encerramento da mentoria'),
        help_text=_("Inclua a data de encerramento se desejar."),
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    def __init__(self, mentor, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mentor = mentor
        self.fields['aluno'] = forms.ModelMultipleChoiceField(
            queryset=self.aluno_list(),
            label=_("Alunos"),
            widget=forms.SelectMultiple
        )


class ConfirmMentorPasswordForm(forms.Form):
    password = forms.CharField(
        label=_('Confirme a senha'),
        widget=forms.PasswordInput(attrs={'type': 'password'})
    )
