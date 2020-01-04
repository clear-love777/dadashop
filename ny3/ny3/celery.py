from django.conf import settings
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE","ny3.settings")

app=Celery("ny3_celery")
app.conf.update(
    BROKER_URL="redis://:@127.0.0.1:6379/1"
)

app.autodiscover_tasks(settings.INSTALLED_APPS)