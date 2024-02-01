from .celery import app as celery_app

__all__ = ['celery_app']

default_app_config = 'activity.apps.ActivityAppConfig' # Adicionado quando testei Signals, não funcionou. Fui na StackOverflow e tinha essa dica. Acabou que o problema era no teste.