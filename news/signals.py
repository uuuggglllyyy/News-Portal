from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Author

@receiver(post_save, sender=User)
def create_user_author(sender, instance, created, **kwargs):
    if created:
        Author.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_author(sender, instance, **kwargs):
    instance.author.save()
