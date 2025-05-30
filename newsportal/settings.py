
from pathlib import Path
import os
from celery.schedules import crontab
import logging.config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-b1i7_hdja@ye=v_^^r@m8e87dj^30$j8gw%)wf7a&o#w!x%7&g'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Application definition

INSTALLED_APPS = [
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'news',
    'protect',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'django_apscheduler',
    'django.middleware.locale',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'middlewares.TimezoneMiddleware',
    'middlewares.RequestLoggingMiddleware'
]

ROOT_URLCONF = 'newsportal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]

WSGI_APPLICATION = 'newsportal.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'ru'

LANGUAGES = [
    ('en', 'English'),
    ('ru', 'Русский'),
]

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

SITE_ID = 1

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Добавляем эти настройки:
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_LOGIN_METHODS = 'email', 'username'
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

ACCOUNT_FORMS = {'signup': 'news.forms.BasicSignupForm'}

EMAIL_HOST = 'smtp.yandex.ru'  # адрес сервера Яндекс-почты для всех один и тот же
EMAIL_PORT = 465  # порт smtp сервера тоже одинаковый
EMAIL_HOST_USER = 'great.egor7288'  # ваше имя пользователя, например, если ваша почта user@yandex.ru, то сюда надо писать user, иными словами, это всё то что идёт до собаки
EMAIL_HOST_PASSWORD = 'vuezzkkdvdleknmg'  # пароль от почты
EMAIL_USE_SSL = True  # Яндекс использует ssl, подробнее о том, что это, почитайте в дополнительных источниках, но включать его здесь обязательно

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER + '@yandex.ru' # если вы используете Яндекс, то не забудьте добавить + ‘@yandex.ru’

# формат даты, которую будет воспринимать наш задачник (вспоминаем модуль по фильтрам)
APSCHEDULER_DATETIME_FORMAT = "N j, Y, f:s a"

# если задача не выполняется за 25 секунд, то она автоматически снимается, можете поставить время побольше, но как правило, это сильно бьёт по производительности сервера
APSCHEDULER_RUN_NOW_TIMEOUT = 25  # Seconds

# Celery settings
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # URL вашего Redis сервера
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'  # Optional, для отслеживания результатов задач
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Yekaterinburg'  # Установите свой часовой пояс

CELERY_BEAT_SCHEDULE = {
    'send_weekly_newsletter': {
        'task': 'news.tasks.send_weekly_newsletter',  # Путь к вашей task
        'schedule': crontab(hour=8, minute=0, day_of_week='monday'),  # Каждый понедельник в 8:00
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'cache_files'),  # Указываем, куда будем сохранять кэшируемые файлы! Не забываем создать папку cache_files внутри папки с manage.py!
    }
}

# Настройки для отправки сообщений администраторам
ADMINS = [
    ('greategor', 'great.egor7288@yandex.ru'),
    # ('Имя Админа 2', 'адрес2@example.com'), # Добавьте других админов при необходимости
]

SERVER_EMAIL = DEFAULT_FROM_EMAIL  # Или другой адрес, с которого будут отправляться сообщения об ошибках

#if you need you can on
'''LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {'format': '%(asctime)s %(levelname)s %(name)s %(module)s %(message)s', 'datefmt': '%Y-%m-%d %H:%M:%S'},
        'file': {'format': '%(asctime)s %(levelname)s %(name)s %(module)s %(message)s', 'datefmt': '%Y-%m-%d %H:%M:%S'},
        'security': {'format': '%(asctime)s %(levelname)s %(name)s %(module)s %(message)s', 'datefmt': '%Y-%m-%d %H:%M:%S'},
        'error_file': {'format': '%(asctime)s %(levelname)s %(name)s %(pathname)s %(exc_info)s %(message)s', 'datefmt': '%Y-%m-%d %H:%M:%S'}
    },
    'filters': {
        'require_debug_true': {'()': 'django.utils.log.RequireDebugTrue'},
        'require_debug_false': {'()': 'django.utils.log.RequireDebugFalse'}
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'console',
            'filters': ['require_debug_true']
        },
        'general': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'general.log'),
            'formatter': 'file',
            'filters': ['require_debug_false']
        },
        'errors': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'errors.log'),
            'formatter': 'error_file'
        },
        'security': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'security.log'),
            'formatter': 'security'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
            'formatter': 'error_file',  # Use error_file format
            'filters': ['require_debug_false']  # Send emails only when DEBUG is False
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'general'], # Remove 'errors' handler here
            'level': 'DEBUG',
            'propagate': False
        },
        'django.security': {
            'handlers': ['security'],
            'level': 'WARNING',
            'propagate': False
        },
        'django.request': {
            'handlers': ['mail_admins'], # Only mail_admins
            'level': 'ERROR',
            'propagate': False
        },
        'django.server': {
            'handlers': ['mail_admins'], # Only mail_admins
            'level': 'ERROR',
            'propagate': False
        },
         'django.template': {
            'handlers': ['errors'],
            'level': 'ERROR',
            'propagate': False
        },
        'django.db.backends': {
            'handlers': ['errors'],
            'level': 'ERROR',
            'propagate': False
        },
        'news.views': {  # Или 'protect.views', или другое имя вашего модуля
            'handlers': ['console', 'errors'], # Keep console and errors
            'level': 'DEBUG', # Or 'ERROR', in production, 'DEBUG' for testing.
            'propagate': False,
        },
    }
}

logging.config.dictConfig(LOGGING)'''


LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale')
]
