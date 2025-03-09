from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.conf import settings  # Импортируем настройки

from .models import Author

@receiver(user_signed_up)
def user_signed_up_callback(sender, request, user, **kwargs):
    """
    Sends a welcome email after a user signs up using django-allauth.
    """
    try:
        mail_subject = 'Welcome to Our Site!'
        message = render_to_string('account/email/welcome_email.html', {
            'user': user,
        })
        to_email = user.email
        send_mail(
            mail_subject,
            strip_tags(message),
            settings.DEFAULT_FROM_EMAIL,  # Используем настройки
            [to_email],
            fail_silently=False,
            html_message=message
        )
    except Exception as e:
        print(f"Error sending welcome email: {e}")

@receiver(user_signed_up)
def create_user_author(sender, request, user, **kwargs):
    """
    Create Author object after user signs up
    """
    Author.objects.create(user=user)
