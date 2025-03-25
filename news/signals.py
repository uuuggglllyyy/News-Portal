from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Author
from .models import Post
from .tasks import send_notifications
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_user_author(sender, instance, created, **kwargs):
    if created:
        Author.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_author(sender, instance, **kwargs):
    instance.author.save()


@receiver(post_save, sender=Post)
def post_created(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Сигнал post_created: отправка уведомления для поста {instance.pk}")
        send_notifications.delay(instance.pk)  # Запускаем task асинхронно
