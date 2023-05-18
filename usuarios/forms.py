from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core.mail import EmailMessage
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from .models import CustomUser


class CustomUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    @transaction.atomic
    def save(self, commit=True):
        user = super(CustomUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

    def send_mail(self, uri_key, email=None, user=None):
        if email is None:
            email = self.cleaned_data.get('email')
            user = self.cleaned_data.get('username')
        pre_text = _(', clique no link para validar o seu email ')
        content = f"{user}{pre_text}, {settings.LOCALHOST_URL}check/email/{uri_key}"
        email = EmailMessage(
            subject=_('Bem vindo ao e-Pesquisa'),
            body=content,
            from_email=settings.NOREPLY_EMAIL,
            to=[email, ],
            headers={'Reply-to': settings.NOREPLY_EMAIL}
        )
        email.send()

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'business', 'password1', 'password2', 'email']
        required_fields = ['first_name', 'username', 'business', 'password1', 'password2', 'email']
