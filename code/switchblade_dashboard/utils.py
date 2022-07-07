import datetime

from dal import autocomplete
from dal.widgets import WidgetMixin
from dateutil.relativedelta import relativedelta
from django.core.exceptions import PermissionDenied
from django.db.models.signals import m2m_changed, pre_save, pre_delete, post_save
from django.utils import timezone, formats
from django.utils.safestring import mark_safe
from django.utils.timezone import make_aware
from django.utils.translation import gettext as _
from rest_framework import pagination

from .signals import model_action_delete_log, model_action_save_m2m_log, \
    model_action_pre_save_log, model_action_post_save_log


class ResultsSetPagination(pagination.PageNumberPagination):
    page_size = 5


class Select2QuerySetViewCompoundChained(autocomplete.Select2QuerySetView):

    def get_selected_result_label(self, result):
        chained = self.forwarded.get('chained', False)
        return result.name if chained else result.compound_name

    def get_result_label(self, result):
        chained = self.forwarded.get('chained', False)
        return result.name if chained else result.compound_name


class ModelSelect2CompoundChained(autocomplete.ModelSelect2):

    def optgroups(self, name, value, attrs=None):
        """Return a list of optgroups for this widget."""
        groups = []
        has_selected = False

        for index, (option_value, option_label) in enumerate(self.choices):
            if option_value is None:
                option_value = ''

            try:
                '''
                hack to deal with compound_name on chained fields.
                '''
                if option_value != '':
                    option_label = self.choices.queryset.get(pk=option_value).name
            except:
                pass

            subgroup = []
            if isinstance(option_label, (list, tuple)):
                group_name = option_value
                subindex = 0
                choices = option_label
            else:
                group_name = None
                subindex = None
                choices = [(option_value, option_label)]
            groups.append((group_name, subgroup, index))

            for subvalue, sublabel in choices:
                selected = (
                    str(subvalue) in value and
                    (not has_selected or self.allow_multiple_selected)
                )
                has_selected |= selected
                subgroup.append(self.create_option(
                    name, subvalue, sublabel, selected, index,
                    subindex=subindex, attrs=attrs,
                ))
                if subindex is not None:
                    subindex += 1
        return groups


class Select2QuerySetViewFixed(autocomplete.Select2QuerySetView):

    def create_object(self, text):
        """Create an object given a text."""
        return self.get_queryset().get_or_create(
            **{self.create_field: text})[0]

    def get_create_option(self, context, q):
        """Form the correct create_option to append to results."""
        create_option = []
        display_create_option = False
        if self.create_field and q:
            page_obj = context.get('page_obj', None)
            if page_obj is None or page_obj.number == 1:
                display_create_option = True

            # Don't offer to create a new option if a
            # case-insensitive) identical one already exists
            existing_options = (self.get_result_label(result).lower()
                                for result in context['object_list'])
            if q.lower() in existing_options:
                display_create_option = False

        if display_create_option and self.has_add_permission(self.request):
            create_option = [{
                'id': q,
                'text': _('Create "%(new_value)s"') % {'new_value': q},
                'create_id': True,
            }]
        return create_option

    def has_add_permission(self, request):

        """Return True if the user has the permission to add a model."""
        if not request.user.is_authenticated:
            return False
        return True


def get_datetime_range(datetime_value):

    if not datetime_value:
        return None

    filter_datetime = datetime_value.split(' until ')

    date_range = [
        make_aware(datetime.datetime.strptime(filter_datetime[0], '%Y-%m-%d %H:%M')),
        make_aware(datetime.datetime.strptime(filter_datetime[1], '%Y-%m-%d %H:%M'))
    ]

    return date_range


def get_datetime(datetime_value):

    if not datetime_value:
        return None

    return make_aware(datetime.datetime.strptime(datetime_value, '%Y-%m-%d %H:%M'))


def get_date(date_value):

    if not date_value:
        return None

    return make_aware(datetime.datetime.strptime(date_value, '%Y-%m-%d')).date()


def get_date_range(date_value):

    if not date_value:
        return None

    if 'until' in date_value:
        filter_date = date_value.split(' until ')

        return [datetime.datetime.strptime(filter_date[0], '%Y-%m-%d').date(), datetime.datetime.strptime(filter_date[1], '%Y-%m-%d').date()]

    return [datetime.datetime.strptime(date_value, '%Y-%m-%d').date(), datetime.datetime.strptime(date_value, '%Y-%m-%d').date()]


def date_to_datetime_range(date_value):

    if not date_value:
        return None

    if 'until' in date_value:
        filter_date = date_value.split(' until ')

        return [make_aware(datetime.datetime.combine(filter_date[0], datetime.datetime.min.time())),
                make_aware(datetime.datetime.combine(filter_date[1], datetime.datetime.max.time()))]

    return [make_aware(datetime.datetime.combine(date_value[0], datetime.datetime.min.time())),
            make_aware(datetime.datetime.combine(date_value[1], datetime.datetime.max.time()))]


def timedelta_to_float_hours(value):

    if isinstance(value, datetime.timedelta):
        return value / datetime.timedelta(hours=1)

    return value


def get_relative_date():
    # Get Relative Today
    today = timezone.localtime().date()
    today_datetime_min = datetime.datetime.combine(today, datetime.datetime.min.time())
    today_datetime_max = datetime.datetime.combine(today, datetime.datetime.max.time())

    # Get Relative Yesterday
    yesterday = (today - datetime.timedelta(days=1))
    yesterday_datetime_min = datetime.datetime.combine(yesterday, datetime.datetime.min.time())
    yesterday_datetime_max = datetime.datetime.combine(yesterday, datetime.datetime.max.time())

    # Get Relative 2 days ago
    two_days_ago = (today - datetime.timedelta(days=2))
    two_days_ago_datetime_min = datetime.datetime.combine(two_days_ago, datetime.datetime.min.time())
    two_days_ago_datetime_max = datetime.datetime.combine(today, datetime.datetime.max.time())

    # Get Relative 3 days ago
    three_days_ago = (today - datetime.timedelta(days=3))
    three_days_ago_datetime_min = datetime.datetime.combine(three_days_ago, datetime.datetime.min.time())
    three_days_ago_datetime_max = datetime.datetime.combine(today, datetime.datetime.max.time())

    # Get Relative 7 days ago
    seven_days_ago = (today - datetime.timedelta(days=7))
    seven_days_ago_datetime_min = datetime.datetime.combine(seven_days_ago, datetime.datetime.min.time())
    seven_days_ago_datetime_max = datetime.datetime.combine(today, datetime.datetime.max.time())

    # Get Relative Week
    days_from_start = (today.isoweekday() % 7)
    week_date_range = [today - datetime.timedelta(days=days_from_start),
                       today + datetime.timedelta(days=(6 - days_from_start))]
    week_datetime_min = datetime.datetime.combine(week_date_range[0], datetime.datetime.min.time())
    week_datetime_max = datetime.datetime.combine(week_date_range[1], datetime.datetime.max.time())

    # Get Relative Last Week
    days_from_start_last_week = (today.isoweekday() % 14)
    last_week_date_range = [
        (today - datetime.timedelta(days=(7 + days_from_start_last_week))),
        today + datetime.timedelta(days=(6 - (7 + days_from_start_last_week)))]
    last_week_datetime_min = datetime.datetime.combine(last_week_date_range[0], datetime.datetime.min.time())
    last_week_datetime_max = datetime.datetime.combine(last_week_date_range[1], datetime.datetime.max.time())

    # Get Relative 9 days ago
    nine_days_ago = (today - datetime.timedelta(days=9))
    nine_days_ago_datetime_min = datetime.datetime.combine(nine_days_ago, datetime.datetime.min.time())
    nine_days_ago_datetime_max = datetime.datetime.combine(today, datetime.datetime.max.time())

    # Get Relative 15 days ago
    fifteen_days_ago = (today - datetime.timedelta(days=15))
    fifteen_days_ago_datetime_min = datetime.datetime.combine(fifteen_days_ago, datetime.datetime.min.time())
    fifteen_days_ago_datetime_max = datetime.datetime.combine(today, datetime.datetime.max.time())

    # Get Relative 30 days ago
    thirty_days_ago = (today - datetime.timedelta(days=30))
    thirty_days_ago_datetime_min = datetime.datetime.combine(thirty_days_ago, datetime.datetime.min.time())
    thirty_days_ago_datetime_max = datetime.datetime.combine(today, datetime.datetime.max.time())

    # Get Relative Month
    month_date_range = [today.replace(day=1), (today + relativedelta(day=31))]
    month_datetime_min = datetime.datetime.combine(month_date_range[0], datetime.datetime.min.time())
    month_datetime_max = datetime.datetime.combine(month_date_range[1], datetime.datetime.max.time())

    # Get Relative Last Month
    first_day = today.replace(day=1)
    last_month_date_range = [
        (first_day - datetime.timedelta(days=1)).replace(day=1), (first_day - datetime.timedelta(days=1))]
    last_month_datetime_min = datetime.datetime.combine(last_month_date_range[0], datetime.datetime.min.time())
    last_month_datetime_max = datetime.datetime.combine(last_month_date_range[1], datetime.datetime.max.time())

    data = {
        'yesterday': yesterday,
        'yesterday_datetime_range': [make_aware(yesterday_datetime_min), make_aware(yesterday_datetime_max)],
        'two_days_ago': two_days_ago,
        'two_days_ago_datetime_range': [make_aware(two_days_ago_datetime_min), make_aware(two_days_ago_datetime_max)],
        'three_days_ago': three_days_ago,
        'three_days_ago_datetime_range': [make_aware(three_days_ago_datetime_min), make_aware(three_days_ago_datetime_max)],
        'seven_days_ago': seven_days_ago,
        'seven_days_ago_datetime_range': [make_aware(seven_days_ago_datetime_min), make_aware(seven_days_ago_datetime_max)],
        'nine_days_ago': nine_days_ago,
        'nine_days_ago_datetime_range': [make_aware(nine_days_ago_datetime_min), make_aware(nine_days_ago_datetime_max)],
        'fifteen_days_ago': fifteen_days_ago,
        'fifteen_days_ago_datetime_range': [make_aware(fifteen_days_ago_datetime_min), make_aware(fifteen_days_ago_datetime_max)],
        'thirty_days_ago': thirty_days_ago,
        'thirty_days_ago_datetime_range': [make_aware(thirty_days_ago_datetime_min), make_aware(thirty_days_ago_datetime_max)],
        'today': today,
        'today_datetime_range': [make_aware(today_datetime_min), make_aware(today_datetime_max)],
        'last_week_date_range': last_week_date_range,
        'last_week_datetime_range': [make_aware(last_week_datetime_min), make_aware(last_week_datetime_max)],
        'week_date_range': week_date_range,
        'week_datetime_range': [make_aware(week_datetime_min), make_aware(week_datetime_max)],
        'last_month_date_range': last_month_date_range,
        'last_month_datetime_range': [make_aware(last_month_datetime_min), make_aware(last_month_datetime_max)],
        'month_date_range': month_date_range,
        'month_datetime_range': [make_aware(month_datetime_min), make_aware(month_datetime_max)]
    }
    return data


def log_signal(m2m_fields=None):
    if m2m_fields is None:
        m2m_fields = []

    def log_decorator(cls):
        pre_save.connect(model_action_pre_save_log, sender=cls)
        post_save.connect(model_action_post_save_log, sender=cls)
        pre_delete.connect(model_action_delete_log, sender=cls)
        for m2m_field in m2m_fields:
            m2m_changed.connect(model_action_save_m2m_log, getattr(cls, m2m_field).through)
        return cls
    return log_decorator


def check_dashboard_permission(request, resource):

    user_roles = request.user.get_allowed_resources

    if resource not in user_roles and not request.user.is_admin:
        raise PermissionDenied()