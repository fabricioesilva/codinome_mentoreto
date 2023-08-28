# from django.db import models
# from usuarios.models import CustomUser
# from django.utils.translation import gettext_lazy as _
# from django.utils import timezone
# # Create your models here.


# class PlanosAssinatura(models.Model):
#     criado_por = models.ForeignKey(
#         CustomUser, verbose_name=_('Criado por'),
#         null=True, blank=True, on_delete=models.SET_NULL)
#     titulo = models.CharField(_('Nome comercial'), max_length=100)
#     descricao = models.TextField(_('Descrição'), null=True, blank=True)
#     criado_em = models.DateTimeField(_('Criado em'), default=timezone.now)
#     criado_por_pk = models.PositiveIntegerField(null=True, blank=True)
#     criado_por_email = models.EmailField(null=True, blank=True)
#     criado_por_nome = models.CharField(max_length=50, null=True, blank=True)
#     ativo = models.BooleanField(_('Em uso'), default=False)
#     preco = models.FloatField()
#     desconto = models.ManyToManyField('mentorias.Descontos')

#     def save(self, *args, **kwargs):
#         if not self.criado_por_pk:
#             self.criado_por_pk = self.criado_por.pk
#         if not self.criado_por_email:
#             self.criado_por_email = self.criado_por.email
#         if not self.criado_por_nome:
#             self.criado_por_nome = self.criado_por.first_name
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return self.titulo


# class Descontos(models.Model):
#     criado_por = models.ForeignKey(
#         CustomUser, verbose_name=_('Criado por'),
#         null=True, blank=True, on_delete=models.SET_NULL)
#     desconto = models.FloatField(default=0.00)
#     titulo = models.CharField(_('Nome comercial do desconto'), max_length=50)
#     abreviatura = models.CharField(_('Abreviatura'), max_length=20, null=True, blank=True)
#     descricao = models.TextField(_('Descrição'), null=True, blank=True)
#     criado_em = models.DateTimeField(_('Criado em'), default=timezone.now)
#     criado_por_pk = models.PositiveIntegerField(null=True, blank=True)
#     criado_por_email = models.EmailField(null=True, blank=True)
#     criado_por_nome = models.CharField(max_length=50, blank=True, null=True)
#     ativo = models.BooleanField(_('Em uso'), default=False)
#     desconto = models.FloatField(default=0)
#     prazo_duracao = models.PositiveIntegerField(_('Dias duração do desconto'), null=True, blank=True)
#     encerramento = models.DateTimeField(_('Encerramento'), null=True, blank=True)

#     def save(self, *args, **kwargs):
#         if not self.criado_por_pk:
#             self.criado_por_pk = self.criado_por.pk
#         if not self.criado_por_email:
#             self.criado_por_email = self.criado_por.email
#         if not self.criado_por_nome:
#             self.criado_por_nome = self.criado_por.first_name
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return self.titulo


# class AssinaturasMentor(models.Model):
#     usuario = models.ForeignKey(CustomUser, verbose_name=_('Usuário'), null=True, blank=True, on_delete=models.SET_NULL)
#     plano = models.ForeignKey(
#         PlanosAssinatura, verbose_name=_('Plano de assinatura'),
#         on_delete=models.SET_NULL, null=True, blank=True)
#     criada_em = models.DateTimeField(_('Data assinatura'), default=timezone.now)
#     encerra_em = models.DateField(_('Encerra em'), null=True, blank=True)
#     pagamento = models.JSONField(_("Controle de pagamentos"), null=True, blank=True)
#     usuario_pk = models.PositiveIntegerField(_("Id do usuário"), null=True, blank=True)
#     usuario_email = models.EmailField(_('Email do usuário'), null=True, blank=True)
#     usuario_nome = models.CharField(_('Nome do usuário'), max_length=100, null=True, blank=True)
#     desconto = models.ForeignKey('mentorias.Descontos', null=True, blank=True, on_delete=models.SET_NULL)

#     def save(self, *args, **kwargs):
#         if not self.usuario_pk:
#             self.usuario_pk = self.usuario.pk
#         if not self.usuario_email:
#             self.usuario_email = self.usuario.email
#         if not self.usuario_nome:
#             self.usuario_nome = self.usuario.first_name
#         super().save(*args, **kwargs)
