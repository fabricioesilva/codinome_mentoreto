from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import (
    AbstractUser,
    UserManager,
)
import uuid
from datetime import datetime
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.shortcuts import reverse
from django.db.models.signals import post_save
from django.utils.timezone import now

from politicas.models import PolicyRules, DevPolicyRules


# Create your models here.
FORMA_PAGAMENTO = [
    ("cart", _("Cartão de crédito")),
    ("ppix", _("Pix")),
    ("bole", _("Boleto")),
    ("depo", _("Depósito bancário"))
]


class CustomUser(AbstractUser):
    phone_regex = RegexValidator(
        regex=r'\d{11}$', message="O telefone para contato precisa \
        ser incerido com o DDD e os nove dígitos.")

    first_name = models.CharField(
        max_length=50, verbose_name=_('Nome'), null=True)
    last_name = models.CharField(
        max_length=50, verbose_name=_('Sobrenome'), null=True)
    username = models.CharField(
        max_length=50, unique=True, verbose_name=_('Usuário'))    
    email = models.EmailField(unique=True, verbose_name=_('E-mail'))
    phone_number = models.CharField(
        _('Telefone para contato'),
        help_text=_(
            'Insira o telefone para contaco com Whatsapp. Ex:(99)999999999.'),
        validators=[phone_regex], max_length=17, null=True, blank=True
    )
    cpf_usuario = models.CharField(_('CPF do usuário'), max_length=100, blank=True, null=True)

    endereco_faturamento = models.CharField(_('Endereço para faturamento'), max_length=100, blank=True, null=True)

    policy_lang = models.CharField(_("Língua de aceitação da política"),
                                   max_length=5,
                                   null=True,
                                   blank=True,
                                   default='pt',
                                   choices=PolicyRules.LANG
                                   )
    dev_policy_lang = models.CharField(
        _("Língua de aceitação da política para desenvolvedores"),
        max_length=5,
        null=True,
        blank=True,
        default='pt',
        choices=DevPolicyRules.LANG
    )

    slug = models.SlugField(unique=True, blank=True, null=True, max_length=255)

    user_since = models.DateTimeField(
        _("Usuário desde"), null=True, blank=True, auto_now_add=True
    )
    email_checked = models.BooleanField(_("Email verificado"),
                                        default=False)

    objects = UserManager()

    REQUIRED_FIELDS = [
        'first_name', 'phone_number', 'email',
    ]

    @property
    def nome_completo(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            tema = str(self.email) + str(self.username)
            slug = f'{slugify(tema)}'
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def get_absolute_url(self):
        return reverse('usuarios:home_mentor')


class Preferences(models.Model):
    '''
    Preferências do usuário
    '''
    ROLE_CHOICES = (
        (1, 'Estudante'),
        (2, 'Mentor'),
        (3, 'Sempre perguntar'),
        (4, 'Inicial')
    )
    usuario = models.OneToOneField(CustomUser,
                                   verbose_name=_('Preferências do usuário'),
                                   on_delete=models.CASCADE,
                                   blank=True, null=True,
                                   )

    login_redirect = models.SmallIntegerField(
        verbose_name=_('Ir direto para o painel preferido ao iniciar sessão'),
        default=4, choices=ROLE_CHOICES
    )

    def __str__(self):
        return self.usuario.first_name


class PerfilCobranca(models.Model):
    usuario = models.ForeignKey(CustomUser, verbose_name=_("Endereço de cobrança"), on_delete=models.CASCADE)
    telefone1 = models.CharField(_('Telefone de contato com o DDD*'), max_length=25, null=True)
    telefone2 = models.CharField(_('Outro telefone de contato com o DDD'), max_length=25, null=True, blank=True)
    endereco_rua = models.CharField(_("Rua*"), max_length=30, null=True)
    endereco_numero = models.CharField(_("Número*"), max_length=10, null=True)
    endereco_complemento = models.CharField(_("Complemento"), help_text=_("Ex: Apto 601, ou Lote 40"), max_length=30, null=True)
    endereco_bairro = models.CharField(_("Bairro*"), max_length=30, null=True)    
    endereco_cidade = models.CharField(_("Cidade*"), max_length=30, null=True)
    endereco_cep = models.CharField(_("CEP"), max_length=30, null=True)
    endereco_estado = models.CharField(_("Estado"), max_length=2, null=True)
    endereco_resumido = models.CharField(_("Resumo"), null=True, blank=True, max_length=200)
    cpf_cnpj = models.CharField(_("CPF/CNPJ"), null=True, blank=True, max_length=35)
    perfil_pagamento = models.CharField(_("Forma de pagamento"), null=True, max_length=4, default='ppix', choices=FORMA_PAGAMENTO)

    def save(self, *args, **kwargs):
        self.endereco_resumido = f"{self.telefone1}, {self.telefone2}, {self.endereco_rua} {self.endereco_numero}, {self.endereco_complemento}, {self.endereco_bairro}, {self.endereco_cep}, {self.endereco_cidade}, {self.endereco_estado}."
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return self.endereco_resumido

class UserEmailCheck(models.Model):
    user = models.ForeignKey("usuarios.CustomUser", verbose_name=_(
        "Usuário"), on_delete=models.SET_NULL, null=True, blank=True)
    user_email = models.EmailField(
        _("Email do usuário"), max_length=254)
    uri_key = models.UUIDField(_("Chave de acesso da url"),
                               primary_key=False, default=uuid.uuid4)
    date = models.DateTimeField(
        _("Data do email"), null=True, blank=True, default=now)
    confirmed = models.DateTimeField(
        _("Data da confimação"), null=True, blank=True)

    def save(self, *args, **kwargs):
        self.user_email = self.user.email
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.user_email

    class Meta:
        ordering = ['-date']


class DeletedUser(models.Model):
    user_id = models.IntegerField(_("Id de usuário removido"))
    email = models.EmailField(_("Email de usuário removido"), max_length=254)
    user_since = models.DateTimeField(
        _("Usuário desde"), null=True, blank=True
    )
    date = models.DateTimeField(
        _("Data da remoçao do usuário"), default=datetime.now)
    reason = models.CharField(
        _("Razão da remoção do usuário"), max_length=50,
        default="Solicitado pelo usuário."
    )

    def __str__(self):
        return f'Removed {self.user_id}'


class UserMessages(models.Model):
    to_user = models.ForeignKey("usuarios.CustomUser", verbose_name=_(
        "Usuário que recebeu"), on_delete=models.SET_NULL, null=True,
        related_name='receiver'
    )
    user_email = models.EmailField(
        _("Email do usuário que recebeu"),
        max_length=254, blank=True, null=True
    )
    text = models.CharField(_("Texto da mensagem"),
                            max_length=50, null=True, blank=True)
    date = models.DateTimeField(_("Data da mensagem"), auto_now_add=True)

    openned = models.BooleanField(_("Visualizada"), default=False)

    def __str__(self):
        return self.user_email

    def save(self, *args, **kwargs):
        self.user_email = self.to_user.email
        return super().save(*args, **kwargs)


def cria_preferences_post_save(sender, instance, created, **kwargs):
    if created:
        Preferences.objects.create(
            usuario=instance
        )


post_save.connect(cria_preferences_post_save, CustomUser)

"""
SNIPETS PARA MENSAGENS
def set_msg_post_vote_save(sender, instance, created, **kwargs):
    if created:
        UsuariosMessages.objects.create(
            to_user=instance.pergunta.author,
            text=_('Sua pesquisa recebeu um voto.'),
            pergunta_related=instance.pergunta.id
        )
"""
