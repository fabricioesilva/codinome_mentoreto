from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout, update_session_auth_hash
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView
from django.views import View
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.utils.translation import gettext as _
from django.db.models.query_utils import Q
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.conf import settings
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


from utils.resources import POLICY_LANGUAGES, check_user_is_regular
from usuarios.models import CustomUser, UserEmailCheck
from politicas.models import PolicyAcepted, PolicyRules
from .forms import CustomUserForm
from .decorators import mentores_required


# Create your views here.

def index_view(request):
    return render(request, 'usuarios/index.html', {})


@method_decorator([login_required, mentores_required], name='dispatch')
class HomeView(View):
    template_name = 'usuarios/home.html'

    def get(self, request, *args, **kwargs):
        from .models import Role
        if check_user_is_regular(request):
            return render(request, self.template_name)
        else:
            logout(request)
            messages.error(request, _('Ops! Usuário não encontrado!'))
            return redirect('login')


class CadastroView(CreateView):
    form_class = CustomUserForm
    template_name = 'usuarios/cadastro.html'
    success_url = 'login'

    def post(self, request, *args, **kwargs):
        form = CustomUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            if self.request.LANGUAGE_CODE in POLICY_LANGUAGES:
                user.policy_lang = self.request.LANGUAGE_CODE
            else:
                user.policy_lang = 'pt'

            user.save()
            PolicyAcepted.objects.create(
                user=user,
                policy=PolicyRules.objects.get(
                    language=user.policy_lang, active=True)
            )
            check_user = UserEmailCheck.objects.create(
                user=user,
            )
            form.send_mail(check_user.uri_key)
            messages.success(self.request,
                             _('Foi enviado um link para confirmação do seu email!'))

            # return super().form_valid(form)
        return redirect('usuarios:index')


class CustomLoginView(LoginView):
    redirect_authenticated_user = True

    def get_success_url(self):
        print(self)
        return reverse_lazy('usuarios:home')

    def form_invalid(self, form):
        messages.error(self.request, _('Ops! Usuário ou senha inválido!'))
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        user = form.get_user()
        if not user.email_checked:
            logout(self.request)
            messages.error(self.request, _('Ops! Usuário não encontrado ao entrar!'))
            return redirect('login')

        return super().form_valid(form)


def user_logout(request):
    logout(request)
    return redirect('usuarios:cadastro')


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = CustomUser.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "usuarios/password/password_reset_email.txt"
                    c = {
                        "email": user.email,
                        'domain': settings.DOMAIN,
                        'site_name': settings.SITE_NAME,
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    mensagem_email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, mensagem_email, settings.NO_REPLY,
                                  [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect("/password_reset/done/")
            else:
                messages.error(request, _("Email inválido"))
        else:
            messages.error(request, _("Erro no preenchimento."))

    password_reset_form = PasswordResetForm()
    return render(
        request=request, template_name="usuarios/password/password_reset.html",
        context={"password_reset_form": password_reset_form}
    )


def check_user_email(request, uri_key):
    if request.method == 'GET':
        # key = request.GET.get('uuid')
        ck_user = UserEmailCheck.objects.filter(
            uri_key=uri_key
        )
        if ck_user:
            user = ck_user[0].user
            if user:
                user.email_checked = True
                user.save()
                ck_user[0].save()
                # CustomUser.objects.get(
                #     username=user.username).update(email_checked=True)
                messages.success(request, _('Email confirmado com sucesso!'))
                return redirect('login')
            else:
                return redirect('login')
        else:
            return redirect('login')
    else:
        return redirect('usuarios:index')


def change_password_method(request, username):
    if request.method == 'GET':
        if request.user.is_anonymous:
            return redirect('login')
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(
                request, _('Senha alterada com sucesso!'))
            return redirect('usuarios:home', username=request.user)
        else:
            messages.error(request, _('Reveja o formulário!'))
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'usuarios/password/change_password.html', {
        'form': form
    })
