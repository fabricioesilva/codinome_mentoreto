from django.db import models
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import slugify
from django.db import models
from django.utils.translation import gettext_lazy as _
# from django.db.models.signals import post_save
from django.template.defaultfilters import slugify


class PolicyRules(models.Model):
    LANG = (
        ('pt-br', 'Portuguese'),
        ('en', 'English')
    )
    title = models.CharField(_("Título da regra"), max_length=50, null=True)
    text = models.TextField(_("Conteúdo da regra"))
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
    policy_user_id = models.IntegerField(_("Id do usuário que criou a regra"),
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
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = _('Políticas')
        verbose_name_plural = _('Política')


class PolicyAcepted(models.Model):
    user = models.ForeignKey('usuarios.CustomUser', verbose_name=_(
        "Usuário"), on_delete=models.SET_NULL, null=True)
    user_email = models.EmailField(_("Email do usuário"), max_length=254)
    profile_id = models.IntegerField(_("Id do usuário"))
    acept_date = models.DateTimeField(
        _("Data da aceitação"), auto_now_add=True)
    policy = models.ForeignKey(PolicyRules, verbose_name=_(
        "Política de privacidade"), on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.user_email = self.user.email
        self.profile_id = self.user.id
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user}, {self.acept_date}, {self.policy}'


class PolicyChanges(models.Model):
    user_email = models.EmailField(
        _("Email do usuário que criaou ou modificou a política"),
        max_length=254, null=True, blank=True)
    policy_user_id = models.IntegerField(
        _("Id do usuário que criaou ou modificou a política"),
        null=True, blank=True)
    policy_title = models.CharField(
        _("Título da política"), max_length=50, null=True, blank=True)
    policy_status = models.CharField(_("Estado da política(ativa ou não)"),
                                     blank=True,
                                     null=True,
                                     max_length=10)
    policy_content = models.TextField(
        _("Conteúdo da política"), null=True, blank=True)
    policy_pkey = models.IntegerField(
        _("Id da política"), null=True, blank=True)
    mod_date = models.DateTimeField(
        _("Data da modificação"), auto_now_add=True, null=True)
    action = models.CharField(
        _("Ação realizada"), max_length=50, null=True, blank=True)

    def __str__(self):
        return f'{self.action}, {self.policy_user_id}, {self.policy_title}'

    class Meta:
        verbose_name_plural = _('Modificações na política')


class DevPolicyRules(models.Model):
    LANG = (
        ('pt-br', 'Portuguese'),
        ('en', 'English')
    )
    title = models.CharField(_("Título da regra"), max_length=50, null=True)
    text = models.TextField(_("Conteúdo da regra"))
    begin_date = models.DateTimeField(
        _("Data do início da vigência"), auto_now=False, auto_now_add=False)
    end_date = models.DateTimeField(
        _("Data do fim da vigência"), auto_now=False, auto_now_add=False, null=True, blank=True)
    active = models.BooleanField(
        _("Regra está vigente(regra em uso)"), default=False)
    criada_em = models.DateTimeField(
        _("Data da criação"), auto_now_add=True, null=True, blank=True)
    language = models.CharField(
        _("Lingua"),
        max_length=5,
        null=False,
        blank=False,
        default='pt-br',
        choices=LANG
    )
    user = models.ForeignKey("usuarios.CustomUser",
                             verbose_name=_("Usuário que criou a regra"),
                             on_delete=models.SET_NULL, null=True,
                             blank=True
                             )
    user_email = models.EmailField(_("Email do usuário que criou a regra"),
                                   max_length=254, null=True, blank=True)
    policy_user_id = models.IntegerField(_("Id do usuário que criou a regra de desenvolvedores"),
                                         null=True, blank=True)
    slug = models.SlugField('Slug', max_length=100, blank=True, editable=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = _('Políticas para desenvolvedores')


class DevPolicyAcepted(models.Model):
    user = models.ForeignKey('usuarios.CustomUser', related_name='dev_policy', verbose_name=_(
        "Usuário"), on_delete=models.SET_NULL, null=True)
    user_email = models.EmailField(_("Email do usuário"), max_length=254)
    profile_id = models.IntegerField(_("Id do usuário"))
    acept_date = models.DateTimeField(
        _("Data da aceitação"), auto_now_add=True)
    policy = models.ForeignKey(DevPolicyRules, verbose_name=_(
        "Política para desenvolvedores"), on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.user_email = self.user.email
        self.profile_id = self.user.id
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user}, {self.acept_date}, {self.policy}'


class DevPolicyChanges(models.Model):
    user_email = models.EmailField(
        _("Email do usuário que criaou ou modificou a política"),
        max_length=254, null=True, blank=True)
    policy_user_id = models.IntegerField(
        _("Id do usuário que criaou ou modificou a política"),
        null=True, blank=True)
    policy_title = models.CharField(
        _("Título da política"), max_length=50, null=True, blank=True)
    policy_status = models.CharField(_("Estado da política(ativa ou não)"),
                                     blank=True,
                                     null=True,
                                     max_length=10)
    policy_content = models.TextField(
        _("Conteúdo da política"), null=True, blank=True)
    policy_pkey = models.IntegerField(
        _("Id da política"), null=True, blank=True)
    mod_date = models.DateTimeField(
        _("Data da modificação"), auto_now_add=True, null=True)
    action = models.CharField(
        _("Ação realizada"), max_length=50, null=True, blank=True)

    def __str__(self):
        return f'{self.action}, {self.policy_user_id}, {self.policy_title}'

    class Meta:
        verbose_name_plural = _(
            "Modificações na política para desenvolvedores")


class AboutUs(models.Model):
    LANG = (
        ('pt-br', 'Portuguese'),
        ('en', 'English')
    )
    title = models.CharField(_("Título do texto"), max_length=50, null=True)
    text = models.TextField(_("Conteúdo do texto"))
    active = models.BooleanField(
        _("Texto está vigente(em uso)"), default=False)
    criada_em = models.DateTimeField(
        _("Data da criação"), auto_now_add=True, null=True, blank=True)
    language = models.CharField(
        _("Lingua"),
        max_length=5,
        null=False,
        blank=False,
        default='pt-br',
        choices=LANG
    )
    user = models.ForeignKey("usuarios.CustomUser",
                             verbose_name=_("Usuário que criou o texto"),
                             on_delete=models.SET_NULL, null=True,
                             blank=True
                             )
    user_email = models.EmailField(_("Email do usuário que criou o texto"),
                                   max_length=254, null=True, blank=True)
    staff_id = models.IntegerField(_("Id do usuário que criou o texto"),
                                   null=True, blank=True)
    slug = models.SlugField('Slug', max_length=100, blank=True, editable=False)
    pkey = models.IntegerField(
        _("Id do texto"), null=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = _('Sobre Nós textos')


class AboutUsChanges(models.Model):
    user_email = models.EmailField(
        _("Email do usuário que criaou ou modificou o texto"),
        max_length=254, null=True, blank=True)
    user_id = models.IntegerField(
        _("Id do usuário que criaou ou modificou o texto"),
        null=True, blank=True)
    title = models.CharField(
        _("Título do texto"), max_length=50, null=True, blank=True)
    status = models.CharField(_("Estado do texto(ativo ou não)"),
                              blank=True,
                              null=True,
                              max_length=10)
    content = models.TextField(
        _("Conteúdo do texto"), null=True, blank=True)
    pkey = models.IntegerField(
        _("Id do texto"), null=True, blank=True)
    mod_date = models.DateTimeField(
        _("Data da modificação"), auto_now_add=True, null=True)
    action = models.CharField(
        _("Ação realizada"), max_length=50, null=True, blank=True)

    def __str__(self):
        return f'{self.action}, {self.user_id}, {self.title}'

    class Meta:
        verbose_name_plural = _('Modificações no texto "Sobre nós"')

