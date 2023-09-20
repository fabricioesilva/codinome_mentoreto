from django.utils.translation import gettext_lazy as _
import re

ATIVIDADE_MATRICULA  = [
    ("cria", _("Matrícula foi criada")),
    ("ence", _("Matrícula foi encerrada")),
    ("alte", _("Matrícula foi alterada")),
    ("apag", _("Matrícula foi apagada")),
    ("resp", _("Resposta no simulado"))
]

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
    ('at', _('Ativo')),
    ('ex', _('Ex-aluno')),
]
QUESTAO_TIPO = [
    (1, _('ABCD')),
    (2, _('ABCDE')),
    (3, _('Certo/Errado'))
]


def valida_cpf(cpf):
    cpf = str(cpf)
    cpf = re.sub(r'[^0-9]', '', cpf)

    if not cpf or len(cpf) != 11:
        return False

    novo_cpf = cpf[:-2]                 # Elimina os dois últimos digitos do CPF
    reverso = 10                        # Contador reverso
    total = 0

    # Loop do CPF
    for index in range(19):
        if index > 8:                   # Primeiro índice vai de 0 a 9,
            index -= 9                  # São os 9 primeiros digitos do CPF

        total += int(novo_cpf[index]) * reverso  # Valor total da multiplicação

        reverso -= 1                    # Decrementa o contador reverso
        if reverso < 2:
            reverso = 11
            d = 11 - (total % 11)

            if d > 9:                   # Se o digito for > que 9 o valor é 0
                d = 0
            total = 0                   # Zera o total
            novo_cpf += str(d)          # Concatena o digito gerado no novo cpf

    # Evita sequencias. Ex.: 11111111111, 00000000000...
    sequencia = novo_cpf == str(novo_cpf[0]) * len(cpf)

    # Descobri que sequências avaliavam como verdadeiro, então também
    # adicionei essa checagem aqui
    if cpf == novo_cpf and not sequencia:
        return True
    else:
        return False


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
