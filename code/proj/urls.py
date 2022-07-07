import notifications.urls

from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from material.frontend import urls as frontend_urls

urlpatterns = [
    path('flow/', include(frontend_urls)),
    path('admin/', admin.site.urls),
    path('admin/maintenance-mode/', include('maintenance_mode.urls')),
    path('notifications/', include(notifications.urls, namespace='notifications')),

    path('', include('switchblade_users.urls')),
    path('', include('switchblade_dashboard.urls')),
    path('', include('registros.urls'))
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

try:
    import __dev__
    if settings.DEBUG and settings.USE_SILK and 'silk' in settings.INSTALLED_APPS:
        urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]
except ImportError:
    pass