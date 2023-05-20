from django.db import models
from usuarios.models import CustomUser
from django.utils.translation import gettext_lazy as _
from datetime import datetime
# Create your models here.


# class Programas(models.Model):
#     mentor = models.ForeignKey(CustomUser, blank=True, null=True,
#                                on_delete=models.SET_NULL)
#     mentor_email = models.EmailField('Email do Mentor', blank=True, null=True)
#     nome = models.CharField(verbose_name=_('', blank=False, null=False))
#     created = models.DateTimeField(_('Data criação:'), blank=True, null=True, auto_now_add=False, default=datetime.now)
