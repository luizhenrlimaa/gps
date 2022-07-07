from django.urls import path, include
# from dashboard import views
from .apis import CeleryTaskStatusAPI, MenuHelpAPI
from .views import AuditLogList, DashboardIndexView, Index
from .decorators import register_resource

urlpatterns = [
    path('', register_resource(Index), name='dashboard-index'),

    path('config/', include([
        path('', register_resource(DashboardIndexView.as_view(page_title='Configuration', header='Configuration', columns=[3, 3, 3, 3])), name='dashboard-config'),
        path('audit-log/', register_resource(AuditLogList), name='audit-log-list'),
    ])),

    path('api/', include([
        path('async-task-status/', CeleryTaskStatusAPI.as_view(), name='api-async-task-status'),
        path('help-text/', MenuHelpAPI.as_view(), name='api-help-text'),
    ])),

]

