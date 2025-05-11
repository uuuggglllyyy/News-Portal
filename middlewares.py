# middlewares.py
import logging
import pytz
from django.utils import timezone


logger = logging.getLogger('django.request') # Используем логгер django.request

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info(f"Request received: {request.method} {request.path}") # Логируем входящий запрос
        response = self.get_response(request)
        logger.info(f"Response sent: {response.status_code} for {request.method} {request.path}") # Логируем исходящий ответ
        return response

class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = request.session.get('django_timezone')
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()  # Активируем часовой пояс по умолчанию

        return self.get_response(request)