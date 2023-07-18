from django.db import models
from usuarios.models import CustomUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import date
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
# from django.db.models.signals import pre_save, post_delete
from django.conf import settings
import os
# import random
import string
import re
from secrets import SystemRandom as SR

from utils.resources import (
    PREPARO_CHOICES, PERFIL_PSICO, SITUACAO_ALUNO, QUESTAO_TIPO
)
# Create your models here.


def user_directory_path(instance, filename):
    ext = filename[-3:]
    variavel = str(timezone.now())[0:19]
    variavel = re.sub('\D', '', variavel)
    filename = f'{filename[:-4]}_{variavel}.{ext}'
    if instance.__class__.__name__ == 'Simulados':
        nome_arquivo = f'simulado_{instance.mentor.username}_{instance.titulo}.{ext}'
        nome_arquivo = nome_arquivo.replace(' ', '_')
        file_path = f'media/usuarios/user_{instance.mentor.id}/{nome_arquivo}'
        if os.path.exists(os.path.join(settings.BASE_DIR, file_path)):
            os.remove(file_path)
        return f'usuarios/user_{instance.mentor.id}/{nome_arquivo}'
    return f'usuarios/user_{instance.mentor.id}/{filename}'


def aluno_directory_path(instance, filename):
    ext = filename[-3:]
    import re
    variavel = str(timezone.now())[0:19]
    variavel = re.sub('\D', '', variavel)
    filename = f'{filename[:-4]}_{variavel}.{ext}'
    return f'usuarios/user_{instance.mentor.id}/{filename}'


def file_size(value):  # add this to some file where you can import it from
    limit = 2 * 1024 * 1024 * 1024 * 1024 * 1024
    if value.size > limit:
        raise ValidationError(_('Arquivo muito grande. Tamanho não pode exceder 5MB.'))


def get_random_string():
    # Gera senha de acesso do aluno ao simulado.
    letters = string.ascii_lowercase
    print('PASsosoooooo')
    # result_str = ''.join(random.choice(letters) for i in range(6))
    result_str = ''.join(SR().choices(string.ascii_letters + string.digits + string.punctuation, k=8))
    return result_str


class Mentoria(models.Model):
    mentor = models.ForeignKey(CustomUser,
                               on_delete=models.SET_NULL, null=True, blank=True)
    titulo = models.CharField(
        max_length=100, verbose_name=_('Titulo da mentoria'),
        help_text=_('Insira um título para a mentoria.'),
        blank=False, null=False)
    criada_em = models.DateTimeField(_('Data criação:'), blank=True, null=True, default=timezone.now)
    controle = models.TextField(verbose_name=_('Anotações da mentoria'), null=True, blank=True, help_text=_(
        'Anotações da Mentoria para seu controle. Apenas você terá acesso a este conteúdo.'))
    resumo_mentoria = models.TextField(
        _('Apresentação da mentoria'),
        help_text=_('Se desejar, escreva um texto de apresentação desta mentoria ao estudante.'),
        max_length=300, null=True, blank=True)
    arquivos_da_mentoria = models.ManyToManyField(
            'mentorias.ArquivosMentoria',
            related_name="arquivos_da_mentoria",
            help_text=_(
                    'Arquivos de uma mentoria são arquivos disponíveis aos estudantes \
				que fizerem parte da mentoria.'), blank=True)
    etapas = models.JSONField(
        _("Etapas da mentoria"), null=True, blank=True)
    ativa = models.BooleanField(_('Ativa'), default=True)

    matriculas = models.ManyToManyField('mentorias.MatriculaAlunoMentoria',
                                        blank=True)
    simulados_mentoria = models.ManyToManyField('mentorias.AplicacaoSimulado', blank=True)
    links_externos = models.ManyToManyField('mentorias.LinksExternos', blank=True)
    username_mentor = models.CharField('Username do Mentor', max_length=50, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.username_mentor:
            self.username_mentor = self.mentor.username
        return super().save(*args, **kwargs)

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
    estatisticas = models.JSONField('Estatísticas', null=True, blank=True)
    senha_do_aluno = models.CharField(
        _('Senha para acesso'),
        default=get_random_string, max_length=8, null=True, blank=True)

    class Meta:
        ordering = ['aluno',]

    @property
    def falta_responder(self):
        falta_responder = 0
        for aplicacao in self.aplicacoes_matricula.all():
            if not aplicacao.data_resposta:
                falta_responder += 1
        return falta_responder


class Simulados(models.Model):
    mentor = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    mentor_name = models.CharField(max_length=50, null=True, blank=True)
    mentor_username = models.CharField(max_length=50, null=True, blank=True)
    titulo = models.CharField(verbose_name=_('Título do simulado'), max_length=100)
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

    def save(self, *args, **kwargs):
        if not self.mentor_name:
            self.mentor_username = self.mentor.username
        return super().save(*args, **kwargs)


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
    mentoria = models.ForeignKey(Mentoria,
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


class AplicacaoSimulado(models.Model):
    aluno = models.ForeignKey('mentorias.Alunos', related_name='aplicacao_aluno',
                              blank=True, null=True, on_delete=models.SET_NULL)
    simulado = models.ForeignKey('mentorias.Simulados', related_name='aplicacao_simulado',
                                 blank=True, null=True, on_delete=models.SET_NULL)
    simulado_titulo = models.CharField('Titulo do simulado', max_length=100, null=True, blank=True)
    resposta_alunos = models.JSONField(_('Resposta do Aluno'), null=True, blank=True)
    criada_em = models.DateField(_('Data'), default=date.today)
    data_resposta = models.DateField(_('Data da resposta'), null=True, blank=True)
    aplicacao_agendada = models.DateTimeField(_('Agendar'), default=timezone.now)
    senha_do_aluno = models.CharField(
        _('Senha para acesso'),
        default=get_random_string, max_length=8, null=True, blank=True)
    matricula = models.ForeignKey(
        'mentorias.MatriculaAlunoMentoria', related_name='aplicacoes_matricula', null=True, blank=True,
        on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.id}/{self.simulado.titulo}/{self.aluno}/{self.matricula}'

    def save(self, *args, **kwargs):
        if not self.simulado_titulo:
            self.simulado_titulo = self.simulado.titulo
        return super().save(*args, **kwargs)

    class Meta:
        unique_together = ['aluno', 'simulado']
        ordering = ['-criada_em']


class PlanosAssinatura(models.Model):
    criado_por = models.ForeignKey(
        CustomUser, verbose_name=_('Criado por'),
        null=True, blank=True, on_delete=models.SET_NULL)
    titulo = models.CharField(_('Nome comercial'), max_length=100)
    descricao = models.TextField(_('Descrição'), null=True, blank=True)
    criado_em = models.DateTimeField(_('Criado em'), default=timezone.now)
    criado_por_pk = models.PositiveIntegerField(null=True, blank=True)
    criado_por_email = models.EmailField(null=True, blank=True)
    criado_por_nome = models.CharField(max_length=50, null=True, blank=True)
    ativo = models.BooleanField(_('Em uso'), default=False)
    preco = models.FloatField()
    desconto = models.ManyToManyField('mentorias.Descontos')

    def save(self, *args, **kwargs):
        if not self.criado_por_pk:
            self.criado_por_pk = self.criado_por.pk
        if not self.criado_por_email:
            self.criado_por_email = self.criado_por.email
        if not self.criado_por_nome:
            self.criado_por_nome = self.criado_por.first_name
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo


class AssinaturasMentor(models.Model):
    usuario = models.ForeignKey(CustomUser, verbose_name=_('Usuário'), null=True, blank=True, on_delete=models.SET_NULL)
    plano = models.ForeignKey(
        PlanosAssinatura, verbose_name=_('Plano de assinatura'),
        on_delete=models.SET_NULL, null=True, blank=True)
    criada_em = models.DateTimeField(_('Data assinatura'), default=timezone.now)
    encerra_em = models.DateField(_('Encerra em'), null=True, blank=True)
    pagamento = models.JSONField(_("Controle de pagamentos"), null=True, blank=True)
    usuario_pk = models.PositiveIntegerField(_("Id do usuário"), null=True, blank=True)
    usuario_email = models.EmailField(_('Email do usuário'), null=True, blank=True)
    usuario_nome = models.CharField(_('Nome do usuário'), max_length=100, null=True, blank=True)
    desconto = models.ForeignKey('mentorias.Descontos', null=True, blank=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        if not self.usuario_pk:
            self.usuario_pk = self.usuario.pk
        if not self.usuario_email:
            self.usuario_email = self.usuario.email
        if not self.usuario_nome:
            self.usuario_nome = self.usuario.first_name
        super().save(*args, **kwargs)


class Descontos(models.Model):
    criado_por = models.ForeignKey(
        CustomUser, verbose_name=_('Criado por'),
        null=True, blank=True, on_delete=models.SET_NULL)
    desconto = models.FloatField(default=0.00)
    titulo = models.CharField(_('Nome comercial do desconto'), max_length=50)
    abreviatura = models.CharField(_('Abreviatura'), max_length=20, null=True, blank=True)
    descricao = models.TextField(_('Descrição'), null=True, blank=True)
    criado_em = models.DateTimeField(_('Criado em'), default=timezone.now)
    criado_por_pk = models.PositiveIntegerField(null=True, blank=True)
    criado_por_email = models.EmailField(null=True, blank=True)
    criado_por_nome = models.CharField(max_length=50, blank=True, null=True)
    ativo = models.BooleanField(_('Em uso'), default=False)
    desconto = models.FloatField(default=0)
    prazo_duracao = models.PositiveIntegerField(_('Dias duração do desconto'), null=True, blank=True)
    encerramento = models.DateTimeField(_('Encerramento'), null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.criado_por_pk:
            self.criado_por_pk = self.criado_por.pk
        if not self.criado_por_email:
            self.criado_por_email = self.criado_por.email
        if not self.criado_por_nome:
            self.criado_por_nome = self.criado_por.first_name
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo

# Sginals


def pre_save_arquivos(instance, created):
    pass
