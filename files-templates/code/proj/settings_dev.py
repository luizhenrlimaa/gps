import os

DEBUG = True
ALLOWED_HOSTS = ['*']
INTERNAL_IPS = ('127.0.0.1', 'localhost',)

USE_CELERY = True
LOGGING_CONFIG = None


if os.name == 'nt':

    GDAL_LIBRARY_PATH = r'D:/projects/minas_vale/cargou-backend/venv/Lib/site-packages/osgeo/gdal202.dll'
    OSGEO4W = r'D:/projects/minas_vale/cargou-backend/venv/Lib/site-packages/osgeo/'

    assert os.path.isdir(OSGEO4W), "Directory does not exist: " + OSGEO4W

    os.environ['OSGEO4W_ROOT'] = OSGEO4W
    os.environ['GDAL_DATA'] = OSGEO4W + r"/data/gdal"
    os.environ['PROJ_LIB'] = OSGEO4W + r"/data/proj"
    os.environ['PATH'] = OSGEO4W + r"/;" + os.environ['PATH']

    db_host = '127.0.0.1'
    db_port = 5434
    redis_host = '127.0.0.1'

else:

    db_host = '127.0.0.1'
    db_port = 5434
    redis_host = 'proj-redis-server'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'proj_db',
        'USER': 'postgres',
        'PASSWORD': 'root',
        'HOST': db_host,
        'PORT': db_port,
    }
}

CELERY_BROKER_URL = f'redis://{redis_host}:6379'
CELERY_RESULT_BACKEND = f'redis://{redis_host}:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

AUTH_PASSWORD_VALIDATORS = []
