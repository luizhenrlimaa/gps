import datetime

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field
from django.core.exceptions import ValidationError
from django.forms import TextInput, Textarea, DurationField


class DateInput(TextInput):
    input_type = 'text'
    template_name = 'switchblade_dashboard/forms/widgets/date_input.html'


class FloatDurationField(DurationField):

    def prepare_value(self, value):
        if isinstance(value, datetime.timedelta):
            return value / datetime.timedelta(hours=1)
        return value

    def to_python(self, value):
        if value in self.empty_values:
            return None
        if isinstance(value, datetime.timedelta):
            return value
        try:
            value = datetime.timedelta(hours=float(value))
        except:
            raise ValidationError(self.error_messages['invalid'], code='invalid')
        if value is None:
            raise ValidationError(self.error_messages['invalid'], code='invalid')
        return value


class DateTimeInput(TextInput):
    input_type = 'text'
    template_name = 'switchblade_dashboard/forms/widgets/date_time_input.html'


class RichTextInput(Textarea):
    template_name = 'switchblade_dashboard/forms/widgets/rich_text_input.html'


class DateMonthInput(TextInput):
    input_type = 'text'
    template_name = 'switchblade_dashboard/forms/widgets/date_month_input.html'


class TimeInput(TextInput):
    input_type = 'text'
    template_name = 'switchblade_dashboard/forms/widgets/time_input.html'


class DashboardDateMonthInput(DateMonthInput):
    template_name = 'switchblade_dashboard/forms/dashboard_widgets/dashboard_date_month_input.html'


class DashboardDateInput(DateInput):
    template_name = 'switchblade_dashboard/forms/dashboard_widgets/dashboard_date_input.html'


class DateRangeInput(TextInput):
    input_type = 'text'
    template_name = 'switchblade_dashboard/forms/widgets/date_range_input.html'


class DateTimeRangeInput(TextInput):
    input_type = 'text'
    template_name = 'switchblade_dashboard/forms/widgets/date_time_range_input.html'


class ToggleButtonInput(TextInput):
    input_type = 'checkbox'
    template_name = 'switchblade_dashboard/forms/widgets/toggle_button_input.html'


class InlineFieldWithLabel(Field):
    template_name = 'switchblade_dashboard/forms/widgets/inline_field_with_label.html'


class TabularFormSetHelper(FormHelper):
    type = 'tabular'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_tag = False
        # self.html5_required = True
        # self.error_text_inline = False
        self.template = 'crispy/bootstrap3/table_inline_formset.html'
        self.include_media = True
        self.disable_csrf = True


class StackedFormSetHelper(FormHelper):
    type = 'stacked'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_tag = False
        # self.html5_required = True
        # self.form_class = 'form-horizontal'
        self.label_class = 'col-lg-2'
        self.field_class = 'col-lg-10'
        self.include_media = True
        self.disable_csrf = True


class FormSetHelper(FormHelper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_tag = False
        # self.html5_required = False
        # self.form_class = 'form-horizontal'
        self.label_class = 'col-lg-2'
        self.field_class = 'col-lg-10'


class FilterFormSetHelper(FormHelper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_tag = False
        # self.form_method = 'GET'
        # self.html5_required = False
        # self.form_class = 'form-horizontal'
        self.label_class = 'col-lg-2'
        self.field_class = 'col-lg-10'
        self.disable_csrf = True
        # self.add_input(Submit('submit', 'Filter'))
        # self.add_input(Reset('reset', 'Clear'))


class FieldsColumnsFormSetHelper(FormHelper):
    col_lg_size = 3
    col_md_size = 4
    col_sm_size = 6
    col_xs_size = 12

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_tag = False
        self.disable_csrf = True
        self.col_lg_size = self.col_lg_size
        self.col_md_size = self.col_md_size
        self.col_sm_size = self.col_sm_size
        self.col_xs_size = self.col_xs_size


class DashboardFilterHelper(FormHelper):
    col_sm_size = 12
    col_md_size = 12

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_tag = False
        self.disable_csrf = True
        self.col_md_size = self.col_md_size
        self.col_sm_size = self.col_sm_size


class DashboardExtraCommandsHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_tag = False
        self.form_class = 'form-inline'
        self.field_template = 'bootstrap3/layout/inline_field.html'
        self.disable_csrf = True


class ReadField(Field):
    template = 'crispy/readonly.html'

    def __init__(self, *args, **kwargs):
        kwargs['type'] = 'hidden'
        super().__init__(*args, **kwargs)
