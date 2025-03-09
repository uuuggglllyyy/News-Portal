import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django_apscheduler import util
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils import timezone
from news.models import Category, Post  # Импортируйте ваши модели

logger = logging.getLogger(__name__)


def send_weekly_newsletter():
    """
    Рассылка новостей подписчикам категорий.
    """
    now = timezone.now()
    last_week = now - timezone.timedelta(days=7)

    for category in Category.objects.all():
        subscribers = category.subscribers.all()
        if subscribers.exists():  # Проверяем, есть ли подписчики
            recent_posts = Post.objects.filter(
                categories=category,
                date_created__gte=last_week,
                date_created__lte=now
            )

            if recent_posts.exists():  # Проверяем, есть ли новые посты
                for subscriber in subscribers:
                    subject = f'Еженедельная рассылка новостей из категории "{category.name}"'
                    html_content = render_to_string(
                        'news/weekly_email.html',  # Создайте этот шаблон
                        {
                            'user': subscriber,
                            'posts': recent_posts,
                            'category': category,
                        }
                    )
                    try:
                        send_mail(
                            subject,
                            '',  # Пустая строка для текстовой версии (если используете html)
                            settings.DEFAULT_FROM_EMAIL,  # Используйте настройку из settings.py
                            [subscriber.email],
                            fail_silently=False,
                            html_message=html_content,
                        )
                        logger.info(f"Отправлено письмо {subscriber.email} о категории {category.name}")
                    except Exception as e:
                        logger.error(f"Ошибка отправки письма {subscriber.email}: {e}")
            else:
                logger.info(f"В категории {category.name} нет новых постов за последнюю неделю.")
        else:
            logger.info(f"В категории {category.name} нет подписчиков.")

@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    Удаляет старые записи выполненных задач.
    """
    from django_apscheduler.models import DjangoJobExecution
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # Добавляем задачу на отправку еженедельной рассылки
        scheduler.add_job(
            send_weekly_newsletter,
            trigger="cron",
            day_of_week="mon",  # Каждый понедельник
            hour="08",  # В 8 утра (можно изменить)
            minute="00",
            id="send_weekly_newsletter",  # Уникальный ID
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'send_weekly_newsletter'.")

        # Добавляем задачу на удаление старых выполненных задач
        scheduler.add_job(
            delete_old_job_executions,
            trigger="interval",
            days=7,  # Каждую неделю
            start_date=timezone.now(),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'delete_old_job_executions'.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")