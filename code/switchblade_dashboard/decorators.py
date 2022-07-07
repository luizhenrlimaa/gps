from django.contrib.auth.decorators import login_required

from .permissions import baseResource


def register_flow_resource(cls):
    app_label = cls._meta.app_label
    class_name = cls.__name__.lower()
    class_verbose_name = cls._meta.verbose_name

    resource_view = f'{app_label}.view_{class_name}'
    baseResource.register(resource_view, f'{class_verbose_name} Flow View')
    resource_manage = f'{app_label}.manage_{class_name}'
    baseResource.register(resource_manage, f'{class_verbose_name} Flow Manage')

    return cls


def register_resource(cls, require_login=True, as_view=True, resource=None, description=None):
    '''
    Decorator for register resource
    '''

    as_view = bool(type(cls).__name__ != 'function')

    if as_view:

        resource_name_cls = cls.get_resource()

        if resource_name_cls is not None:
            resource = resource_name_cls
            description = cls.header
            if resource and description:
                baseResource.register(resource, description)
                if cls.resource_type == 'list':
                    # register export resources
                    if cls.show_export_button:
                        baseResource.register(f'{resource_name_cls.split(".")[0]}.export', f'{description} Export')
                    if cls.allow_export_import:
                        baseResource.register(f'{resource_name_cls.split(".")[0]}.template',
                                              f'{description} Template Import/Export')

    elif resource and description:
        baseResource.register(resource, description)

    if as_view:
        return_function = cls.as_view()
    else:
        return_function = cls

    if require_login:
        return login_required(return_function)
    else:
        return return_function
