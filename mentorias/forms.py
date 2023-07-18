from django import forms
from django.utils.translation import gettext_lazy as _
from .models import (
    Mentoria, Alunos, Simulados, Materias, LinksExternos
)


class CriarMentoriaForm(forms.ModelForm):
    class Meta:
        model = Mentoria
        fields = ['titulo', 'resumo_mentoria']


class CadastrarAlunoForm(forms.ModelForm):
    class Meta:
        model = Alunos
        fields = ['nome_aluno', 'email_aluno', 'telefone_aluno']


class CadastrarSimuladoForm(forms.ModelForm):
    class Meta:
        model = Simulados
        fields = ['titulo',]


class CadastrarMateriaForm(forms.ModelForm):
    class Meta:
        model = Materias
        fields = ['titulo', 'peso']


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


class LinksExternosForm(forms.ModelForm):
    link_url = forms.URLField(
        label=_('Insira aqui o link.'),
        required=True,
        widget=forms.URLInput(attrs={'type': 'url'})
    )

    class Meta:
        model = LinksExternos
        fields = '__all__'
