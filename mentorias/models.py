from django.db import models
from usuarios.models import CustomUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import date, datetime
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from django.conf import settings
import os
from statistics import mean
import zoneinfo
# import random
import string
import re
from secrets import SystemRandom as SR

from utils.resources import (
    PREPARO_CHOICES, PERFIL_PSICO, SITUACAO_ALUNO, QUESTAO_TIPO, ATIVIDADE_MATRICULA
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
    result_str = ''.join(SR().choices(string.ascii_letters + string.digits + string.punctuation, k=8))
    return result_str


class Mentoria(models.Model):
    mentor = models.ForeignKey(CustomUser,
                               on_delete=models.SET_NULL, null=True, blank=True)
    titulo = models.CharField(
        max_length=100, verbose_name=_('Titulo da mentoria'),
        help_text=_('Insira um título para a mentoria.'),
        blank=False, null=False)
    criada_em = models.DateTimeField(_('Data criação:'), blank=True, default=timezone.now)
    encerra_em = models.DateField(_('Fim da mentoria:'), help_text=_("Todas as matrículas desta mentoria durarão até no máximo esta data."), blank=True, default=timezone.now)
    periodo_duracao = models.SmallIntegerField("Período de duração de uma matrícula (em meses).", null=True, blank=True, help_text=_("Novas matrículas na mentoria terão esta duração por padrão."), default=6)
    controle = models.TextField(verbose_name=_('Anotações da mentoria'), null=True, blank=True, help_text=_(
        'Anotações da Mentoria para seu controle. Apenas você terá acesso a este conteúdo.'))
    resumo_mentoria = models.TextField(
        _('Apresentação da mentoria'),
        help_text=_('Se desejar, escreva um texto de apresentação desta mentoria ao estudante.'),
        null=True, blank=True)
    etapas = models.JSONField(
        _("Etapas da mentoria"), null=True, blank=True)
    ativa = models.BooleanField(_('Ativa'), default=True)
    simulados_mentoria = models.ManyToManyField('mentorias.AplicacaoSimulado', blank=True)
    links_externos = models.ManyToManyField('mentorias.LinksExternos', blank=True)
    username_mentor = models.CharField('Username do Mentor', max_length=50, null=True, blank=True)
    estatisticas = models.JSONField('Estatísticas', null=True, blank=True)

    @property
    def matriculas_ativas(self):
        matriculas_ativas = self.matriculas_mentoria.filter(encerra_em__gte=timezone.now())
        return matriculas_ativas
    
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
    email_aluno = models.EmailField(verbose_name=_('Email do Aluno'))
    telefone_aluno = models.CharField(verbose_name=_('Telefone do Aluno'),
                                      max_length=25, null=True, blank=True)
    situacao_aluno = models.CharField(
        max_length=2, verbose_name=_('Situação'),
        help_text=_('Se é aluno atual, ou ex-aluno.'),
        default='at', choices=SITUACAO_ALUNO)

    criado_em = models.DateTimeField(_('Data do cadastramento do aluno'),
                                     default=timezone.now)
    controle = models.TextField(
        help_text=_(
            'Anote o que achar necessário para fins de controle do aluno. Aluno não tem acesso a este conteúdo.'),
        null=True, blank=True)
    nivel_preparo = models.PositiveSmallIntegerField(
        verbose_name=_('Nível de preparo para o objetivo final.'),
        null=True, blank=True, choices=PREPARO_CHOICES, default=1)
    perfil_psicológico = models.CharField(max_length=3, verbose_name=_('Perfil psicológico do aluno'),
                                          null=True, blank=True, choices=PERFIL_PSICO)
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
    criada_em = models.DateTimeField(_('Data da matrícula'), default=timezone.now)
    encerra_em = models.DateTimeField(_('Encerramento mentoria'), blank=True, null=True)
    estatisticas = models.JSONField('Estatísticas', null=True, blank=True)
    senha_do_aluno = models.CharField(
        _('Senha para acesso'), max_length=8,
        default=get_random_string, null=True, blank=True)
    mentoria = models.ForeignKey(Mentoria, null=True, blank=True, on_delete=models.SET_NULL, related_name='matriculas_mentoria')
    ativa = models.BooleanField(_("Está ativa"), default=True)
    # data_desativada = models.DateTimeField(_("Data e hora que foi desativada"), null=True, blank=True)

    class Meta:
        ordering = ['aluno',]

    @property
    def retorna_media_matricula(self):
        aplicacoes = AplicacaoSimulado.objects.filter(matricula=self).order_by('data_resposta')
        media_simulados = []
        for apl in aplicacoes:
            estatistica = apl.resposta_alunos        
            if apl.data_resposta:
                media_simulados.append(int(estatistica["resumo"]["percentual"]))        
        if media_simulados:
            media = [round(mean(media_simulados), 2), True]
        else:
            media = ["--", False]
        return media

    @property
    def falta_responder(self):
        falta_responder = 0 
        if self.aplicacoes_matricula:
            for aplicacao in self.aplicacoes_matricula.all():
                if not aplicacao.data_resposta:
                    falta_responder += 1
        data_ultima_aplicacao = self.aplicacoes_matricula.all().order_by('criada_em').first()

        return falta_responder, data_ultima_aplicacao


class Simulados(models.Model):
    mentor = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    mentor_name = models.TextField(null=True, blank=True)
    mentor_username = models.TextField(null=True, blank=True)
    titulo = models.CharField(verbose_name=_('Título do simulado'), max_length=100)
    questao_tipo = models.SmallIntegerField(verbose_name=_('Tipo de questões'),
                                            choices=QUESTAO_TIPO, default=2, null=True, blank=True)
    criado_em = models.DateField(_('Criado'), auto_now_add=True)
    instrucao = models.TextField(verbose_name=_('Instruções ao aluno que fará o simulado'), help_text=_(
        'Se desejar, seus alunos poderão receber instruções para a realização do simulado.'), null=True, blank=True)
    data_aplicacao = models.DateField(verbose_name=_('Data prevista para aplicação'), default=timezone.now)
    pdf_prova = models.ForeignKey('mentorias.ArquivosMentoria', related_name="pdf_prova",
                                     on_delete=models.SET_NULL, null=True, blank=True)
    controle = models.TextField(verbose_name=_('Anotações da mentoria'), null=True, blank=True, help_text=_(
        'Anotações da Mentoria para seu controle. Apenas você terá acesso a este conteúdo.'))
    gabarito = models.JSONField(
        _("Respostas do Gabarito"), null=True, blank=True)
    estatisticas = models.JSONField('Estatísticas', null=True, blank=True) 

    @property
    def filename(self):
        return os.path.basename(self.pdf_prova.arquivo_mentoria.name)

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        if not self.mentor_name:
            self.mentor_username = self.mentor.username
        return super().save(*args, **kwargs)


class Materias(models.Model):
    mentor = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    titulo = models.CharField(_('Título da matéria'), max_length=50)
    criada_em = models.DateField(_('Criada em'), default=timezone.now)
    controle = models.TextField(verbose_name=_('Anotações da matéria'), null=True, blank=True, help_text=_(
        'Anotações da matéria para seu controle. Apenas você terá acesso a este conteúdo.'))
    peso = models.PositiveSmallIntegerField(_('Peso da matéria'), help_text=_(
        'Indique o peso da matéria para fins de cálculo de resultado final.'), default=1)
    simulados = models.ManyToManyField(Simulados, blank=True)
    em_uso = models.BooleanField(_('Em uso'), default=True)
    
    def __str__(self):
        return self.titulo

    class Meta:
        ordering = ['titulo',]


class ArquivosMentoria(models.Model):
    mentoria = models.ForeignKey(Mentoria,
                                 on_delete=models.SET_NULL, null=True, blank=True, related_name='mentoria_arquivos')
    mentor = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    mentor_nome = models.CharField(_('Criado por:'), max_length=50, null=True, blank=True)
    titulo_arquivo = models.CharField(max_length=100, verbose_name=_('Nome do arquivo'), null=True)
    arquivo_mentoria = models.FileField(upload_to=user_directory_path,
                                        verbose_name=_("Arquvio mentoria"),
                                        help_text=_('Insira arquivo em .pdf de até 5MB de tamanho.'),
                                        validators=[
                                            FileExtensionValidator(allowed_extensions=["pdf"]),
                                            file_size
                                        ], null=True
                                        )
    matricula = models.ForeignKey(MatriculaAlunoMentoria, null=True, blank=True, on_delete=models.CASCADE, related_name='arquivos_matricula')
    aluno = models.ForeignKey(Alunos, null=True, blank=True, on_delete=models.CASCADE, related_name='arquivos_aluno')

    def save(self, *args, **kwargs):
        if not self.mentor_nome or self.mentor.first_name != self.mentor_nome:
            self.mentor_nome = self.mentor.first_name
        return super().save(*args, **kwargs)

    @property
    def filename(self):
        return os.path.basename(self.arquivo_mentoria.name)

    def __str__(self):
        if self.titulo_arquivo:
            return self.titulo_arquivo
        return self.filename


class LinksExternos(models.Model):
    titulo = models.CharField(_("Titulo do link"), max_length=50, blank=True, null=True)
    link_url = models.URLField(_('Link'), blank=True, null=True)
    descricao = models.CharField(
        _('Descrição'),
        help_text=_('Escreva uma breve descrição, caso você deseja comunicar-se com o aluno à respeito do link.'),
        max_length=100, null=True, blank=True)

    def __str__(self):
        if self.titulo:
            return self.titulo
        else:
            return self.link_url


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
    senha_do_aluno = models.TextField(
        _('Senha para acesso'),
        default=get_random_string, null=True, blank=True)
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
        unique_together = ['matricula', 'simulado']
        ordering = ['-criada_em', 'aluno']


class RegistrosMentor(models.Model):
    data_registro = models.DateTimeField(_("Data do registro"), default=timezone.now)        
    log_mentor_id = models.IntegerField(_("Id do mentor"), null=True)
    log_mentor_nome = models.TextField(_("Nome do mentor"), null=True)
    log_mentor_email = models.EmailField(_("Email do mentor"), null=True)
    log_matricula_id = models.IntegerField(_("Id da matrícula"), null=True)
    log_matricula_email = models.EmailField(_("Email do aluno nesta matrícula"), null=True)  
    log_matricula_encerra_em = models.DateTimeField(_("Data encerramento da matrícula"), null=True)  
    log_mentoria_id = models.IntegerField(_("Id da mentoria"), null=True)    
    log_mentoria_titulo = models.TextField(_("Título da mentoria"), null=True)
    log_matricula_ativa = models.BooleanField(_("Ativa"), null=True)
    atividade = models.CharField(_("Atividade da matrícula"), null=False, max_length=4,
                                 choices=ATIVIDADE_MATRICULA)
    data_resposta = models.DateTimeField(_("Data da resposta do simulado"), null=True)
    log_simulado = models.IntegerField(_('Número do simulado'), null=True)

    def __str__(self):
        return f"Matrícula {self.log_matricula_id}. {self.atividade}. Data: {self.data_registro}"



# Sginals
@receiver(post_save, sender=MatriculaAlunoMentoria)
def post_save_matricula(sender, instance, created, **kwargs):
    if created:
        RegistrosMentor.objects.create(
            log_mentor_id = instance.mentoria.mentor.id,
            log_mentor_email = instance.mentoria.mentor.email,
            log_mentor_nome = f"{instance.mentoria.mentor.first_name} {instance.mentoria.mentor.last_name}",
            log_mentoria_id = instance.mentoria.id,
            log_mentoria_titulo = instance.mentoria.titulo,
            log_matricula_id = instance.id,
            log_matricula_email = instance.aluno.email_aluno,
            log_matricula_encerra_em = instance.encerra_em,
            log_matricula_ativa = instance.ativa,
            atividade='cria'
        )
    else:
        RegistrosMentor.objects.create(
            log_mentor_id = instance.mentoria.mentor.id,
            log_mentor_email = instance.mentoria.mentor.email,
            log_mentor_nome = f"{instance.mentoria.mentor.first_name} {instance.mentoria.mentor.last_name}",
            log_mentoria_id = instance.mentoria.id,
            log_mentoria_titulo = instance.mentoria.titulo,
            log_matricula_id = instance.id,
            log_matricula_email = instance.aluno.email_aluno,
            log_matricula_encerra_em = instance.encerra_em,
            log_matricula_ativa = instance.ativa,
            atividade='alte'
        )

@receiver(pre_delete, sender=MatriculaAlunoMentoria)
def pre_delete_matricula(sender, instance, **kwargs):
    RegistrosMentor.objects.create(
        log_mentor_id = instance.mentoria.mentor.id,
        log_mentor_email = instance.mentoria.mentor.email,
        log_mentor_nome = f"{instance.mentoria.mentor.first_name} {instance.mentoria.mentor.last_name}",
        log_mentoria_id = instance.mentoria.id,
        log_mentoria_titulo = instance.mentoria.titulo,
        log_matricula_id = instance.id,
        log_matricula_email = instance.aluno.email_aluno,
        log_matricula_encerra_em = instance.encerra_em,
        log_matricula_ativa = instance.ativa,
        atividade='apag'
    )    