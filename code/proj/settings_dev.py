import os
import environ

env = environ.Env()
environ.Env.read_env()

LOGGING_CONFIG = None
USE_CELERY = env.bool('USE_CELERY', True)


if os.name == 'nt':

    GDAL_LIBRARY_PATH = r'C:/projects/cidc-sys-venv37/Lib/site-packages/osgeo/gdal204.dll'
    OSGEO4W = r'C:/projects/cidc-sys-venv37/Lib/site-packages/osgeo'

    assert os.path.isdir(OSGEO4W), "Directory does not exist: " + OSGEO4W

    os.environ['OSGEO4W_ROOT'] = OSGEO4W
    os.environ['GDAL_DATA'] = OSGEO4W + r"/data/gdal"
    os.environ['PROJ_LIB'] = OSGEO4W + r"/data/proj"
    os.environ['PATH'] = OSGEO4W + r"/;" + os.environ['PATH']

    db_host = '127.0.0.1'
    db_port = 5432
    redis_host = '127.0.0.1'

else:

    db_host = '127.0.0.1'
    db_port = 5432
    redis_host = 'redis'


DATABASES = {

    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'tcac',
        'USER': 'postgres',
        'PASSWORD': 'root',
        'HOST': db_host,
        'PORT': db_port,
    },
}

CELERY_BROKER_URL = f'redis://{redis_host}:6379'
CELERY_RESULT_BACKEND = f'redis://{redis_host}:6379'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

AUTH_PASSWORD_VALIDATORS = []

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
