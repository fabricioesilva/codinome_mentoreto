from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django_summernote.fields import SummernoteTextField
from django_summernote.widgets import SummernoteWidget
from .models import (
    Mentoria, Alunos, Simulados, Materias, LinksExternos
)


class CriarMentoriaForm(forms.ModelForm):
    encerra_em = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    class Meta:
        model = Mentoria
        fields = ['titulo', 'encerra_em', 'periodo_duracao']

    def clean(self):
        super(CriarMentoriaForm, self).clean()
        if self.cleaned_data.get('titulo'):
            titulo_exists = Mentoria.objects.filter(mentor=self.mentor, titulo=self.cleaned_data.get('titulo')).exists()
            if titulo_exists:
                error_message = 'Já existe mentoria com este mesmo titulo!'
                self.add_error('titulo', error_message)
        return self.cleaned_data
    
    def __init__(self, mentor, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mentor = mentor            

class CadastrarAlunoForm(forms.ModelForm):
    telefone_aluno = forms.CharField(
        label="Telefone do aluno",
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '(11) 98989999 '})
    )
    class Meta:
        model = Alunos
        fields = ['nome_aluno', 'email_aluno', 'telefone_aluno']

    def clean(self):
        super(CadastrarAlunoForm, self).clean()
        if self.cleaned_data.get('nome_aluno'):
            nome_aluno_enviado = self.cleaned_data.get('nome_aluno')
            nome_exists = Alunos.objects.filter(mentor=self.mentor, nome_aluno__iexact=nome_aluno_enviado)
            if nome_exists:
                if (self.instance.nome_aluno is None) or (nome_exists[0].pk != self.instance.pk):
                    error_message = 'Já existe aluno com este mesmo nome!'
                    self.add_error('nome_aluno', error_message)
        return self.cleaned_data
    
    def __init__(self, mentor, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mentor = mentor


class CadastrarSimuladoForm(forms.ModelForm):
    class Meta:
        model = Simulados
        fields = ['titulo',]

    def clean(self):
        super(CadastrarSimuladoForm, self).clean()
        if self.cleaned_data.get('titulo'):
            simulado_exists = Simulados.objects.filter(mentor=self.mentor, titulo=self.cleaned_data.get('titulo')).exists()
            if simulado_exists:
                error_message = 'Já existe simulado com este mesmo título!'
                self.add_error('titulo', error_message)
        return self.cleaned_data
    
    def __init__(self, mentor, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mentor = mentor

class CadastrarMateriaForm(forms.ModelForm):
    titulo = forms.CharField(
        label=_('Insira o título para a maatéria'),
        widget=forms.TextInput(attrs={"placeholder": 'Título'})
    )

    class Meta:
        model = Materias
        fields = ['titulo', 'peso']
        
    def clean(self):
        super(CadastrarMateriaForm, self).clean()
        if self.cleaned_data.get('titulo'):
            materia_exists = Materias.objects.filter(mentor=self.mentor, titulo=self.cleaned_data.get('titulo')).exists()
            if materia_exists:
                error_message = 'Já existe matéria com este mesmo título!'
                self.add_error('titulo', error_message)
        return self.cleaned_data
    
    def __init__(self, mentor, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mentor = mentor


class MatriculaAlunoMentoriaForm(forms.Form):
    def aluno_list(self):
        enviar_alunos = Alunos.objects.filter(
            mentor=self.mentor, situacao_aluno='at'
        ).all()
        for aluno in enviar_alunos:
            matricula = self.mentoria.matriculas_mentoria.filter(aluno=aluno, encerra_em__gte=timezone.now())
            if matricula:
                enviar_alunos = enviar_alunos.exclude(id=aluno.id)
        return enviar_alunos

    # encerra_em = forms.DateField(
    #     label=_('Data do encerramento da mentoria'),
    #     help_text=_("Inclua a data de encerramento se desejar."),
    #     widget=forms.DateInput(attrs={'type': 'date'})
    # )

    def __init__(self, mentoria, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mentoria = mentoria
        self.mentor = mentoria.mentor
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


class SummernoteFormSimple(forms.ModelForm):
    resumo_mentoria = SummernoteTextField()    
    class Meta:
        model = Mentoria
        fields = ['resumo_mentoria',]
        widgets = {
            'resumo_mentoria': SummernoteWidget(),
        #     'resumo_mentoria': SummernoteInplaceWidget(),
        }