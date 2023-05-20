from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test


def mentores_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='usuarios:cadastro'):
    '''
    Decorator for views that checks that the logged in user is a 'Mentor',
    redirects to the log-in page if necessary.
    '''
    actual_decorator = user_passes_test(
        lambda u: u.email_checked,
        redirect_field_name=redirect_field_name,
        login_url=login_url,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
