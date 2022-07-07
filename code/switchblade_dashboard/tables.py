from django.utils import timezone
from django.utils.safestring import mark_safe
from django_tables2 import tables, columns

from .models import AuditLog


class Table(tables.Table):
    select_row = columns.CheckBoxColumn(accessor='pk',
                                        attrs={
                                            "th": {
                                                "style": 'width: 15px'
                                            },
                                            "th__input": {
                                                "onclick": "toggle(this)"
                                            },
                                            "td": {
                                                "style": 'width: 15px'
                                            },
                                        },
                                        orderable=False,
                                        exclude_from_export=True)
    actions = columns.TemplateColumn(template_name='switchblade_dashboard/tags/table_action.html',
                                     attrs={
                                         "th": {
                                             "style": 'width: 90px'
                                         },
                                         "td": {
                                             "style": 'width: 90px'
                                         },
                                     },
                                     orderable=False,
                                     exclude_from_export=True)

    id = columns.Column(verbose_name='ID', accessor='pk', visible=False)
    delete = columns.BooleanColumn(verbose_name='DELETE', empty_values=(), visible=False)

    def render_delete(self):
        return False

    class Meta:
        # model = City
        attrs = {
            'class': 'table table-bordered table-hover dataTable no-footer',
            'th': {
                '_ordering': {
                    'orderable': 'sorting',
                    'ascending': 'sorting_asc',
                    'descending': 'sorting_desc'
                }
            }
        }
        sequence = ('select_row', 'id', 'actions', '...', 'delete')
        # exclude = ('select_row', )
        exclude_from_export = []
        exclude_from_template = []
        ignore_on_template_import = []
        auxiliary_columns = []


class AuditLogTable(Table):
    content_object = columns.Column(verbose_name='Object Reference', accessor='content_object', visible=True)
    trace = columns.JSONColumn(verbose_name='Traceback', accessor='trace', json_dumps_kwargs={'ensure_ascii': False, 'indent': 2})

    class Meta(Table.Meta):
        model = AuditLog
        fields = ['level', 'created_on', 'msg', 'created_by', 'content_object', 'trace']
        exclude = ('select_row', 'actions')

    def render_level(self, record, value):
        color = AuditLog.LEVEL_COLOR.get(value, 'black')
        return mark_safe(f'<span style="color: {color}""><b>{value}</b></span>')

    def render_created_on(self, record, value):
        return timezone.localtime(value).strftime("%Y-%m-%d %H:%M")

    def render_content_object(self, record, value):
        try:
            return mark_safe(f'<a href="{value.get_absolute_url()}" target="_blank">{value}</a>')
        except:
            return value

    def value_level(self, record, value):
        return value
