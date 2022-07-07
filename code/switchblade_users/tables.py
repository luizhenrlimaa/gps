from switchblade_dashboard import tables as dashboard_table
from django_tables2 import Column, columns

from .models import User, Role


class UserTable(dashboard_table.Table):

    name = columns.Column(empty_values=(), verbose_name='Name', order_by=('first_name', 'last_name'))

    email = columns.Column(accessor='email', verbose_name='Email')

    def render_name(self, record):
        return str(record)

    class Meta(dashboard_table.Table.Meta):
        model = User
        fields = ['name', 'email', 'is_admin', 'is_active', 'last_login']
        # exclude = ('select_row', )
        exclude_from_template = ['is_admin', 'last_login']
        ignore_on_template_import = ['name', 'email']


class RoleTable(dashboard_table.Table):

    class Meta(dashboard_table.Table.Meta):
        model = Role
        fields = ['description', 'active', ]
        exclude = ('select_row', )
