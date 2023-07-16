from django import forms
from django.utils.translation import gettext_lazy as _
from .models import (
    Mentoria, Alunos, Simulados, Materias, LinksExternos, AplicacaoSimulado
)


class CriarMentoriaForm(forms.ModelForm):
    class Meta:
        model = Mentoria
        fields = ['titulo', 'resumo_mentoria']


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


# class AplicacaoSimuladoForm(forms.Form):

#     def __init__(self, mentoria, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.mentoria = mentoria
#         queryset = Alunos.objects.filter(mentor=mentoria.mentor, situacao_aluno='at')
#         alunos = []
#         for aluno in queryset:
#             alunos.append(
#                 (aluno.pk,
#                  f'Nome: {aluno.nome_aluno}. Simulados aplicados neste aluno: {AplicacaoSimulado.objects.filter(simulado__in=mentoria.simulados_mentoria.all()).filter(aluno=aluno).count()}.'))
#         self.fields['aluno'] = forms.MultipleChoiceField(
#             label=_("Alunos"),
#             choices=alunos,
#             widget=forms.CheckboxSelectMultiple()
#         )
#         self.fields['aplicacao_agendada'] = forms.DateTimeField(
#             label=_('Data da aplicação.'),
#             help_text=_(
#                 'Escolha uma data e hora futura para agendar a aplicação. Ou informe dia e hora atuais para aplicação imediata.'),
#             widget=forms.DateTimeInput)
#         simulados = Simulados.objects.filter(mentor=mentoria.mentor)
#         simulados_choices = []
#         for simulado in simulados:
#             simulados_choices.append(
#                 (simulado.pk, simulado.titulo)
#             )
