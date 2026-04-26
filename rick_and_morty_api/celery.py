import os

from celery import Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rick_and_morty_api.settings')

celery = Celery('rick_and_morty_api')
celery.config_from_object('django.conf:settings', namespace='CELERY')

# Use solo pool for Windows compatibility
celery.autodiscover_tasks()

# Windows compatibility
celery.conf.update(
    worker_pool='solo',
    worker_concurrency=1,
)

@celery.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")