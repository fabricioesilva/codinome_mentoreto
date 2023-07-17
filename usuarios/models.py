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

from politicas.models import PolicyRules, DevPolicyRules

# Create your models here.


class CustomUser(AbstractUser):
    phone_regex = RegexValidator(
        regex=r'\d{11}$', message="O telefone para contato precisa \
        ser incerido com o DDD e os nove dígitos.")

    first_name = models.CharField(
        max_length=50, verbose_name=_('Nome'), null=True, blank=True)
    last_name = models.CharField(
        max_length=50, verbose_name=_('Sobrenome'), null=True, blank=True)
    username = models.CharField(
        max_length=50, unique=True, verbose_name=_('Usuário'))
    email = models.EmailField(unique=True, verbose_name=_('E-mail'))
    phone_number = models.CharField(
        _('Telefone para contato'),
        help_text=_(
            'Insira o telefone para contaco com Whatsapp. Ex:(99)999999999.'),
        validators=[phone_regex], max_length=17, null=True, blank=True
    )
    cnpj_faturamento = models.CharField(_('CNPJ/CPF para faturamento'), max_length=100, blank=True, null=True)

    endereco_faturamento = models.CharField(_('Endereço para faturamento'), max_length=100, blank=True, null=True)

    policy_lang = models.CharField(_("Língua de aceitação da política"),
                                   max_length=5,
                                   null=True,
                                   blank=True,
                                   default='en',
                                   choices=PolicyRules.LANG
                                   )
    dev_policy_lang = models.CharField(
        _("Língua de aceitação da política para desenvolvedores"),
        max_length=5,
        null=True,
        blank=True,
        default='en',
        choices=DevPolicyRules.LANG
    )

    slug = models.SlugField(unique=True, blank=True, null=True)

    user_since = models.DateTimeField(
        _("Usuário desde"), null=True, blank=True, auto_now_add=True
    )
    email_checked = models.BooleanField(_("Email verificado"),
                                        default=False)

    objects = UserManager()

    REQUIRED_FIELDS = [
        'first_name', 'phone_number', 'email',
    ]

    def save(self, *args, **kwargs):
        if not self.slug:
            tema = str(self.email) + str(self.username)
            slug = f'{slugify(tema)}'
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

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
        return self.user.first_name


class UserEmailCheck(models.Model):
    user = models.ForeignKey("usuarios.CustomUser", verbose_name=_(
        "Usuário"), on_delete=models.SET_NULL, null=True, blank=True)
    user_email = models.EmailField(
        _("Email do usuário"), max_length=254)
    uri_key = models.UUIDField(_("Chave de acesso da url"),
                               primary_key=False, default=uuid.uuid4)
    date = models.DateTimeField(
        _("Data do email"), null=True, blank=True, default=datetime.now)
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
