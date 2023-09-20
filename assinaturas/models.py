from django.db import models
from usuarios.models import CustomUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models.signals import pre_delete, post_save, pre_save
from django.dispatch import receiver
from usuarios.models import PerfilCobranca
from django.template.defaultfilters import slugify

# # Create your models here.

# NIVEIS_PLANOS = [
#     (5, ('Grupo pequeno')),
#     (10, ('Turmas pequenas')),
#     (20, ('Turmas médias')),
#     (60, ('Turmas grandes')),    
# ]



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
    abreviatura = models.CharField(_('Abreviatura'), help_text=_('Escreva uma abreviatura de até 10 caracteres.'), max_length=10, null=True, blank=True)
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
    desconto_incluido = models.ForeignKey(Descontos, on_delete=models.CASCADE, related_name='oferta_desconto')
    criada_em = models.DateTimeField(_('Data cadastro'), default=timezone.now)
    encerra_em = models.DateTimeField(_('Data do encerramento'), blank=True, null=True)
    ativa = models.BooleanField(_("Ativa"), default=False)
    log_criado_por_pk = models.PositiveIntegerField(null=True, blank=True)
    log_criado_por_email = models.EmailField(null=True, blank=True)
    log_criado_por_nome = models.CharField(max_length=200, blank=True, null=True)
    tipo = models.SmallIntegerField(_("Tipo de oferta"), default=1)

    def __str__(self):
        return self.titulo


class AssinaturasMentor(models.Model):
    mentor = models.ForeignKey(CustomUser, verbose_name=_('Mentor'), null=True, blank=True, on_delete=models.SET_NULL)
    oferta_contratada = models.ForeignKey(
        OfertasPlanos, verbose_name=_('Oferta contratada'),
        on_delete=models.SET_NULL, null=True, blank=True, related_name='assinatura_oferta')
    criada_em = models.DateTimeField(_('Data assinatura'), default=timezone.now)
    encerra_em = models.DateField(_('Encerra em'), null=True, blank=True)
    ativa = models.BooleanField(_('Ativa'), default=True)
    endereco_cobranca = models.ForeignKey(PerfilCobranca, verbose_name=_("Endereço para cobrança"), null=True, blank=True, on_delete=models.SET_NULL)
    renovacao_automatica = models.BooleanField(_("Renovação automática habilitada"), default=True)

    log_mentor_cpf = models.CharField(_('CPF/CNPJ do usuário'), max_length=20, null=True)
    log_telefone1 = models.CharField(_('Telefone de contato com o DDD*'), max_length=25, null=True)
    log_telefone2 = models.CharField(_('Outro telefone de contato com o DDD'), max_length=25, null=True, blank=True)
    log_endereco_resumido = models.CharField(_("Endereço resumido"), null=True, blank=True, max_length=200)
    log_usuario_pk = models.PositiveIntegerField(_("Id do usuário"), null=True, blank=True)
    log_usuario_email = models.EmailField(_('Email do usuário'), null=True, blank=True)
    log_usuario_nome = models.CharField(_('Nome do usuário'), max_length=200, null=True, blank=True)    
    log_meses_isencao_restante = models.IntegerField(_("Meses com isencao"), null=True, blank=True) 
    log_percentual_desconto = models.FloatField(_("Percentual de desconto contratado"), null=True, blank=True)
    log_precos_contratados = models.JSONField(_("Preços contratados"), null=True)
    log_condicoes_contratadas = models.TextField(_("Condições do plano em HTML"), null=True, blank=True)    
    # pagamento = models.JSONField(_("Controle de pagamentos"), null=True, blank=True)    

    def __str__(self):
        return f"{self.mentor.nome_completo}, {self.oferta_contratada}, {self.encerra_em}"


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
        instance.log_criado_por_pk = instance.criado_por.pk
        instance.log_criado_por_email = instance.criado_por.email
        instance.log_criado_por_nome = instance.criado_por.nome_completo


@receiver(pre_save, sender=AssinaturasMentor)
def pre_save_assinaturas(sender, instance, **kwargs):
    precos = instance.oferta_contratada.preco_ofertado.precos
    percentual_desconto = instance.oferta_contratada.desconto_incluido.percentual_desconto
    if not instance.pk:        
        instance.log_mentor_pk = instance.mentor.pk
        instance.log_mentor_email = instance.mentor.email
        instance.log_mentor_nome = instance.mentor.nome_completo
        instance.meses_isencao_restante = instance.oferta_contratada.desconto_incluido.meses_isencao
        instance.log_meses_isencao_restante = instance.oferta_contratada.desconto_incluido.meses_isencao
        instance.log_percentual_desconto = percentual_desconto
        instance.log_endereco_resumido = instance.endereco_cobranca.endereco_resumido
        instance.log_mentor_cpf = instance.endereco_cobranca.cpf_cnpj
        instance.log_telefone1 = instance.endereco_cobranca.telefone1
        instance.log_telefone2 = instance.endereco_cobranca.telefone2
        instance.log_condicoes_contratadas = instance.oferta_contratada.preco_ofertado.condicoes
        if percentual_desconto > 0:
            for letras in precos['display'].keys():
                precos['display'][letras][2] = round(float(precos['display'][letras][2].replace(",", ".")) * ((100 - percentual_desconto) / 100), 2)
        instance.log_precos_contratados = precos
    else:
        instance.log_endereco_resumido = instance.endereco_cobranca.endereco_resumido
        if percentual_desconto > 0:
            for letras in precos['display'].keys():
                precos['display'][letras][2] = round(float(precos['display'][letras][2].replace(",", ".")) * ((100 - percentual_desconto) / 100), 2)

        instance.log_precos_contratados = precos

@receiver(pre_save, sender=FaturasMentores)
def pre_save_faturas(sender, instance, **kwargs):
    if not instance.pk:        
        instance.log_mentor_pk = instance.mentor.pk
        instance.log_mentor_email = instance.mentor.email
        instance.log_mentor_nome = instance.mentor.nome_completo
        instance.mentor_cpf = instance.assinatura.log_mentor_cpf

## Planos de pagamentos
# Qtd Alunos  ----    Valor   ----    Preço P/A
#     1                50,00           -
#     2                80,00           - 
#     3º ao 10º         -             19,99 p/a
#     11º ao 50º        -             15,99 p/a
#     51º ao 100º       -             9,98  p/a
#     101º ou mais      -             5,98  p/a
## Ou
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
    language = models.CharField(
        _("Lingua"),
        max_length=5,
        null=False,
        blank=False,
        default='pt-br',
        choices=LANG
    )
    slug = models.SlugField('Slug', max_length=100, blank=True, editable=False)

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
        self.user_email = self.user.email
        self.profile_id = self.user.id
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user}, {self.acept_date}, {self.termo}'


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
        return f'{self.action}, {self.termo_user_id}, {self.termos_title}'

    class Meta:
        verbose_name_plural = _('Modificações nos termos')

