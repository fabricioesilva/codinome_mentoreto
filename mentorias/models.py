from django.db import models
from usuarios.models import CustomUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db.models.signals import pre_delete
from utils.resources import (
    PREPARO_CHOICES, PERFIL_PSICO, SITUACAO_ALUNO, QUESTAO_TIPO
)
# Create your models here.


def user_directory_path(instance, filename):
    import re
    variavel = str(timezone.now())[0:19]
    variavel = re.sub('\D', '', variavel)
    print(variavel)
    return 'user_{0}/{1}_{3}'.format(instance.user.id, filename, variavel)


def file_size(value):  # add this to some file where you can import it from
    limit = 2 * 1024 * 1024 * 1024 * 1024 * 1024
    if value.size > limit:
        raise ValidationError(_('Arquivo muito grande. Tamanho não pode exceder 5MB.'))


class Programas(models.Model):
    mentor = models.ForeignKey(CustomUser,
                               on_delete=models.CASCADE)
    titulo = models.CharField(
        max_length=100, verbose_name=_('Titulo do programa'),
        help_text=_('Insira um título para o programa.'),
        blank=False, null=False)
    created = models.DateTimeField(_('Data criação:'), blank=True, null=True, default=timezone.now)
    controle = models.TextField(verbose_name=_('Anotações do Programa'), null=True, blank=True, help_text=_(
        'Anotações do Programa para seu controle. Apenas você terá acesso a este conteúdo.'))
    arquivos_programa = models.ManyToManyField(
        'mentorias.ArquivosPrograma',
        help_text=_(
            'Arquivos de um Programa são arquivos disponíveis aos estudantes \
                que fizerem parte do Programa.'), blank=True)
    etapas = models.JSONField(
        _("Etapas do Programa"), null=True, blank=True)

    def __str__(self):
        return self.titulo


class ArquivosPrograma(models.Model):
    titulo_arquivo = models.CharField(max_length=50, verbose_name=_('Nome do arquivo'))
    arquivo = models.FileField(upload_to=user_directory_path,
                               verbose_name=_("Arquvio"), validators=[file_size])

    def __str__(self):
        return self.titulo_arquivo


class Turmas(models.Model):
    programa = models.ForeignKey(Programas,
                                 on_delete=models.SET_NULL, null=True, blank=True)
    mentor_name = models.CharField(max_length=100, null=True, blank=True)
    mentor_email = models.EmailField('Email do Mentor', blank=True, null=True)
    titulo = models.CharField(max_length=100, verbose_name=_('Título da Turma'),
                              blank=False, null=False)
    created = models.DateTimeField(_('Data criação:'), blank=True, null=True,
                                   default=timezone.now)
    descricao = models.CharField(
        max_length=100, verbose_name=_('Descrição do Programa'),
        null=True, blank=True,
        help_text=_('Inclua uma descrição resumida da Turma, que fica disponível para o estudante.'))
    controle = models.TextField(verbose_name=_('Anotações da Turma para seu controle.'),
                                null=True, blank=True, help_text=_(
        'Anote o que quiser neste espaço. Apenas você terá acesso a este conteúdo.'))
    termino_turma = models.DateField(verbose_name=_('Data do término'),
                                     help_text=_('Data do término do estudo com esta turma.'),
                                     blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.mentor_name:
            self.mentor_name = self.programa.mentor.first_name
        if not self.mentor_email:
            self.mentor_email = self.programa.mentor.email
        super().save(*args, **kwargs)


class Alunos(models.Model):
    mentor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='mentor_alunos')
    turma_matriculada = models.ManyToManyField(Turmas,
                                               verbose_name=_('Turma matriculada'))
    student_user = models.ForeignKey(CustomUser, null=True, blank=True,
                                     on_delete=models.SET_NULL, related_name='student_alunos')
    nome_aluno = models.CharField(max_length=100,
                                  verbose_name=_('Nome do Aluno'),
                                  null=True, blank=True)
    email_aluno = models.EmailField(verbose_name=_('Email do Aluno'), help_text=_(
        'Este email precisa bater com o email utilizado pelo estudante para se cadastrar.'), null=True, blank=True)
    telefone_aluno = models.CharField(verbose_name=_('Telefone do Aluno'),
                                      max_length=20, null=True, blank=True)
    situacao_matricula = models.CharField(
        max_length=2, verbose_name=_('Matrícula ativa ou inativa, ou pagamento atrasado'),
        help_text=_('Se é aluno atual, ou ex-aluno. E se está em dia, ou não.'),
        default='ok', choices=SITUACAO_ALUNO)
    data_cadastro = models.DateTimeField(_('Data do cadastramento do aluno'),
                                         auto_now_add=True)
    controle = models.TextField(
        help_text=_(
            'Anote o que achar necessário para fins de controle do aluno. Aluno não tem acesso a este conteúdo.'),
        null=True, blank=True)
    nivel_preparo = models.PositiveSmallIntegerField(verbose_name=_('Nível de preparo para o objetivo final.'),
                                                     null=True, blank=True, choices=PREPARO_CHOICES)
    perfil_psicológico = models.CharField(max_length=3, verbose_name=_('Perfil psicológico do aluno'),
                                          null=True, blank=True, choices=PERFIL_PSICO)
    arquivos_aluno = models.ManyToManyField(
        'mentorias.ArquivosAluno',
        help_text=_(
            'Arquivos de um Aluno são arquivos disponíveis ao estudante selecionado.'))

    simulados_realizados = models.ManyToManyField(
        'mentorias.Simulados',
        help_text=_(
            'Simulados que os alunos devem fazer.'))

    def save(self, *args, **kwargs):
        if not self.student_user or self.student_user.email != self.student_user:
            user = CustomUser.objects.get(email=self.email_aluno)
            self.student_user = user
        return super().save(*args, **kwargs)


class ArquivosAluno(models.Model):
    titulo_arquivo = models.CharField(max_length=50, verbose_name=_('Nome do arquivo'))
    arquivo = models.FileField(upload_to=user_directory_path,
                               verbose_name=_("Arquivo"), validators=[file_size])

    def __str__(self):
        return self.titulo_arquivo


class Simulados(models.Model):
    mentor = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    mentor_name = models.CharField(max_length=50, null=True, blank=True)
    titulo = models.CharField(verbose_name=_('Título do simulado'), max_length=50)
    questao_tipo = models.SmallIntegerField(verbose_name=_('Tipo de questões'),
                                            choices=QUESTAO_TIPO)
    questao_qtd = models.PositiveSmallIntegerField(verbose_name=_('Quantidade de questões no simulado'))
    instrucao = models.TextField(verbose_name=_('Instruções ao aluno que fará o simulado'), null=True, blank=True)
    data_aplicacao = models.DateTimeField(verbose_name=_('Data da liberação'), default=timezone.now)
    arquivo_prova = models.FileField(upload_to=user_directory_path,
                                     verbose_name=_("Arquvio com a prova"),
                                     validators=[
                                         FileExtensionValidator(allowed_extensions=["pdf"]),
                                         file_size
                                     ]
                                     )
    gabarito = models.OneToOneField('mentorias.Gabaritos', null=True, blank=True,
                                    verbose_name=_('Gabarito do Simulado'),
                                    on_delete=models.SET_NULL)


class Gabaritos(models.Model):
    titulo = models.CharField(_('Título do Gabarito'), max_length=50)
    questao_qtd = models.PositiveSmallIntegerField('Quantidade de questões', null=True, blank=True)
    respostas_gabarito = models.JSONField(
        _("Respostas do Gabarito"))


class RespostasSimulados(models.Model):
    simulado = models.ForeignKey(Simulados, on_delete=models.SET_NULL, null=True)
    student_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL,
                                     null=True, blank=True)
    mentor_nome = models.CharField(_('Criado por:'), max_length=50, null=True, blank=True)
    aluno_nome = models.CharField(_('Nome do aluno'), max_length=50, null=True, blank=True)
    respostas_alunos = models.JSONField(_('Respostas do Aluno'))

    def save(self, *args, **kwargs):
        if not self.mentor_nome or self.nome_mentor != self.simulado.mentor.first_name:
            self.mentor_nome = self.simulado.mentor.first_name
        if not self.aluno_nome or self.aluno_nome != self.student_user.first_name:
            self.aluno_nome = self.student_user.first_name
        return super().save(*args, **kwargs)


class Materias(models.Model):
    mentor = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    titulo = models.CharField(_('Título da matéria'), max_length=50)
    peso = models.PositiveSmallIntegerField(_('Peso da matéria'), help_text=_(
        'Indique o peso da matéria para fins de cálculo de resultado final.'), default=1)


# class Questionarios(models.Model):
#     mentor = models.ForeignKey(CustomUser,
#                                on_delete=models.CASCADE)
#     titulo = models.CharField(
#         _("Título para o formulário"), max_length=50)
#     created_at = models.DateTimeField(_("Data da criação"), auto_now_add=True)
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
