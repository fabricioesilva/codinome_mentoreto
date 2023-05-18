from django.core.exceptions import ValidationError
from django.db import models
# from django.utils.text import slugify
from django.contrib.auth.models import (
    AbstractUser,
    UserManager,
)
import uuid
from datetime import datetime
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.shortcuts import reverse

from politicas.models import PolicyRules, DevPolicyRules


class Role(models.Model):
    '''
    The Role entries are managed by the system,
    automatically created via a Django data migration.
    (if role == Role.ADMIN:)
    '''
    ESTUDANTE = 1
    MENTOR = 2
    ADM = 5
    ROLE_CHOICES = (
        (ESTUDANTE, 'estudante'),
        (MENTOR, 'mentor'),
        (ADM, 'adm'),
    )

    id = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, primary_key=True)

    def __str__(self):
        return self.get_id_display()


# Create your models here.
class CustomUser(AbstractUser):
    roles = models.ManyToManyField(Role)
    phone_regex = RegexValidator(
        regex=r'\d{11}$', message="Ó telefone para contato precisa \
            ser incerido com o DDD e os nove dígitos.")
    first_name = models.CharField(
        max_length=100, verbose_name=_('Nome'), null=True, blank=True)
    last_name = models.CharField(
        max_length=100, verbose_name=_('Sobrenome'), null=True, blank=True)
    username = models.CharField(
        max_length=30, unique=True, verbose_name=_('Usuário'))
    email = models.EmailField(unique=True, verbose_name=_('E-mail'))
    phone_number = models.CharField(
        _('Telefone para contato'),
        help_text=_(
            'Insira o telefone para contaco com Whatsapp. Ex:(99)999999999.'),
        validators=[phone_regex], max_length=17, null=True, blank=True
    )

    business = models.BooleanField(_("Sou empresa"),
                                   default=False)

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

    user_since = models.DateTimeField(_("Usuário desde"),
                                      blank=True, null=True, auto_now_add=False, default=datetime.now)
    email_checked = models.BooleanField(_("Email verificado"),
                                        default=False)

    objects = UserManager()

    REQUIRED_FIELDS = [
        'first_name', 'phone_number', 'email',
    ]

    def clean(self):
        if self.business is False:
            if not self.last_name:
                raise ValidationError({'last_name': "Informe um sobrenome."})

        # super().clean(self)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('home')


class UserEmailCheck(models.Model):
    user = models.OneToOneField("usuarios.CustomUser", verbose_name=_(
        "Usuário"), on_delete=models.SET_NULL, null=True, blank=True)
    user_email = models.EmailField(
        _("Email do usuário"), max_length=254)
    uri_key = models.UUIDField(_("Chave de acesso da url"),
                               primary_key=False, default=uuid.uuid4)
    date = models.DateTimeField(
        _("Data do email"), auto_now_add=True, null=True)
    confirmed = models.DateTimeField(
        _("Data da confimação"), auto_now=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.user_email = self.user.email
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.user_email


class DeletedUser(models.Model):
    user_id = models.IntegerField(_("Id de usuário removido"))
    email = models.EmailField(_("Email de usuário removido"), max_length=254)
    user_since = models.DateTimeField(
        _("Usuário desde"), null=True, blank=True, auto_now=False,
        auto_now_add=False
    )
    date = models.DateTimeField(
        _("Data da remoçao do usuário"), auto_now_add=True)
    reason = models.CharField(
        _("Razão da remoção do usuário"), max_length=50,
        default="Self removed"
    )

    def __str__(self):
        return f'Removed {self.user_id}'


class UserMessages(models.Model):
    to_user = models.ForeignKey("usuarios.CustomUser", verbose_name=_(
        "Usuário que recebeu"), on_delete=models.CASCADE,
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
