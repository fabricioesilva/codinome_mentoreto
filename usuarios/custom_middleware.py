from django.contrib.auth import logout
from django.contrib import messages
from django.utils.translation import gettext as _


class CustomMiddleware:
    """Verifica se o usuário está com email confirmado ou não.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_anonymous:
            return response
        if not request.user.email_checked:
            messages.error(request, _('Usuário inválido.'))
            logout(request)
        return response
