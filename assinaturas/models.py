from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models.signals import  pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
import re
from copy import deepcopy
from usuarios.models import PerfilCobranca
from usuarios.models import CustomUser

# # Create your models here.

# NIVEIS_PLANOS = [
#     (5, ('Grupo pequeno')),
#     (10, ('Turmas pequenas')),
#     (20, ('Turmas médias')),
#     (60, ('Turmas grandes')),    
# ]

def user_directory_path(instance, filename):
    ext = filename[-3:]
    variavel = str(timezone.now())[0:19]
    variavel = re.sub('\D', '', variavel)
    filename = f'{filename[:-4]}_{variavel}.{ext}'
    return f'system/termos_de_uso/{instance.id}/{filename}'

def file_size(value):  # add this to some file where you can import it from
    limit = 10 * 1024 * 1024
    if value.size > limit:
        raise ValidationError(_('Arquivo muito grande. Tamanho não pode exceder 10MB.'))


class PrecosAssinatura(models.Model):
    criado_por = models.ForeignKey(
        CustomUser, verbose_name=_('Criado por'),
        null=True, blank=True, on_delete=models.SET_NULL)
    titulo = models.CharField(_('Nome comercial'), max_length=100)
    descricao = models.TextField(_('Descrição'), null=True, blank=True)
    criado_em = models.DateTimeField(_('Criado em'), default=timezone.now)
    ativo = models.BooleanField(_('Em uso'), default=False)
    log_criado_por_pk = models.PositiveIntegerField(null=True, blank=True)
    log_criado_por_email = models.EmailField(null=True, blank=True)
    log_criado_por_nome = models.CharField(max_length=200, null=True, blank=True)
    precos = models.JSONField(_('Preços'))
    condicoes = models.TextField(_("Condições do plano em HTML"), null=True, blank=True)

    def __str__(self):
        return self.titulo


class Descontos(models.Model):    
    criado_por = models.ForeignKey(
        CustomUser, verbose_name=_('Criado por'),
        null=True, blank=True, on_delete=models.SET_NULL)
    percentual_desconto = models.FloatField(default=0.00)
    meses_isencao = models.SmallIntegerField(_('Meses de isenção'), default=1)
    titulo = models.CharField(_('Nome comercial do desconto'), max_length=100)
    resumo_desconto = models.CharField(_('Resumo do desconto'), help_text=_('Escreva um resumo de até 100 caracteres.'), max_length=100, null=True, blank=True)
    descricao = models.TextField(_('Descrição'), null=True, blank=True)    
    criado_em = models.DateTimeField(_('Criado em'), default=timezone.now)
    ativo = models.BooleanField(_('Em uso'), default=False)
    desconto = models.FloatField(default=0)
    encerramento = models.DateTimeField(_('Encerramento'), null=True, blank=True)
    ativo = models.BooleanField(_('Ativo'), default=False)
    log_criado_por_pk = models.PositiveIntegerField(null=True, blank=True)
    log_criado_por_email = models.EmailField(null=True, blank=True)
    log_criado_por_nome = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.titulo


class OfertasPlanos(models.Model):
    # TIPO_OFERTA:
    # 1: Específica
    # 2: Geral
    criado_por = models.ForeignKey(
        CustomUser, verbose_name=_('Criado por'),
        null=True, blank=True, on_delete=models.SET_NULL)
    titulo = models.CharField(_("Título da oferta"), max_length=100)
    pequeno_anuncio = models.CharField(_("Pequeno anúncio para a oferta"), max_length=100, null=True, blank=True)
    preco_ofertado = models.ForeignKey(PrecosAssinatura, verbose_name=_("Preço ofertado"), on_delete=models.CASCADE)
    desconto_incluido = models.ForeignKey(Descontos, on_delete=models.CASCADE, related_name='oferta_desconto', null=True, blank=True)
    criada_em = models.DateTimeField(_('Data cadastro'), default=timezone.now)
    inicia_vigencia = models.DateField(_("Início da vigência"), null=True, blank=True)
    encerra_em = models.DateField(_('Data do encerramento'), blank=True, null=True)
    promocional = models.BooleanField(_("É promocional"), default=False)
    ativa = models.BooleanField(_("Ativa"), default=True)
    log_criado_por_pk = models.PositiveIntegerField(null=True, blank=True)
    log_criado_por_email = models.EmailField(null=True, blank=True)
    log_criado_por_nome = models.CharField(max_length=200, blank=True, null=True)
    tipo = models.SmallIntegerField(_("Tipo de oferta"), default=1)

    @property
    def retorna_precos_oferta(self):
        if self.desconto_incluido:
            if self.desconto_incluido.percentual_desconto > 0:
                for letras in self.preco_ofertado.precos['display'].keys():
                    self.preco_ofertado.precos['display'][letras][2] = str(format(round(float(self.preco_ofertado.precos['display'][letras][2].replace(",", ".")) * ((100 - self.desconto_incluido.percentual_desconto) / 100), 2), '.2f')).replace('.', ',')
            
            return self.preco_ofertado.precos    
        else:            
            return self.preco_ofertado.precos
        
    def __str__(self):
        return self.titulo

    class Meta:
        ordering = ['-id', ]    


class AssinaturasMentor(models.Model):
    mentor = models.ForeignKey(CustomUser, verbose_name=_('Mentor'), null=True, blank=True, on_delete=models.SET_NULL, related_name="assinaturas_mentor")
    oferta_contratada = models.ForeignKey(
        OfertasPlanos, verbose_name=_('Oferta contratada'),
        on_delete=models.SET_NULL, null=True, blank=True, related_name='assinatura_oferta')
    resumo = models.CharField(_("Resumo da oferta"), max_length=100, null=True, blank=True)
    resumo_desconto = models.CharField(_("Resumo do desconto incluído"), max_length=50, null=True, blank=True)
    criada_em = models.DateTimeField(_('Data assinatura'), default=timezone.now)
    inicia_vigencia = models.DateField(_('Inicia vigência em'), null=True, blank=True)
    encerra_em = models.DateField(_('Encerra em'), null=True, blank=True)
    ativa = models.BooleanField(_('Ativa'), default=True)    
    # perfil_cobranca = models.ForeignKey(PerfilCobranca, verbose_name=_("Perfil de cobrança"), null=True, blank=True, on_delete=models.SET_NULL)
    renovacao_automatica = models.BooleanField(_("Renovação automática habilitada"), default=True)
    log_mentor_cpf = models.CharField(_('CPF/CNPJ do usuário'), max_length=20, null=True, blank=True)
    log_telefone1 = models.CharField(_('Telefone de contato com o DDD*'), max_length=25, null=True, blank=True)
    log_telefone2 = models.CharField(_('Outro telefone de contato com o DDD'), max_length=25, null=True, blank=True)
    log_endereco_resumido = models.CharField(_("Endereço resumido"), null=True, blank=True, max_length=200)
    log_usuario_pk = models.PositiveIntegerField(_("Id do usuário"), null=True, blank=True)
    log_usuario_email = models.EmailField(_('Email do usuário'), null=True, blank=True)
    log_usuario_nome = models.CharField(_('Nome do usuário'), max_length=200, null=True, blank=True)    
    log_meses_isencao_restante = models.IntegerField(_("Meses com isencao"), null=True, blank=True) 
    log_percentual_desconto = models.FloatField(_("Percentual de desconto contratado"), null=True, blank=True)
    log_precos_contratados = models.JSONField(_("Preços contratados"), null=True, blank=True)
    log_condicoes_contratadas = models.TextField(_("Condições do plano em HTML"), null=True, blank=True)    
    # pagamento = models.JSONField(_("Controle de pagamentos"), null=True, blank=True)    

    def __str__(self):
        return f"{self.mentor.nome_completo}, {self.oferta_contratada}, {self.encerra_em}"

    class Meta:
        ordering = ['encerra_em']

class FaturasMentores(models.Model):
    mentor = models.ForeignKey(CustomUser, verbose_name=_("Mentor"), null=True, on_delete=models.SET_NULL)
    assinatura = models.ForeignKey(AssinaturasMentor, verbose_name="Assinatura relacionada", null=True, related_name='fatura_assinatura', on_delete=models.SET_NULL)
    demonstrativo = models.JSONField(_("Demonstrativo das cobranças"), null=True)
    mes_referencia = models.CharField(_("Mês de referência da fatura"), max_length=10, null=True)
    log_mentor_pk = models.IntegerField(_('Mentor pk'), null=True)
    log_mentor_email = models.EmailField(_("Email do usuário"), null=True)
    log_mentor_nome = models.CharField(_('Nome do usuário'), max_length=200, null=True)
    gastos_no_mes = models.FloatField(_("Gastos no mês"), default=0)
    vencimento = models.DateField(_("Data do vencimento"))
    mentor_cpf = models.CharField(_('CPF/CNPJ do usuário'), max_length=20, null=True)
    mes_isento = models.BooleanField(_("Mês de isenção"), default=False)    
    total_a_pagar = models.FloatField(_("Valor a pagar"))
    foi_paga = models.BooleanField(_("Pago"), default=False)
    data_pagamento = models.DateField(_("Data do pagamento"), null=True, blank=True)
    numero_transacao = models.CharField(_("Transação"), max_length=30, null=True)

    def __str__(self):
        return f"{self.mentor.nome_completo}, {self.vencimento}, {self.total_a_pagar}"

    class Meta:
        ordering = ['-id', ]

# Signals
@receiver(pre_save, sender=PrecosAssinatura)
def pre_save_precos(sender, instance, **kwargs):
    if not instance.pk:
        instance.log_criado_por_pk = instance.criado_por.pk
        instance.log_criado_por_email = instance.criado_por.email
        instance.log_criado_por_nome = instance.criado_por.nome_completo
    
@receiver(pre_save, sender=Descontos)
def pre_save_descontos(sender, instance, **kwargs):
    if not instance.pk:        
        instance.log_criado_por_pk = instance.criado_por.pk
        instance.log_criado_por_email = instance.criado_por.email
        instance.log_criado_por_nome = instance.criado_por.nome_completo
    

@receiver(pre_save, sender=OfertasPlanos)
def pre_save_ofertas(sender, instance, **kwargs):
    if not instance.pk:
        if instance.promocional:
            if not instance.inicia_vigencia:
                instance.inicia_vigencia = date.today()
            if not instance.encerra_em:
                instance.encerra_em = date.today()+timedelta(days=30)
        else:
            hoje = date.today()
            oferta_vigente = OfertasPlanos.objects.filter(encerra_em__gte=hoje, promocional=False).exclude(inicia_vigencia__gte=hoje).first()
            if oferta_vigente:
                dia_encerra_vigencia = oferta_vigente.encerra_em
            else:
                dia_encerra_vigencia = date.today()
            ano_seguinte = date(year=dia_encerra_vigencia.year+1, month=dia_encerra_vigencia.month, day=28)            
            instance.inicia_vigencia = dia_encerra_vigencia+timedelta(days=1)
            instance.encerra_em = ano_seguinte
        instance.log_criado_por_pk = instance.criado_por.pk
        instance.log_criado_por_email = instance.criado_por.email
        instance.log_criado_por_nome = instance.criado_por.nome_completo


@receiver(pre_save, sender=AssinaturasMentor)
def pre_save_assinaturas(sender, instance, **kwargs):
    precos = deepcopy(instance.oferta_contratada.preco_ofertado.precos)
    if instance.oferta_contratada.desconto_incluido:
        percentual_desconto = instance.oferta_contratada.desconto_incluido.percentual_desconto
        meses_isencao = instance.oferta_contratada.desconto_incluido.meses_isencao
    else:
        percentual_desconto = 0
        meses_isencao = 0
    resumo = F"{instance.oferta_contratada}"
    if instance.oferta_contratada.desconto_incluido:
        resumo_desconto = instance.oferta_contratada.desconto_incluido.resumo_desconto
    else:
        resumo_desconto = ''
    if not instance.pk:
        instance.resumo = resumo
        instance.resumo_desconto = resumo_desconto
        instance.log_mentor_pk = instance.mentor.pk
        instance.log_mentor_email = instance.mentor.email
        instance.log_mentor_nome = instance.mentor.nome_completo
        instance.meses_isencao_restante = meses_isencao
        instance.log_meses_isencao_restante = meses_isencao
        instance.log_percentual_desconto = percentual_desconto
        instance.log_condicoes_contratadas = instance.oferta_contratada.preco_ofertado.condicoes        
        if percentual_desconto > 0:
            for letras in precos['display'].keys():
                precos['display'][letras][2] = str(format(round(float(precos['display'][letras][2].replace(",", ".")) * ((100 - percentual_desconto) / 100), 2), '.2f')).replace('.', ',')
        instance.log_precos_contratados = precos


@receiver(pre_save, sender=FaturasMentores)
def pre_save_faturas(sender, instance, **kwargs):
    if not instance.pk:        
        instance.log_mentor_pk = instance.mentor.pk
        instance.log_mentor_email = instance.mentor.email
        instance.log_mentor_nome = instance.mentor.nome_completo
        instance.mentor_cpf = instance.assinatura.log_mentor_cpf

## Planos de pagamentos(desatualizado)
# {"display": {"a": ["1", "Um aluno", "39,9"], 
# "b": ["2", "O 2º aluno", "34,9"], 
# "c": ["5", "Do 3º ao 5º aluno", "29,9"], 
# "d": ["10", "Do 6º ao 10º aluno", "24,9"], 
# "e": ["20", "Do 11º ao 20º aluno", "19,9"], 
# "f": ["50", "Do 21º ao 50º aluno", "14,9"], 
# "g": ["100", "Do 51º ao 100º aluno", "9,9"], 
# "h":["999", "Do 101º aluno em diante", "4,9"]}}


class TermosDeUso(models.Model):
    LANG = (
        ('pt-br', 'Portuguese'),
        ('en', 'English')
    )
    PUBLICO_ALVO = (
        ('mentor', 'Mentor'),
        ('aluno', 'Aluno')
    )
    termo_title = models.CharField(_("Título do termo"), max_length=50, null=True)
    text = models.TextField(_("Conteúdo do termo"))
    begin_date = models.DateTimeField(
        _("Data do início da vigência"), auto_now=False, auto_now_add=False)
    end_date = models.DateTimeField(
        _("Data do fim da vigência"), auto_now=False, auto_now_add=False, null=True, blank=True)
    active = models.BooleanField(
        _("Regra está vigente(regra em uso)"), default=False)
    criada_em = models.DateTimeField(
        _("Data da criação"), auto_now_add=True, null=True, blank=True)

    user = models.ForeignKey("usuarios.CustomUser",
                             verbose_name=_("Usuário que criou a regra"),
                             on_delete=models.SET_NULL, null=True,
                             blank=True
                             )
    user_email = models.EmailField(_("Email do usuário que criou a regra"),
                                   max_length=254, null=True, blank=True)
    termo_user_id = models.IntegerField(_("Id do usuário que criou a regra"),
                                         null=True, blank=True)
    arquivo_termo = models.FileField(upload_to=user_directory_path,
                                    verbose_name=_("Arquvio do termo"),
                                    help_text=_('Insira arquivo em .pdf de até 10MB de tamanho.'),
                                    validators=[
                                        FileExtensionValidator(allowed_extensions=["pdf"]),
                                        file_size
                                    ], null=True
                                    )    
    language = models.CharField(
        _("Lingua"),
        max_length=5,
        null=False,
        blank=False,
        default='pt-br',
        choices=LANG
    )
    slug = models.SlugField('Slug', max_length=100, blank=True, editable=False)
    publico_allvo = models.CharField(_('Público alvo do termo'), max_length=10, default='mentor', choices=PUBLICO_ALVO, null=True)

    def __str__(self):
        return self.termo_title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.termo_title)
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = _('Termos')


class TermosAceitos(models.Model):
    user = models.ForeignKey('usuarios.CustomUser', verbose_name=_(
        "Usuário"), on_delete=models.SET_NULL, null=True)    
    user_email = models.EmailField(_("Email do usuário"), max_length=254)
    profile_id = models.IntegerField(_("Id do usuário"))
    acept_date = models.DateTimeField(
        _("Data da aceitação"), auto_now_add=True)
    termo = models.ForeignKey(TermosDeUso, verbose_name=_(
        "Termos de Uso"), on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.user:
            self.user_email = self.user.email
            self.profile_id = self.user.id
        return super().save(*args, **kwargs)

    def __str__(self):        
        return f'{self.user}, {self.acept_date}, {self.termo}.'


class AlteracoesTermos(models.Model):
    user_email = models.EmailField(
        _("Email do usuário que criaou ou modificou o termo"),
        max_length=254, null=True, blank=True)
    termo_user_id = models.IntegerField(
        _("Id do usuário que criaou ou modificou o termo"),
        null=True, blank=True)
    termo_title = models.CharField(
        _("Título da política"), max_length=50, null=True, blank=True)
    termo_status = models.CharField(_("Estado do termo(ativa ou não)"),
                                     blank=True,
                                     null=True,
                                     max_length=10)
    termo_content = models.TextField(
        _("Conteúdo do termo"), null=True, blank=True)
    termo_pkey = models.IntegerField(
        _("Id do termo"), null=True, blank=True)
    mod_date = models.DateTimeField(
        _("Data da modificação"), auto_now_add=True, null=True)
    action = models.CharField(
        _("Ação realizada"), max_length=50, null=True, blank=True)

    def __str__(self):
        return f'{self.action}, {self.termo_user_id}, {self.termo_title}'

    class Meta:
        verbose_name_plural = _('Modificações nos termos')


        # precos = deepcopy(instance.oferta_contratada.preco_ofertado.precos)

    # else:
    #     if percentual_desconto > 0:
    #         for letras in precos['display'].keys():
    #             precos['display'][letras][2] = round(float(precos['display'][letras][2].replace(",", ".")) * ((100 - percentual_desconto) / 100), 2)

        # instance.log_precos_contratados = precos