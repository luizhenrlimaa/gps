import django_filters
from django.utils.translation import gettext as _


from switchblade_dashboard.filters import UserNameFilter
from .models import User

FILTER_CHOICES = (
    (True,'Yes'),
    (False,'No'),
)


class UserFilter(django_filters.FilterSet):

    def is_valid(self):
        return super().is_valid()

    name = UserNameFilter(label='Name contains', field_name='')

    is_admin = django_filters.ChoiceFilter(choices=FILTER_CHOICES, label=_("User Admin"))

    is_active = django_filters.ChoiceFilter(choices=FILTER_CHOICES, label=_("User Active"))

    class Meta:
        model = User
        fields = ['name', 'is_admin', 'is_active']
