from django.db import models
from usuarios.models import CustomUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
import os
from utils.resources import (
    PREPARO_CHOICES, PERFIL_PSICO, SITUACAO_ALUNO, QUESTAO_TIPO
)
# Create your models here.


def user_directory_path(instance, filename):
    ext = filename[-3:]
    import re
    variavel = str(timezone.now())[0:19]
    variavel = re.sub('\D', '', variavel)
    filename = f'{filename[:-4]}_{variavel}.{ext}'
    return f'user_{instance.mentor.id}/{filename}'


def aluno_directory_path(instance, filename):
    ext = filename[-3:]
    import re
    variavel = str(timezone.now())[0:19]
    variavel = re.sub('\D', '', variavel)
    filename = f'{filename[:-4]}_{variavel}.{ext}'
    return f'{instance.aluno.mentor.first_name}/{filename}'


def file_size(value):  # add this to some file where you can import it from
    limit = 2 * 1024 * 1024 * 1024 * 1024 * 1024
    if value.size > limit:
        raise ValidationError(_('Arquivo muito grande. Tamanho não pode exceder 5MB.'))


class Mentorias(models.Model):
    mentor = models.ForeignKey(CustomUser,
                               on_delete=models.CASCADE)
    titulo = models.CharField(
        max_length=100, verbose_name=_('Titulo da mentoria'),
        help_text=_('Insira um título para a mentoria.'),
        blank=False, null=False)
    criada_em = models.DateTimeField(_('Data criação:'), blank=True, null=True, default=timezone.now)
    controle = models.TextField(verbose_name=_('Anotações da mentoria'), null=True, blank=True, help_text=_(
        'Anotações da Mentoria para seu controle. Apenas você terá acesso a este conteúdo.'))
    arquivos_mentoria = models.ManyToManyField(
        'mentorias.ArquivosMentoria',
        help_text=_(
            'Arquivos de uma mentoria são arquivos disponíveis aos estudantes \
                que fizerem parte da mentoria.'), blank=True)
    etapas = models.JSONField(
        _("Etapas da mentoria"), null=True, blank=True)

    matriculas = models.ManyToManyField('mentorias.MatriculaAlunoMentoria',
                                        blank=True)
    simulados_mentoria = models.ManyToManyField('mentorias.Simulados', blank=True)
    links_externos = models.ManyToManyField('mentorias.LinksExternos', blank=True)

    def __str__(self):
        return self.titulo


class Alunos(models.Model):
    mentor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='mentor_alunos')
    student_user = models.ForeignKey(CustomUser, null=True, blank=True,
                                     on_delete=models.SET_NULL, related_name='student_alunos')
    nome_aluno = models.CharField(max_length=100,
                                  verbose_name=_('Nome do Aluno'), null=True, blank=True)
    email_aluno = models.EmailField(verbose_name=_('Email do Aluno'), help_text=_(
        'Este email precisa bater com o email utilizado pelo estudante para se cadastrar.'))
    telefone_aluno = models.CharField(verbose_name=_('Telefone do Aluno'),
                                      max_length=20, null=True, blank=True)

    situacao_aluno = models.CharField(
        max_length=2, verbose_name=_('Situação'),
        help_text=_('Se é aluno atual, ou ex-aluno.'),
        default='at', choices=SITUACAO_ALUNO)

    criado_em = models.DateTimeField(_('Data do cadastramento do aluno'),
                                     auto_now_add=True)
    controle = models.TextField(
        help_text=_(
            'Anote o que achar necessário para fins de controle do aluno. Aluno não tem acesso a este conteúdo.'),
        null=True, blank=True)
    nivel_preparo = models.PositiveSmallIntegerField(
        verbose_name=_('Nível de preparo para o objetivo final.'),
        null=True, blank=True, choices=PREPARO_CHOICES, default=1)
    perfil_psicológico = models.CharField(max_length=3, verbose_name=_('Perfil psicológico do aluno'),
                                          null=True, blank=True, choices=PERFIL_PSICO)
    arquivos_aluno = models.ManyToManyField(
        'mentorias.ArquivosAluno',
        help_text=_(
            'Arquivos de um Aluno são arquivos disponíveis ao estudante selecionado.'), blank=True)

    simulados_realizados = models.ManyToManyField(
        'mentorias.Simulados',
        help_text=_(
            'Simulados que os alunos devem fazer.'), blank=True)

    def save(self, *args, **kwargs):
        if not self.student_user or self.student_user.email != self.email_aluno:
            user = CustomUser.objects.filter(email=self.email_aluno).first()
            self.student_user = user
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.nome_aluno

    class Meta:
        ordering = ['nome_aluno', '-pk']


class MatriculaAlunoMentoria(models.Model):
    aluno = models.ForeignKey(Alunos, on_delete=models.CASCADE, null=True, blank=True)
    criada_em = models.DateField(_('Data da matrícula'), auto_now_add=True)
    encerra_em = models.DateField(_('Encerramento mentoria'), blank=True, null=True)

    class Meta:
        ordering = ['aluno',]


class Simulados(models.Model):
    mentor = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    mentor_name = models.CharField(max_length=50, null=True, blank=True)
    titulo = models.CharField(verbose_name=_('Título do simulado'), max_length=50)
    questao_tipo = models.SmallIntegerField(verbose_name=_('Tipo de questões'),
                                            choices=QUESTAO_TIPO, null=True, blank=True)
    criado_em = models.DateField(_('Criado'), auto_now_add=True)
    questao_qtd = models.PositiveSmallIntegerField(verbose_name=_(
        'Quantidade de questões no simulado'), null=True, blank=True)
    pontuacao = models.PositiveIntegerField(_('Pontuação máxima'), null=True)
    instrucao = models.TextField(verbose_name=_('Instruções ao aluno que fará o simulado'), help_text=_(
        'Se desejar, seus alunos poderão receber instruções para a realização do simulado.'), null=True, blank=True)
    data_aplicacao = models.DateField(verbose_name=_('Data prevista para aplicação'), default=timezone.now)
    arquivo_prova = models.FileField(upload_to=user_directory_path,
                                     verbose_name=_("Arquvio com a prova"),
                                     validators=[
                                         FileExtensionValidator(allowed_extensions=["pdf"]),
                                         file_size
                                     ]
                                     )
    controle = models.TextField(verbose_name=_('Anotações da mentoria'), null=True, blank=True, help_text=_(
        'Anotações da Mentoria para seu controle. Apenas você terá acesso a este conteúdo.'))
    gabarito = models.JSONField(
        _("Respostas do Gabarito"), null=True, blank=True)

    @property
    def filename(self):
        return os.path.basename(self.arquivo_prova.name)

    def __str__(self):
        return self.titulo

# Não utilizado, por enquanto. Gabarito enviado diretamente no models Simulado


class RespostasSimulados(models.Model):
    simulado = models.ForeignKey(Simulados, related_name='simulado_respondido', on_delete=models.SET_NULL, null=True)
    student_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL,
                                     null=True, blank=True)
    email_aluno = models.EmailField(_('Email do Aluno'), blank=True, null=True)
    mentor_nome = models.CharField(_('Criado por:'), max_length=50, null=True, blank=True)
    aluno_nome = models.CharField(_('Nome do aluno'), max_length=50, null=True, blank=True)
    respostas_alunos = models.JSONField(_('Respostas do Aluno'))

    def save(self, *args, **kwargs):
        if not self.mentor_nome or self.nome_mentor != self.simulado.mentor.first_name:
            self.mentor_nome = self.simulado.mentor.first_name
        if not self.aluno_nome or self.aluno_nome != self.student_user.first_name:
            self.aluno_nome = self.student_user.first_name
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.aluno_nome}, respondeu {self.simulado.titulo}'


class Materias(models.Model):
    mentor = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    titulo = models.CharField(_('Título da matéria'), max_length=50)
    criada_em = models.DateField(_('Criada em'), default=timezone.now)
    controle = models.TextField(verbose_name=_('Anotações da matéria'), null=True, blank=True, help_text=_(
        'Anotações da matéria para seu controle. Apenas você terá acesso a este conteúdo.'))
    peso = models.PositiveSmallIntegerField(_('Peso da matéria'), help_text=_(
        'Indique o peso da matéria para fins de cálculo de resultado final.'), default=1)

    def __str__(self):
        return self.titulo

    class Meta:
        ordering = ['titulo',]


class ArquivosMentoria(models.Model):
    mentoria = models.ForeignKey(Mentorias,
                                 on_delete=models.SET_NULL, null=True, blank=True)
    mentor = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    mentor_nome = models.CharField(_('Criado por:'), max_length=50, null=True, blank=True)
    titulo_arquivo = models.CharField(max_length=50, verbose_name=_('Nome do arquivo'), null=True)
    arquivo_mentoria = models.FileField(upload_to=user_directory_path,
                                        verbose_name=_("Arquvio mentoria"),
                                        help_text=_('Insira arquivo em .pdf de até 5MB de tamanho.'),
                                        validators=[
                                            FileExtensionValidator(allowed_extensions=["pdf"]),
                                            file_size
                                        ], null=True
                                        )

    def save(self, *args, **kwargs):
        if not self.mentor_nome or self.mentor.first_name != self.mentor_nome:
            self.mentor_nome = self.mentor.first_name
        return super().save(*args, **kwargs)

    @property
    def filename(self):
        return os.path.basename(self.arquivo_mentoria.name)

    def __str__(self):
        return self.filename


class ArquivosAluno(models.Model):
    mentor_nome = models.CharField(_('Criado por:'), max_length=50, null=True, blank=True)
    arquivo_aluno = models.FileField(upload_to=aluno_directory_path,
                                     verbose_name=_("Arquvio mentoria"),
                                     help_text=_('Insira arquivo em .pdf de até 5MB de tamanho.'),
                                     validators=[
                                         FileExtensionValidator(allowed_extensions=["pdf"]),
                                         file_size
                                     ], null=True
                                     )
    student_user = models.ForeignKey(CustomUser,
                                     on_delete=models.SET_NULL, null=True, blank=True)
    email_aluno = models.EmailField(_('Email do Aluno'), blank=True, null=True)
    aluno = models.ForeignKey(Alunos, verbose_name=_('Aluno'), on_delete=models.SET_NULL,
                              null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.mentor_nome or self.aluno.mentor.first_name != self.mentor_nome:
            self.mentor_nome = self.aluno.mentor.first_name
        if self.student_user:
            if not self.email_aluno or self.student_user.email != self.email_aluno:
                self.email_aluno = self.student_user.email
        elif self.aluno:
            if not self.email_aluno or self.aluno.email_aluno != self.email_aluno:
                self.email_aluno = self.aluno.email_aluno
        else:
            return super().save(*args, **kwargs)
        return super().save(*args, **kwargs)

    @property
    def filename(self):
        return os.path.basename(self.arquivo_aluno.name)

    def __str__(self):
        return self.filename


class LinksExternos(models.Model):
    titulo = models.CharField(_("Titulo do link"), max_length=50, blank=True, null=True)
    link_url = models.URLField(_('Link'), blank=True, null=True)
    descricao = models.CharField(
        _('Descrição'),
        help_text=_('Escreva uma breve descrição, caso você deseja comunicar-se com o aluno à respeito do link.'),
        max_length=100, null=True, blank=True)

    def __str__(self):
        return self.titulo

# class Questionarios(models.Model):
#     mentor = models.ForeignKey(CustomUser,
#                                on_delete=models.CASCADE)
#     titulo = models.CharField(
#         _("Título para o formulário"), max_length=50)
#     criada_em = models.DateTimeField(_("Data da criação"), auto_now_add=True)
#     perguntas = models.JSONField(_("Dados"), null=True)
#     numeracao = models.PositiveSmallIntegerField(
#         _("Numeração do questionário"), null=True, blank=True)
#     total_respostas = models.PositiveSmallIntegerField(_("Total de respostas"), default=0)
#     instrucao = models.TextField(_("Instrução ao usuário"), max_length=200, blank=True, null=True)

#     def __str__(self, *args, **kwargs):
#         return self.titulo


# class RespostasQuestionarios(models.Model):
#     questionario = models.ForeignKey(Questionarios, on_delete=models.CASCADE)
#     student_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL)
#     aluno_nome = models.CharField(max_length=50, null=True, blank=True)
#     respostas = models.JSONField(_("Respostas"), blank=True, null=True)

# class OutrasInfosTurmas(models.Model):
#     ...

# class Questoes(models.Model):
#     pass

"""


class ExpenseForm(forms.Form):
    CHOICES = (
        ('Debt', (
            (11, 'Credit Card'),
            (12, 'Student Loans'),
            (13, 'Taxes'),
        )),
        ('Entertainment', (
            (21, 'Books'),
            (22, 'Games'),
        )),
        ('Everyday', (
            (31, 'Groceries'),
            (32, 'Restaurants'),
        )),
    )
    amount = forms.DecimalField()
    date = forms.DateField()
    category = forms.ChoiceField(choices=CHOICES)


"""
