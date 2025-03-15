import logging
from django.conf import settings
from django.core.management.base import BaseCommand
from django_apscheduler import util
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.models import DjangoJobExecution
from django.utils import timezone
from .tasks import send_weekly_newsletter # Импорт task из news.tasks

logger = logging.getLogger(__name__)  # Важно использовать __name__

@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """Удаляет старые записи выполненных задач."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # Планируем Celery task
        scheduler.add_job(
            send_weekly_newsletter.delay,  # Запускаем task через Celery
            trigger="cron",
            day_of_week="mon",  # Каждый понедельник
            hour="08",
            minute="00",
            id="send_weekly_newsletter",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'send_weekly_newsletter'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger="interval",
            days=7,
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