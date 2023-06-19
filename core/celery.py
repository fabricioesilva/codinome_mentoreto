from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# setting the Django settings module.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
app = Celery('celery_app')
app.config_from_object('django.conf:settings', namespace='CELERY')
# app.conf.broker_url = 'redis://:Mentoreto1536874@127.0.0.1:6379/0'
# Looks up for task modules in Django applications and loads them
app.autodiscover_tasks()
