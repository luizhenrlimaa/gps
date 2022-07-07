import os
import environ

env = environ.Env()
environ.Env.read_env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=True)

ALLOWED_HOSTS = ['*']
INTERNAL_IPS = ('127.0.0.1', 'localhost',)

# Application definition
INSTALLED_APPS = [
    'dal',
    'dal_select2',
    'viewflow.frontend',
    'viewflow',
    'material',
    'material.frontend',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'django.contrib.gis',
    'django_celery_beat',
    'menu',
    'rest_framework',
    'crispy_forms',
    'django_tables2',
    'django_filters',
    'maintenance_mode',
    'django_mailbox',
    'switchblade_dashboard',
    'switchblade_users',
    'notifications',
    'registros'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'maintenance_mode.middleware.MaintenanceModeMiddleware',
]

ROOT_URLCONF = 'proj.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'maintenance_mode.context_processors.maintenance_mode',
                'switchblade_dashboard.context_processors.dashboard_info',
            ],
        },
    },
]

WSGI_APPLICATION = 'proj.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_L10N = True
USE_TZ = True

DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M'
SHORT_DATE_FORMAT = '%Y-%m-%d'
SHORT_DATETIME_FORMAT = '%Y-%m-%d %H:%M'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, './static_files'),
)

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/files/'

# ---------------
# CELERY SETTINGS
# ---------------
USE_CELERY = env.bool('USE_CELERY', True)

# Get only one task at time
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_DEFAULT_QUEUE = 'default'

# Serialization
CELERY_ACCEPT_CONTENT = ['application/json', 'pickle']
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_EAGER_PROPAGATES = False

if env.bool('CELERY_DEBUG', False):
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True

# ---------------
# AUTH SETTINGS
# ---------------
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/auth/login'
LOGOUT_URL = '/auth/logout'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
AUTH_USER_MODEL = 'switchblade_users.User'
USE_SWITCHBLADE_USER = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True

# ---------------
# LOG SETTINGS
# ---------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'proj.log'),
            'maxBytes': 1024 * 1024 * 3,  # 3 MB
            'backupCount': 5,
            'formatter': 'standard',
        },
        'request_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'proj_request.log'),
            'maxBytes': 1024 * 1024 * 3,  # 3 MB
            'backupCount': 5,
            'formatter': 'standard',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'standard',
        }
    },
    'loggers': {
        'cidc-sys': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True
        },
        'django.request': {
            'handlers': ['request_handler', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False
        },
    }
}

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    )
}

# ---------------
# OTHER SETTINGS
# ---------------
CRISPY_TEMPLATE_PACK = 'bootstrap3'
DJANGO_TABLES2_TEMPLATE = 'django_tables2/bootstrap_custom.html'
DJANGO_NOTIFICATIONS_CONFIG = {'USE_JSONFIELD': True}
MAINTENANCE_MODE_IGNORE_SUPERUSER = True
MAINTENANCE_MODE_IGNORE_ADMIN_SITE = True
USE_SILK = env.bool('USE_SILK', False)
MPTT_DEFAULT_LEVEL_INDICATOR = ''
MENU_SELECT_PARENTS = True

VERSION = env.str('VERSION', '1.0.0')
SYSTEM_SHORT_NAME = env.str('SYSTEM_SHORT_NAME', 'SYS')
SYSTEM_LONG_NAME = env.str('SYSTEM_LONG_NAME', 'System')
SYSTEM_OWNER = env.str('SYSTEM_OWNER', 'Owner')
ACTUAL_ENV = env.str('ACTUAL_ENV', 'dev')

if ACTUAL_ENV:
    try:
        if ACTUAL_ENV == 'dev':
            from .settings_dev import *
            if os.name == 'nt' and USE_SILK:
                INSTALLED_APPS = INSTALLED_APPS + ['silk']
                MIDDLEWARE = MIDDLEWARE + ['silk.middleware.SilkyMiddleware']
                SILKY_PYTHON_PROFILER = True
                SILKY_PYTHON_PROFILER_BINARY = True
                SILKY_META = True
        elif ACTUAL_ENV == 'staging':
            from .settings_staging import *
        elif ACTUAL_ENV == 'production':
            from .settings_production import *
    except ImportError:
        raise SystemError('Settings file not found for {0}! Missing settings_{0}.py file'.format(ACTUAL_ENV))
else:
    raise SystemError('Environment not set! Create .env file.')
