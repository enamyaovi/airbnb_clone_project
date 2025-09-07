import os
from celery import Celery

# set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_travel_app.settings")

app = Celery("alx_travel_app")

# load celery config from Django settings with `CELERY_` namespace
app.config_from_object("django.conf:settings", namespace="CELERY")

# optional: prevent crash on broker startup
app.conf.broker_connection_retry_on_startup = True

# auto-discover tasks across all INSTALLED_APPS
app.autodiscover_tasks()