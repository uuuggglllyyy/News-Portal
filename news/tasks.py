from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail, send_mass_mail
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from .models import Category, Post
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, retry_backoff=True, max_retries=5)
def send_notifications(self, post_id):
    """Отправляет уведомления подписчикам после создания новости (Celery task)."""
    try:
        post = Post.objects.get(pk=post_id)  # Получаем пост по ID
        logger.info(f"Начинаем рассылку уведомлений для поста ID: {post_id}")

        for category in post.categories.all():
            for subscriber in category.subscribers.all():
                subject = post.title

                html_content = render_to_string(
                    'news/email_notification.html',
                    {
                        'user': subscriber,
                        'post': post,
                    }
                )

                try:
                    send_mail(
                        subject,
                        '',  # Если html, то пустая строка
                        settings.DEFAULT_FROM_EMAIL,  # Ваша почта
                        [subscriber.email],
                        fail_silently=False,
                        html_message=html_content,
                    )
                    logger.info(f"Отправлено уведомление {subscriber.email} о посте {post.title}")

                except Exception as e:
                    logger.error(f"Ошибка отправки уведомления {subscriber.email}: {e}")
                    raise self.retry(exc=e)  # Retry on error

        logger.info(f"Рассылка уведомлений для поста ID: {post_id} завершена")
        return f"Уведомления для поста {post_id} отправлены."

    except Post.DoesNotExist:
        logger.error(f"Пост с ID {post_id} не найден.")
        return f"Пост с ID {post_id} не найден."
    except Exception as e:
        logger.error(f"Общая ошибка при отправке уведомлений для поста {post_id}: {e}")
        raise


@shared_task(bind=True, retry_backoff=True, max_retries=3)
def send_weekly_newsletter(self):
    """Рассылка новостей подписчикам категорий (Celery task)."""
    now = timezone.now()
    last_week = now - timedelta(days=7)

    for category in Category.objects.all():
        subscribers = category.subscribers.all()
        if subscribers.exists():
            recent_posts = Post.objects.filter(
                categories=category,
                date_created__gte=last_week,
                date_created__lte=now
            )

            for subscriber in subscribers:
                subject = f'Еженедельная рассылка новостей из категории "{category.name}"'
                html_content = render_to_string(
                    'news/weekly_email.html',
                    {
                        'user': subscriber,
                        'posts': recent_posts,
                        'category': category,
                    }
                )

                try:
                    send_mail(
                        subject,
                        '',  # Если html, то пустая строка
                        settings.DEFAULT_FROM_EMAIL,  # Ваша почта
                        [subscriber.email],
                        fail_silently=False,
                        html_message=html_content,  # Явно указываем html_message
                    )
                    logger.info(f"Отправлено уведомление {subscriber.email} о еженедельной рассылке категории {category.name}")

                except Exception as e:
                    logger.error(f"Ошибка отправки уведомления {subscriber.email}: {e}")
                    raise self.retry(exc=e)
        else:
            logger.info(f"В категории {category.name} нет подписчиков.")

    logger.info("Еженедельная рассылка успешно отправлена.")
    return "Еженедельная рассылка успешно отправлена."