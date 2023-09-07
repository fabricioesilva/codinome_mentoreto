from django.db import models
from usuarios.models import CustomUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models.signals import pre_delete, post_save, pre_save
from django.dispatch import receiver
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
    preco = models.FloatField()    
    log_criado_por_pk = models.PositiveIntegerField(null=True, blank=True)
    log_criado_por_email = models.EmailField(null=True, blank=True)
    log_criado_por_nome = models.CharField(max_length=200, null=True, blank=True)
    precos = models.JSONField(_('Preços'))    

    def __str__(self):
        return self.titulo


class Descontos(models.Model):
    criado_por = models.ForeignKey(
        CustomUser, verbose_name=_('Criado por'),
        null=True, blank=True, on_delete=models.SET_NULL)
    percentual_desconto = models.FloatField(default=0.00)
    meses_isencao = models.SmallIntegerField(_('Meses de isenção'), default=1)
    meses_desconto = models.SmallIntegerField(_("Meses de desconto"), default=12)
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
    criado_por = models.ForeignKey(
        CustomUser, verbose_name=_('Criado por'),
        null=True, blank=True, on_delete=models.SET_NULL)
    titulo = models.CharField(_("Título da oferta"), max_length=100)
    preco_ofetado = models.ForeignKey(PrecosAssinatura, verbose_name=_("Preço ofertado"), on_delete=models.CASCADE)
    desconto_incluido = models.ForeignKey(Descontos, on_delete=models.CASCADE, related_name='oferta_desconto')
    criada_em = models.DateTimeField(_('Data cadastro'), default=timezone.now)
    encerra_em = models.DateTimeField(_('Data do encerramento'), blank=True, null=True)
    ativa = models.BooleanField(_("Ativa"), default=False)
    log_criado_por_pk = models.PositiveIntegerField(null=True, blank=True)
    log_criado_por_email = models.EmailField(null=True, blank=True)
    log_criado_por_nome = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.titulo


class AssinaturasMentor(models.Model):
    usuario = models.ForeignKey(CustomUser, verbose_name=_('Mentor'), null=True, blank=True, on_delete=models.SET_NULL)
    oferta_contratada = models.ForeignKey(
        OfertasPlanos, verbose_name=_('Oferta contratada'),
        on_delete=models.SET_NULL, null=True, blank=True, related_name='assinatura_oferta')
    criada_em = models.DateTimeField(_('Data assinatura'), default=timezone.now)
    encerra_em = models.DateField(_('Encerra em'), null=True, blank=True)
    ativa = models.BooleanField(_('Ativa'), default=True)
    usuario_cpf = models.CharField(_('CPF/CNPJ do usuário'), max_length=20)
    log_usuario_pk = models.PositiveIntegerField(_("Id do usuário"), null=True, blank=True)
    log_usuario_email = models.EmailField(_('Email do usuário'), null=True, blank=True)
    log_usuario_nome = models.CharField(_('Nome do usuário'), max_length=200, null=True, blank=True)    
    meses_desconto_restante = models.IntegerField(_("Meses com desconto"), default=0)
    meses_isencao_restante = models.IntegerField(_("Meses com isencao"), default=1)
    limite_matriculas = models.IntegerField(_("Limite de matrículas"))
    # pagamento = models.JSONField(_("Controle de pagamentos"), null=True, blank=True)    

    def __str__(self):
        return f"{self.usuario.nome_completo}, {self.plano}, {self.encerra_em}"


class FaturasMentores(models.Model):
    usuario = models.ForeignKey(CustomUser, verbose_name=_("Mentor"), null=True, on_delete=models.SET_NULL)
    assinatura = models.ForeignKey(AssinaturasMentor, verbose_name="Assinatura relacionada", null=True, related_name='fatura_assinatura', on_delete=models.SET_NULL)
    log_usuario_pk = models.IntegerField(_('Usuario pk'), null=True)
    log_usuario_email = models.EmailField(_("Email do usuário"), null=True)
    log_usuario_nome = models.CharField(_('Nome do usuário'), max_length=200, null=True)
    quantidade_matriculas = models.IntegerField(_("Quantidade de matrículas ativas"), default=0)
    vencimento = models.DateField(_("Data do vencimento"))
    usuario_cpf = models.CharField(_('CPF/CNPJ do usuário'), max_length=20)
    valor_total = models.FloatField(_("Valor total"))
    desconto_aplicado = models.FloatField(_("Desconto aplicado"), default=0.00)
    mes_isento = models.BooleanField(_("Mês de isenção"), default=False)    
    total_a_pagar = models.FloatField(_("Valor a pagar"))
    foi_paga = models.BooleanField(_("Pago"), default=False)
    data_pagamento = models.DateField(_("Data do pagamento"), null=True, blank=True)
    numero_transacao = models.CharField(_("Transação"), max_length=30, null=True)

    def __str__(self):
        return f"{self.usuario.nome_completo}, {self.plano}, {self.total_a_pagar}"


# Signals
@receiver(pre_save, sender=PrecosAssinatura)
def pre_save_planos(instance, sender, created, **kwargs):
    if created:        
        log_criado_por_pk = instance.criado_por.pk
        log_criado_por_email = instance.criado_por.email
        log_criado_por_nome = instance.criado_por.nome_completo
    
@receiver(pre_save, sender=Descontos)
def pre_save_planos(instance, sender, created, **kwargs):
    if created:        
        log_criado_por_pk = instance.criado_por.pk
        log_criado_por_email = instance.criado_por.email
        log_criado_por_nome = instance.criado_por.nome_completo
    

@receiver(pre_save, sender=OfertasPlanos)
def pre_save_planos(instance, sender, created, **kwargs):
    if created:        
        log_criado_por_pk = instance.criado_por.pk
        log_criado_por_email = instance.criado_por.email
        log_criado_por_nome = instance.criado_por.nome_completo


@receiver(pre_save, sender=AssinaturasMentor)
def pre_save_planos(instance, sender, created, **kwargs):
    if created:        
        instance.log_usuario_pk = instance.usuario.pk
        instance.log_usuario_email = instance.usuario.email
        instance.log_usuario_nome = instance.usuario.nome_completo
        instance.meses_desconto_restante = instance.assinatura_oferta.oferta_desconto.meses_desconto
        instance.meses_isencao_restante = instance.assinatura_oferta.oferta_desconto.meses_isencao

@receiver(pre_save, sender=FaturasMentores)
def pre_save_planos(instance, sender, created, **kwargs):
    if created:        
        log_usuario_pk = instance.usuario.pk
        log_usuario_email = instance.usuario.email
        log_usuario_nome = instance.usuario.nome_completo
        usuario_cpf = instance.assinatura.usuario_cpf

## Planos de pagamentos
# Qtd Alunos  ----    Valor   ----    Preço P/A
#     5               120,00          24,00
#     10              230,00          23,00
#     20              400,00          20,00
#     60              960,00          16,00
#     +X             960+(x 12)       ----
