import importlib

from dal import autocomplete
from django.conf import settings
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django_filters import Filter, ChoiceFilter, FilterSet, MultipleChoiceFilter, ModelChoiceFilter, CharFilter
if settings.USE_SWITCHBLADE_USER:
    from switchblade_users.models import User
from .forms import DateTimeRangeInput
from .models import AuditLog
from .utils import get_date_range, get_datetime_range


class ListFilter(Filter):
    def filter(self, qs, value):

        if value:
            value_list = value.strip().split('\r\n')
            filtered_items_id = []

            for vl in value_list:
                for item in qs.filter(**{self.field_name + '__icontains': vl}):
                    filtered_items_id.append(item.pk)

            qs = qs.filter(pk__in=filtered_items_id)

        return qs


class UserNameFilter(Filter):
    def filter(self, qs, value):

        if value:

            if self.field_name != '':
                qs = qs.annotate(full_name=Concat('%s__first_name' % (self.field_name), Value(' '), '%s__last_name' % (self.field_name))).filter(full_name__unaccent__icontains=value)
            else:
                qs = qs.annotate(full_name=Concat('first_name', Value(' '), 'last_name')).filter(full_name__unaccent__icontains=value)

        return qs


class MaxResultsFilter(ChoiceFilter):

    def filter(self, qs, value):

        if value:
            qs = qs.filter()[:int(value)]
        return qs


class DateRangeFilter(Filter):

    def filter(self, qs, value):
        if value:

            start, end = get_date_range(value)
            self.lookup_expr = 'range'
            value = (start, end)

        return super().filter(qs, value)


class DateTimeRangeFilter(Filter):

    def filter(self, qs, value):
        if value:

            start, end = get_datetime_range(value)
            self.lookup_expr = 'range'
            value = (start, end)

        return super().filter(qs, value)


class AuditLogFilter(FilterSet):

    msg = CharFilter(label='Message contains', field_name='msg', lookup_expr='icontains')
    trace = CharFilter(label='Traceback contains', field_name='trace', lookup_expr='icontains')
    created_on = DateTimeRangeFilter(widget=DateTimeRangeInput())

    level = ChoiceFilter(choices=AuditLog.LEVEL_CHOICES)
    if settings.USE_SWITCHBLADE_USER:
        created_by = ModelChoiceFilter(queryset=User.objects.all(),
                                                        field_name='created_by',
                                                        label='User',
                                                        widget=autocomplete.ModelSelect2(url='user-autocomplete',
                                                        ))

    class Meta:
        model = AuditLog
        fields = ['level', 'msg', 'trace', 'created_by', 'created_on']
