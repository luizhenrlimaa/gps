from django.conf import settings


def dashboard_info(request):

    return {
        'SYSTEM_VERSION': settings.VERSION,
        'DEPLOY_ENV': settings.ACTUAL_ENV,
        'SYSTEM_SHORT_NAME': settings.SYSTEM_SHORT_NAME,
        'SYSTEM_LONG_NAME': settings.SYSTEM_LONG_NAME,
        'SYSTEM_OWNER': settings.SYSTEM_OWNER
    }
