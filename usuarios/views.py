# from django.contrib.auth.views import LoginView
from django.contrib.auth import logout, update_session_auth_hash
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView
from django.views import View
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.translation import gettext as _
from django.core.mail import BadHeaderError, EmailMessage, get_connection, send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models import Count
from datetime import date, timedelta
import threading
import zoneinfo
import datetime

from usuarios.models import (
    CustomUser, UserEmailCheck, Preferences, DeletedUser, PerfilCobranca
)
from politicas.models import PolicyAcepted, PolicyRules
from .forms import (
    CustomUserForm,
    EditProfilerForm,
    EditUserEmailForm,
    EditPreferencesForm,
    ConfirmPasswordForm
)
from mentorias.models import ( 
    Mentoria, MatriculaAlunoMentoria, Alunos
)
from assinaturas.models import (
    OfertasPlanos, PrecosAssinatura, TermosDeUso, TermosAceitos, AssinaturasMentor, PerfilCobranca
)
from assinaturas.views import get_faixa_de_exemplo
from utils.resources import POLICY_LANGUAGES

# Create your views here.
def index_view(request):
    if request.user.is_authenticated:
        return redirect("usuarios:home_mentor")
    return render(request, 'usuarios/index.html', {})


def home_view(request):
    if request.user.is_authenticated:
        preference = request.user.preferences.login_redirect
        if request.user.preferences.login_redirect == 1:
            return redirect('usuarios:home_student')
        elif preference == 2:
            return redirect('usuarios:home_mentor')
        else:
            return render(request, 'usuarios/home.html', {})
    else:
        return redirect(request, 'usuarios:index')


@method_decorator([login_required], name='dispatch')
class HomeMentorView(ListView):
    template_name = 'usuarios/home_mentor.html'
    model = Mentoria
    
    def get_queryset(self, *args, **kwargs): 
        qs = super(HomeMentorView, self).get_queryset(*args, **kwargs) 
        qs = qs.filter(
            mentor=self.request.user, ativa=True
            ).alias(nb=Count('matriculas_mentoria', filter=Q(matriculas_mentoria__ativa=True))).order_by('-nb')
        return qs

    def post(self, request, *args, **kwargs):
        qs = self.get_queryset(**kwargs)
        situacao_enviada = 'pendente'
        situacao_enviada = request.POST.get('filtros')
        return render(request, self.template_name, {"object_list":qs, 'situacao': situacao_enviada})


def buscar_geral(request):
    ctx = {}
    template_name = 'usuarios/buscar_geral.html'
    if request.method == 'POST':
        matriculas = MatriculaAlunoMentoria.objects.filter(
                mentoria__in=Mentoria.objects.filter(mentor=request.user)).filter( 
                Q(aluno__nome_aluno__icontains=request.POST.get('search')) |
                Q(aluno__email_aluno__iexact=request.POST.get('search'))
            )
        alunos = Alunos.objects.filter(mentor=request.user).filter(
            Q(nome_aluno__iexact=request.POST.get('search')) |
            Q(email_aluno__iexact=request.POST.get('search')) |
            Q(nome_aluno__icontains=request.POST.get('search'))
        )
        ctx = {
            'expressao': request.POST.get('search'),
            'matriculas': matriculas,
            "alunos": alunos
        }
        return render(request, template_name, ctx)
    else:
        return render(request, template_name, ctx)        


class CadastroView(CreateView):
    form_class = CustomUserForm
    template_name = 'usuarios/cadastro.html'
    success_url = 'login'

    def setup(self, request, *args, **kwargs):
        hoje = date.today()
        self.oferta_disponivel = OfertasPlanos.objects.filter(encerra_em__gte=hoje, promocional=True).exclude(inicia_vigencia__gte=hoje).first()
        if not self.oferta_disponivel:
            self.oferta_disponivel = OfertasPlanos.objects.filter(encerra_em__gte=hoje, promocional=False).exclude(inicia_vigencia__gte=hoje).first()
        if self.oferta_disponivel.desconto_incluido:
            self.oferta_percentual = self.oferta_disponivel.desconto_incluido.percentual_desconto
        else:
            self.oferta_percentual = None
        self.plano_disponivel = PrecosAssinatura.objects.filter(ativo=True).first()
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['oferta_disponivel'] = self.oferta_disponivel
        ctx['oferta_percentual'] = self.oferta_percentual
        return ctx

    def get(self, *args, **kwargs):   
        if self.request.user.is_authenticated:
            return redirect("usuarios:home_mentor")
        else:
            return super().get(*args, **kwargs)

    def form_invalid(self, form):
        messages.error(self.request, self.error_message)
        return super().form_invalid(form)        

    def post(self, request, *args, **kwargs):    
        form = CustomUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            if self.request.LANGUAGE_CODE in POLICY_LANGUAGES:
                user.policy_lang = self.request.LANGUAGE_CODE
            else:
                user.policy_lang = 'pt'
            user.save()
            politica_aceita = PolicyAcepted.objects.create(
                user=user,
                policy=PolicyRules.objects.get(
                    language=user.policy_lang, active=True)
            )
            termo=TermosDeUso.objects.filter(
                language=user.policy_lang, begin_date__lt=datetime.datetime.now(tz=zoneinfo.ZoneInfo(settings.TIME_ZONE)), end_date=None, publico_allvo='mentor')
            if not termo:
                termo=TermosDeUso.objects.get(
                    language='pt', active=True
                )
            else:
                termo = termo[0]
            termo_aceito = TermosAceitos.objects.create(
                user=user,
                termo=termo
            )      
            check_user = UserEmailCheck.objects.create(
                user=user,
            )
            # Contratação de assinatura
            assinar_plano_no_cadastro(request, user)
            try:
                form.send_mail(check_user.uri_key, politica=politica_aceita, termo=termo_aceito)
            except BadHeaderError:
                print("Erro ao enviar o email.")
            messages.success(self.request,
                             _('Em breve você receverá um email para confirmação do seu cadastro!'))
        else:
            return super().get(request, *args, **kwargs)
        return redirect('usuarios:index')


def user_logout(request):
    logout(request)
    return redirect('usuarios:cadastro')

def check_user_email(request, uri_key):
    if request.method == 'GET':
        ck_user = UserEmailCheck.objects.filter(
            uri_key=uri_key
        ).first()
        if ck_user:
            user = ck_user.user
            if user:
                user.email_checked = True
                user.save()
                ck_user.save()
                ck_user.confirmed = datetime.datetime.now(tz=zoneinfo.ZoneInfo(settings.TIME_ZONE))
                ck_user.save()
                mail_trheading = threading.Thread(target=email_threading_bem_vindo_professor, args=(request, user))
                mail_trheading.start()
                logout(request)
                messages.success(request, _('Email confirmado com sucesso!'))
                return redirect('login')
            else:
                return redirect('login')
        else:
            return redirect('login')
    else:
        return redirect('usuarios:index')


def email_threading_bem_vindo_professor(request, user):
    try:
        with get_connection(
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            use_tls=settings.EMAIL_USE_TLS
        ) as connection:
            subject = f"Seja bem-vindo ao ExpertZone - Sua plataforma de ensino completa!"
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email]
            email_template_name = "usuarios/email_bem_vindo_professor.txt"
            context = {
                'site_name': settings.SITE_NAME,
                'user': user,
            }
            mensagem_email = render_to_string(email_template_name, context)
            EmailMessage(subject, mensagem_email, email_from,
                recipient_list, connection=connection).send()
    except BadHeaderError:
        messages.warning(request, _('Erro ao enviar emails.'))


def change_password_method(request):
    if request.method == 'POST':
        if request.user.is_anonymous:
            return redirect('login')
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            logout(request)
            messages.success(
                request, _('Senha alterada com sucesso!'))
            return redirect('login')
        else:
            messages.error(request, _('Reveja o formulário!'))
    else:
        if request.user.is_anonymous:
            return redirect('login')
        form = PasswordChangeForm(request.user)
    return render(request, 'usuarios/change_password.html', {
        'form': form
    })


@method_decorator([login_required], name='dispatch')
class ProfileView(View):
    template_name = 'usuarios/profile_view.html'

    def get(self, *args, **kwargs):
        return render(self.request, self.template_name)


@method_decorator([login_required], name='dispatch')
class EditPreferencesView(UpdateView):
    model = Preferences
    template_name = 'usuarios/edit_preferences.html'
    form_class = EditPreferencesForm
    success_url = reverse_lazy('usuarios:profile_view')


@method_decorator([login_required], name='dispatch')
class EditProfileView(UpdateView):
    form_class = EditProfilerForm
    model = CustomUser
    template_name = 'usuarios/edit_profile.html'
    success_url = reverse_lazy('usuarios:profile_view')    

    def get_form_kwargs(self):
        kwargs = super(EditProfileView, self).get_form_kwargs()
        kwargs['instance'] = self.request.user  # Profile object
        return kwargs


def edit_user_email(request):
    if request.method == 'POST':
        password = request.POST['password']
        email1 = request.POST['email1']
        senha_correta = request.user.check_password(password)
        if not senha_correta:
            messages.error(request, _('Senha incorreta!'))
            form = EditUserEmailForm(request.POST)
            return render(request, 'usuarios/edit_user_email.html', {'form': form})
        elif CustomUser.objects.filter(email=email1).exists():
            messages.error(request, 'Email já existe.')
            form = EditUserEmailForm(request.POST)
            return render(request, 'usuarios/edit_user_email.html', {'form': form})
        else:
            form = EditUserEmailForm(request.POST)
            request.user.email_checked = False
            request.user.email = email1
            request.user.save()
            check_user = UserEmailCheck.objects.create(
                user=request.user,
            )
            try:
                form.send_mail(check_user.uri_key, email_to=email1, user=request.user)
            except BadHeaderError:
                print("Erro ao enviar o email.")
            logout(request)
            messages.success(request,
                             _('Você receberá um email, para confirmação do seu novo email!'))
            return redirect('usuarios:index')
    form = EditUserEmailForm(request.POST or None)
    return render(request, 'usuarios/edit_user_email.html', {'form': form})


def delete_user(request, username):
    if request.method == 'GET':
        if username != request.user.username:
            messages.error(request, _('Usuário inválido!'))
            return redirect('usuarios:index')
        context = {'form': ConfirmPasswordForm(
            request.POST or None, instance=request.user), }
        return render(request, 'usuarios/check_password.html',
                      context)

    if request.method == 'POST':
        if username != request.user.username:
            messages.error(request, _('Usuário inválido!'))
            return redirect('usuarios:index')
        form = ConfirmPasswordForm(request.POST, instance=request.user)
        if form.is_valid():
            DeletedUser.objects.create(
                user_id=request.user.id,
                email=request.user.email,
                user_since=request.user.user_since
            )
            request.user.delete()
            messages.add_message(request, messages.SUCCESS,
                                 _('Perfil removido.'))
            return redirect('usuarios:index')
        else:
            messages.add_message(request, messages.ERROR,
                                 _('Erro na digitação da senha.'))
            form = ConfirmPasswordForm()
            return render(request, 'usuarios/check_password.html',
                          {"form": form})

def assinar_plano_no_cadastro(request, user):
    hoje = date.today()
    oferta_disponivel = OfertasPlanos.objects.filter(encerra_em__gte=hoje, promocional=True).exclude(inicia_vigencia__gte=hoje).first()
    if not oferta_disponivel:
        oferta_disponivel = OfertasPlanos.objects.filter(encerra_em__gte=hoje, promocional=False).exclude(inicia_vigencia__gte=hoje).first()
    if not oferta_disponivel:
        messages.error(request, "Erro ao encontrar oferta! Tente novamente mais tarde.")
    ano_seguinte = date(year=hoje.year+1, month=hoje.month, day=28)    
    PerfilCobranca.objects.create(usuario=user)
    AssinaturasMentor.objects.create(
        mentor=user,
        oferta_contratada=oferta_disponivel,
        inicia_vigencia=hoje,
        encerra_em=ano_seguinte,        
    )
    termo=TermosDeUso.objects.filter(
                language=user.policy_lang, begin_date__lt=datetime.datetime.now(tz=zoneinfo.ZoneInfo(settings.TIME_ZONE)), end_date=None, publico_allvo='mentor')
    if not termo:
        termo=TermosDeUso.objects.get(
        language='pt', active=True)
    else:
        termo = termo[0]
    TermosAceitos.objects.create(
    user=user,
    termo=termo
    )
    return

def simulacao_precos(request):
    template_name="usuarios/simulacao_precos.html"
    data_atual = date.today()
    plano_disponivel = OfertasPlanos.objects.filter(encerra_em__gte=data_atual, promocional=True).exclude(inicia_vigencia__gte=data_atual).first()
    if not plano_disponivel:
        plano_disponivel = OfertasPlanos.objects.filter(encerra_em__gte=data_atual, promocional=False).exclude(inicia_vigencia__gte=data_atual).first()    
    faixas = []
    precos_dicio = dict(plano_disponivel.retorna_precos_oferta['display'])
    for faixa in precos_dicio:        
        faixas.append(precos_dicio[faixa][2])
    
    plano_disponivel.log_precos_contratados = plano_disponivel.retorna_precos_oferta
    total_matriculas_exemplo, quantidades_exemplo, valor_total_exemplo = get_faixa_de_exemplo(15, plano_disponivel)
    ctx={
        'plano_disponivel': plano_disponivel,
        'faixas': faixas,
        'valor_por_aluno': "0,00" if total_matriculas_exemplo == 0 else str(format(round(float(valor_total_exemplo.replace(',', '.')) / total_matriculas_exemplo, 2), '.2f').replace('.', ',')),
        'valor_total': valor_total_exemplo,
        'total':total_matriculas_exemplo,
        'quantidades': quantidades_exemplo
    }
    if request.method == 'POST':
        total_matriculas_exemplo, quantidades_exemplo, valor_total_exemplo = get_faixa_de_exemplo(int(request.POST.get("quantidadaEnviada")), plano_disponivel)
        new_ctx = {}
        new_ctx['valor_por_aluno'] = "0,00" if total_matriculas_exemplo == 0 else str(format(round(float(valor_total_exemplo.replace(',', '.')) / total_matriculas_exemplo, 2), '.2f')).replace('.', ',')
        new_ctx['valor_total'] = valor_total_exemplo
        new_ctx['total'] = total_matriculas_exemplo
        new_ctx['quantidades'] = quantidades_exemplo    
        return JsonResponse(new_ctx)
    return render(request, template_name, ctx)