from characters.models import Character
from celery import shared_task


@shared_task
def count_characters() -> int:
    return Character.objects.count()
