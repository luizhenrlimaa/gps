from django.apps import AppConfig


class DashboardConfig(AppConfig):
    name = 'switchblade_dashboard'

    def ready(self):
        from proj.config_resources import EXTRA_RESOURCES
        from .permissions import baseResource

        baseResource.register_menus()
        baseResource.register_extra_resources(EXTRA_RESOURCES)
