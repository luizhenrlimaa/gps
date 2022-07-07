from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.exceptions import PermissionDenied

def require_resource_permission(resource):
    '''
    Decorator for views that checks that the logged in user has a resource allowed
    '''

    def check_user_type(user):
        user_roles = user.get_allowed_resources

        if resource not in user_roles and not user.is_admin:
            raise PermissionDenied()

        return True

    return user_passes_test(check_user_type)
