from django.utils.translation import gettext_lazy as _

MAINLY_DOMAINS = [
    'bol.com.br',
    'uol.com.br',
    'gmail.com',
    'yahoo.com',
    'hotmail.com',
    'aol.com',
    'hotmail.co.uk',
    'hotmail.fr',
    'msn.com',
    'yahoo.fr',
    'wanadoo.fr',
    'orange.fr',
    'comcast.net',
    'yahoo.co.uk',
    'yahoo.com.br',
    'yahoo.co.in',
    'live.com',
    'rediffmail.com',
    'free.fr',
    'gmx.de',
    'web.de',
    'yandex.ru',
    'ymail.com',
    'libero.it',
    'outlook.com',
    'uol.com.br',
    'bol.com.br',
    'mail.ru',
    'cox.net',
    'hotmail.it',
    'sbcglobal.net',
    'sfr.fr',
    'live.fr',
    'verizon.net',
    'live.co.uk',
    'googlemail.com',
    'yahoo.es',
    'ig.com.br',
    'live.nl',
    'bigpond.com',
    'terra.com.br',
    'yahoo.it',
    'neuf.fr',
    'yahoo.de',
    'alice.it',
    'rocketmail.com',
    'att.net',
    'laposte.net',
    'facebook.com',
    'bellsouth.net',
    'yahoo.in',
    'hotmail.es',
    'charter.net',
    'yahoo.ca',
    'yahoo.com.au',
    'rambler.ru',
    'hotmail.de',
    'tiscali.it',
    'shaw.ca',
    'yahoo.co.jp',
    'sky.com',
    'earthlink.net',
    'optonline.net',
    'freenet.de',
    't-online.de',
    'aliceadsl.fr',
    'virgilio.it',
    'home.nl',
    'qq.com',
    'telenet.be',
    'me.com',
    'yahoo.com.ar',
    'tiscali.co.uk',
    'yahoo.com.mx',
    'voila.fr',
    'gmx.net',
    'mail.com',
    'planet.nl',
    'tin.it',
    'live.it',
    'ntlworld.com',
    'arcor.de',
    'yahoo.co.id',
    'frontiernet.net',
    'hetnet.nl',
    'live.com.au',
    'yahoo.com.sg',
    'zonnet.nl',
    'club-internet.fr',
    'juno.com',
    'optusnet.com.au',
    'blueyonder.co.uk',
    'bluewin.ch',
    'skynet.be',
    'sympatico.ca',
    'windstream.net',
    'mac.com',
    'centurytel.net',
    'chello.nl',
    'live.ca',
    'aim.com',
    'bigpond.net.au'
]
TRANSLATIONS_LANGUAGES = [
    'pt-br',
    'pt',
    'en'
]
POLICY_LANGUAGES = [
    'pt-br',
    'en'
]
GENDER_CHOICES = [
    ('mo', _('Masculino')),
    ('fe', _('Feminino')),
    ('ni', _('Outro')),
]
PREPARO_CHOICES = [
    (1, 'Iniciante'),
    (2, 'Intermediário'),
    (3, 'Avançado')
]
PERFIL_PSICO = [
    ('san', _('Sanguíneo')),
    ('fle', _('Fleumático')),
    ('col', _('Colérico')),
    ('mel', _('Melancólico'))
]
SITUACAO_ALUNO = [
    ('ok', _('Ativo')),
    ('ex', _('Ex-aluno')),
]
QUESTAO_TIPO = [
    (1, _('A-D')),
    (2, _('A-E')),
    (3, _('Certo/Errado'))
]


def form_valid_custom(form, validation_error):
    """
    Adicionalmente, ao salvar campo em branco, as alternativas serão organizadas.
    """
    changed_d = False
    changed_e = False
    if not form.instance.alt_c:
        if form.instance.alt_d:
            form.instance.alt_c = form.instance.alt_d
            if form.instance.alt_e:
                form.instance.alt_d = form.instance.alt_e
                if form.instance.alt_f:
                    form.instance.alt_e = form.instance.alt_f
                    form.instance.alt_f = ''
                else:
                    form.instance.alt_e = ''
                    changed_e = True
            else:
                if form.instance.alt_f:
                    form.instance.alt_d = form.instance.alt_f
                    form.instance.alt_f = ''
                else:
                    form.instance.alt_d = ''
                    changed_d = True
        elif form.instance.alt_e:
            form.instance.alt_c = form.instance.alt_e
            if form.instance.alt_f:
                form.instance.alt_d = form.instance.alt_f
                form.instance.alt_f = ''
                form.instance.alt_e = ''
                changed_e = True
            else:
                form.instance.alt_e = ''
                changed_e = True
        elif form.instance.alt_f:
            form.instance.alt_c = form.instance.alt_f
            form.instance.alt_f = ''
    elif not form.instance.alt_d and not changed_d:
        if form.instance.alt_e:
            form.instance.alt_d = form.instance.alt_e
            if form.instance.alt_f:
                form.instance.alt_e = form.instance.alt_f
                form.instance.alt_f = ''
            else:
                form.instance.alt_e = ''
                changed_e = True
        elif form.instance.alt_f:
            form.instance.alt_d = form.instance.alt_f
            form.instance.alt_f = ''
    elif not form.instance.alt_e and not changed_e:
        if form.instance.alt_f:
            form.instance.alt_e = form.instance.alt_f
            form.instance.alt_f = ''
    return form


def check_user_is_regular(request):
    """Verifica se o usuário autenticado está com email verificado, para fins de utilização logado.

    Args:
        request (wsgi request): Parâmetro 'request'

    Returns:
        Bool: Booleano
    """
    if request.user.email_checked:
        return True
    else:
        return False
