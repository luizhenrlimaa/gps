import json
from difflib import SequenceMatcher
from io import BytesIO

import pandas as pd
from abc import abstractmethod

from celery.result import AsyncResult
from crispy_forms.utils import render_crispy_form
from django.conf import settings
from django.contrib import messages
from django.contrib.gis.geos import Polygon, MultiPoint, Point
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction
from django.db.models import ProtectedError, DateField, DateTimeField, FloatField, IntegerField
from django.db.models.signals import pre_delete
from django.utils.translation import gettext as _

from django.forms import inlineformset_factory, all_valid
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone, text
from django.template.loader import render_to_string
from django.views import View
from django_tables2 import RequestConfig, LazyPaginator, A
from django_tables2.export import TableExport

from menu import Menu

from menu.templatetags.menu import MenuNode
# from silk.profiling.profiler import silk_profile
from registros.models import Certificado, Aluno
from switchblade_users.models import User
from .filters import AuditLogFilter
from .forms import FormSetHelper, FieldsColumnsFormSetHelper, DashboardFilterHelper, DashboardExtraCommandsHelper
from .models import AuditLog
from .signals import model_action_delete_log
from .smart_dash_components import COMPONENT_CHART_TYPE, COMPONENT_TABLE_TYPE, COMPONENT_CARD_TYPE, COMPONENT_TYPES, \
    COMPONENT_CUSTOM_HTML_TYPE
from .tables import AuditLogTable
from .utils import check_dashboard_permission


def find_selected_menu(context):
    # if a 500 error happens we get an empty context, in which case
    # we should just return to let the 500.html template render
    if 'request' not in context:
        return '<!-- menu failed to render due to missing request in the context -->'

    request = context['request']
    menus = Menu.process(request)

    found_item = {'item': None, 'similarity': 0}

    def iterate_over_items(items):
        for item in items:
            if item.selected:
                similarity = SequenceMatcher(None, request.path, item.url).ratio()
                if not found_item['item'] or similarity > found_item['similarity']:
                    found_item['item'] = item
                    found_item['similarity'] = similarity
            if item.children:
                iterate_over_items(item.children)

    for menu in menus:
        iterate_over_items(menus[menu])

    # set the items in our context
    return found_item['item']


class DashboardBaseView(View):
    resource_type = None
    resource = None

    page_title = _('Page Title')
    header = _('Page Header')

    object = None
    template_name = None
    extra_context = {}

    render_template = ''
    request = None

    def get_context(self):
        pass

    def get_extra_context(self):
        return self.extra_context

    def get(self, request):
        self.request = request
        context = self.get_render_context()
        return render(request, self.render_template, context)

    @classmethod
    def get_resource(cls, type_name=None):

        type_name = type_name or cls.resource_type

        if cls.resource_type in ['report', 'smart_report', 'chart']:
            return f'{cls.resource}.{type_name or cls.resource_type}'
        if cls.resource:
            return f'{cls.resource}.{type_name}'
        elif cls.object:
            return f'{cls.object._meta.model_name}.{type_name}'
        else:
            return None

    def _get_base_context(self):

        extra_content = self.get_extra_context()
        self.extra_context.update(extra_content)

        return {
            'PageTitle': self.page_title,
            'Header': self.header,
            'ExtraContext': self.extra_context,
        }

    def get_render_context(self):

        data = self._get_base_context()

        try:
            data.update(self.get_context())
            data['menu_info'] = find_selected_menu({'request': self.request})
        except Exception as e:
            pass

        return data


class DashboardIndexView(DashboardBaseView):
    resource_type = 'index'

    columns = [6, 6]

    def get_context(self):

        context = {'request': self.request}
        MenuNode().render(context)
        del (context['request'])

        cols_num = len(self.columns)
        menu_items = [{'col_size': self.columns[i], 'items': []} for i in range(cols_num)]

        c = 0
        column = 0

        for item in context['menus']['sidebar']:
            if item.area == context['selected_menu'].area and item.list:
                c += 1
                if c % cols_num != 0:
                    menu_items[column]['items'].append(item)
                    column += 1
                else:
                    menu_items[column]['items'].append(item)
                    column = 0

        context.update({'menu_items': menu_items})

        return context

    def get(self, request, *args, **kwargs):
        return render(request, 'switchblade_dashboard/index_page.html', self.get_render_context())


def Index(request):
    template_name = 'switchblade_dashboard/index.html'
    context = {}

    aluno = Aluno.objects.filter(user=request.user)

    if aluno or request.user.is_admin:
        h = 0
        certificado = Certificado.objects.filter(aluno=aluno)


        context = {
            'aluno' : aluno,
            'user' : request.user,
        }

    else:
        context = {
            'a' : "aaaa",
        }

    return render(request, template_name, context)


class DashboardListView(DashboardBaseView):
    resource_type = 'list'

    add_button_title = _('New')
    add_button_url = ''
    columns = {}
    options = []
    actions = {}
    template_name = 'switchblade_dashboard/list.html'
    template_name_table = 'switchblade_dashboard/list_table.html'
    table_class = None
    filter_class = None
    lazy_pagination = False
    per_page = 50

    show_option_detail = True
    show_option_update = True
    show_option_delete = True
    show_export_button = True

    allow_export_import = False
    allow_insert_by_template = True
    allow_delete_by_template = True
    form_template_class = None

    send_filtered_qs_to_template = False

    custom_template_key = {}
    custom_template_dtype = {}

    filter_form_helper = FieldsColumnsFormSetHelper

    form_field_lg_size = 3
    form_field_sm_size = 3
    form_field_md_size = 3
    form_field_xs_size = 12

    template_date_time_format = '%Y-%m-%d %H:%M'
    template_date_format = '%Y-%m-%d'

    @abstractmethod
    def get_queryset(self):
        return self.object.objects.filter()

    def get_table_class(self, qs):
        return self.table_class(qs)

    def get_context(self):

        data = self._get_base_context()

        self.options = []

        if self.add_button_title and self.add_button_url:
            data['AddButton'] = {}
            data['AddButton']['Title'] = self.add_button_title
            data['AddButton']['Url'] = self.add_button_url
        if self.show_export_button:
            data['ExportButton'] = True
        if self.allow_export_import:
            data['TemplateButtons'] = True
            data['ColumnsToIgnore'] = self.get_columns_to_ignore_on_template()
        if self.columns:
            data['Columns'] = self.columns
        if self.actions:
            data['Actions'] = self.actions

        # TEMPORARY
        if not self.table_class:
            data['Objects'] = self.get_queryset()

        data['CreateResource'] = self.get_resource(DashboardCreateView.resource_type)
        data['DetailResource'] = self.get_resource(DashboardDetailView.resource_type)
        data['UpdateResource'] = self.get_resource(DashboardUpdateView.resource_type)
        data['DeleteResource'] = self.get_resource(DashboardDeleteView.resource_type)
        data['ExportResource'] = self.get_resource('export')
        data['TemplateResource'] = self.get_resource('template')
        data['ButtonDetail'] = self.show_option_detail
        data['ButtonUpdate'] = self.show_option_update
        data['ButtonDelete'] = self.show_option_delete

        return data

    # @silk_profile(name='list-view')
    def get(self, request, *args, **kwargs):

        table = None
        filter = None
        # filter_helper = None
        template_name = self.template_name

        self.extra_context = self.get_extra_context()

        qs = self.get_queryset()

        if self.filter_class:
            filter = self.filter_class(request.GET, queryset=qs)
            if self.filter_form_helper is not None:
                filter.helper = self.filter_form_helper

        # if self.filter_class:
        #     filter = self.filter_class(request.GET, queryset=qs)

        # self.table_class = self.get_table_class()

        if self.table_class:

            template_name = self.template_name_table

            if filter:
                qs = filter.qs
            table = self.get_table_class(qs)

            if self.lazy_pagination:
                RequestConfig(
                    request, paginate={'per_page': self.per_page, "paginator_class": LazyPaginator}
                ).configure(table)
            else:
                RequestConfig(request, paginate={'per_page': self.per_page}).configure(table)

        check_dashboard_permission(self.request, self.get_resource())
        export_format = request.GET.get('_export', None)

        if TableExport.is_valid_format(export_format):
            exporter = TableExport(
                export_format, table, exclude_columns=['id', 'delete'] + self.table_class.Meta.exclude_from_export)

            return exporter.response(
                f'export-{text.slugify(self.header)}-'
                f'{timezone.localtime(timezone.now()).strftime("%Y%m%d%H%M")}.{export_format}'
            )

        export_template = request.GET.get('_template', None)

        if export_template == 'export':
            exporter = TableExport('xlsx', table, exclude_columns=self.table_class.Meta.exclude_from_template)
            return exporter.response(
                f'template-{text.slugify(self.header)}-{timezone.localtime(timezone.now()).strftime("%Y%m%d%H%M")}.xlsx')

        context = self.get_render_context()

        if filter:
            rows = filter.qs.count()
        else:
            rows = qs.count()

        context.update({'list_data': context, 'table': table, 'filter': filter, 'rows': rows})

        if self.send_filtered_qs_to_template:
            context['qs'] = filter.qs

        return render(request, template_name, context)

    def delete_custom_validation(self, ids):
        pass

    def _delete_by_ids(self, ids, request=None):
        if ids:
            try:
                if request is not None:
                    check_dashboard_permission(self.request, self.get_resource(DashboardDeleteView.resource_type))
                if not self.allow_delete_by_template:
                    raise PermissionDenied()
                self.delete_custom_validation(ids)
                self.get_queryset().filter(pk__in=ids).delete()
            except ProtectedError:
                raise Exception(_('Cannot delete some objects because they are related to others.'))
            except PermissionDenied:
                raise Exception(_('You are not allowed to delete items.'))
            except Exception as e:
                raise Exception(e)
        pass

    def _get_template_mapping(self):

        template_mapping = {}

        for k, v in self.table_class.base_columns.items():

            if not v.exclude_from_export \
                    and v.verbose_name is not None and \
                    k not in self.table_class.Meta.exclude_from_template and \
                    k not in self.table_class.Meta.auxiliary_columns and \
                    k not in self.table_class.Meta.ignore_on_template_import \
                    and v.verbose_name not in ['ID', 'DELETE'] \
                    and v.verbose_name not in self.custom_template_key.keys():
                accessor = A(k).get_field(self.object)

                template_mapping[v.verbose_name] = {
                    'key': k,
                    'attname': accessor.name,
                    'is_relation': accessor.is_relation,
                    'related_model': accessor.related_model,
                    'is_date_field': False,
                    'is_date_time_field': False,
                    'is_float': False,
                    'is_integer': False,
                    'fk': accessor.many_to_one if accessor.is_relation else False,
                    'm2m': accessor.many_to_many if accessor.is_relation else False,
                    'choices': accessor.choices,
                    'choices_array': False  # to deal with ArrayField
                }

                if isinstance(accessor, DateTimeField):
                    template_mapping[v.verbose_name].update({
                        'is_date_time_field': True,
                    })
                elif isinstance(accessor, DateField):
                    template_mapping[v.verbose_name].update({
                        'is_date_field': True
                    })

                if isinstance(accessor, FloatField):
                    template_mapping[v.verbose_name].update({
                        'is_float': True,
                    })
                elif isinstance(accessor, IntegerField):
                    template_mapping[v.verbose_name].update({
                        'is_integer': True
                    })

        template_mapping.update(self.custom_template_key)

        return template_mapping

    def get_columns_to_ignore_on_template(self):
        return [v.verbose_name for k, v in self.table_class.base_columns.items() if
                k in self.table_class.Meta.ignore_on_template_import and k not in self.table_class.Meta.exclude_from_template]

    def _format_datetime_df(self, df, template_mapping):
        date_time_columns = [k for k, v in template_mapping.items() if v['is_date_time_field']]
        date_columns = [k for k, v in template_mapping.items() if v['is_date_field']]

        for column in date_time_columns:
            df[column] = pd.to_datetime(df[column].values.astype(str), errors='coerce',
                                        format=self.template_date_time_format)

        for column in date_columns:
            df[column] = pd.to_datetime(df[column].values.astype(str), errors='coerce',
                                        format=self.template_date_format)

        return df

    def _format_number_df(self, df, template_mapping):
        integer_columns = [k for k, v in template_mapping.items() if v['is_integer'] and not v['choices']]
        float_columns = [k for k, v in template_mapping.items() if v['is_float'] and not v['choices']]

        for column in integer_columns:
            df[column] = pd.to_numeric(df[column], errors='coerce', downcast='integer')

        for column in float_columns:
            df[column] = pd.to_numeric(df[column], errors='coerce', downcast='float')

        return df

    def _format_template_df(self, df, template_mapping):

        df = df.copy()

        if df.empty:
            return df

        for column, data in template_mapping.items():

            if data['is_relation'] and data['fk']:  # FK
                try:
                    df[column] = df[column].apply(
                        lambda s: data['related_model']._filter_by_str(s.strip()) if s != '-' else None)
                except Exception as e:
                    raise ValueError(_(f'Error on column FK {column}: {e}'))
            elif data['is_relation'] and data['m2m']:  # M2M
                try:
                    df[column] = df[column].apply(lambda s: [data['related_model']._filter_by_str(i.strip()) for i in
                                                             s.split(',')] if s != '-' else [])
                except Exception as e:
                    raise ValueError(_(f'Error on column M2M {column}:{e}'))
            elif not data['is_relation'] and len(data['choices']) > 0:  # choices
                choices = {v: k for k, v in dict(data['choices']).items()}
                try:
                    if data['choices_array']:
                        df[column] = df[column].apply(
                            lambda s: [choices[i.strip()] for i in s.split(',')] if s != '-' else [])
                    else:
                        df[column] = df[column].apply(lambda s: choices[s] if s != '-' else None)
                except Exception as e:
                    raise ValueError(_(f"Choice {e} for column {column} not found."))

            df[column].replace('-', '', inplace=True)
            df[column].fillna('', inplace=True)

            df.rename(columns={column: data['attname']}, inplace=True)

        df.rename(columns={'ID': 'id'}, inplace=True)

        df.drop(columns=['DELETE'], errors='ignore', inplace=True)

        df.drop(columns=self.get_columns_to_ignore_on_template(), errors='ignore', inplace=True)

        return df

    def set_extra_include(self, obj):
        return obj

    def process_auxiliary_columns(self, form_obj, instance, record, pre_save=True):
        if pre_save:
            return form_obj
        pass

    def _insert_from_dict(self, records, user, request=None, force_insert_with_id=False):

        if records:

            try:
                if request is not None:
                    check_dashboard_permission(self.request, self.get_resource(DashboardCreateView.resource_type))
                if not self.allow_insert_by_template:
                    raise PermissionDenied()
            except PermissionDenied:
                raise Exception(_('You are not allowed to insert items.'))

            try:
                for record in records:

                    # remove id
                    if not force_insert_with_id:
                        record.pop('id', None)

                    try:
                        form_obj = self.form_template_class(record)
                    except:
                        raise Exception(_('Please define a form template class.'))

                    if form_obj.is_valid():
                        form_obj = self.process_auxiliary_columns(form_obj, None, record, pre_save=True)
                        obj = form_obj.save(commit=False)
                        if hasattr(self.object, 'created_by') and 'created_by' not in record:
                            obj.created_by = user
                        if hasattr(self.object, 'modified_by') and 'modified_by' not in record:
                            obj.modified_by = user
                        obj = self.set_extra_include(obj)
                        if force_insert_with_id:
                            obj.pk = record['id']
                        obj.save()
                        form_obj.save_m2m()
                        self.process_auxiliary_columns(form_obj, obj, record, pre_save=False)
                    else:
                        for k, v in form_obj.errors.items():
                            for error in v:
                                raise Exception(
                                    _(f'Error on save - Field: {k} - Value: {form_obj.data.get(k, None)} - {error}'))
            except Exception as e:
                raise Exception(e)

    def _update_from_dict(self, records, user, request=None):

        if records:

            try:
                if request is not None:
                    check_dashboard_permission(self.request, self.get_resource(DashboardUpdateView.resource_type))
            except PermissionDenied:
                raise Exception(_('You are not allowed to update items.'))

            try:
                for record in records:

                    obj_qs = self.get_queryset().filter(pk=record['id'])

                    if obj_qs.exists():
                        instance = obj_qs.first()

                        if hasattr(self.object, 'modified_by') and 'modified_by' not in record:
                            record['modified_by'] = user

                        try:
                            form_obj = self.form_template_class(record, instance=instance)
                        except:
                            raise Exception(_('Please define a form template class.'))

                        if form_obj.is_valid():
                            form_obj = self.process_auxiliary_columns(form_obj, instance, record, pre_save=True)
                            form_obj.save()
                            self.process_auxiliary_columns(form_obj, instance, record, pre_save=False)
                        else:
                            for k, v in form_obj.errors.items():
                                for error in v:
                                    raise Exception(
                                        _(f'Error on update - Field: {k} - Value: {form_obj.data.get(k, None)} - {error}'))

            except Exception as e:
                raise Exception(e)

    def import_template(self, template_df, user, request=None, force_insert_with_id=False):

        with transaction.atomic():
            try:
                sid = transaction.savepoint()
                # get objects to delete with ID
                if not force_insert_with_id:
                    template_df['ID'] = pd.to_numeric(template_df['ID'], errors='coerce', downcast='integer')
                    template_df['ID'] = template_df['ID'].fillna(0).astype(int)

                items_to_delete = template_df.loc[template_df['DELETE'] == True].dropna(axis=0, subset=['ID'])[
                    'ID'].tolist()
                items_to_update_initial = template_df.loc[template_df['DELETE'] == False].dropna(axis=0,
                                                                                                 subset=['ID'])
                items_to_update_initial.fillna(value='-', inplace=True)
                items_to_update_initial_ids = items_to_update_initial['ID'].tolist()
                filter_qs = self.get_queryset().filter(pk__in=items_to_update_initial_ids)
                ids_not_allowed = list(set(items_to_update_initial_ids) - set(filter_qs.values_list('pk', flat=True)))
                items_to_update_initial = items_to_update_initial[~items_to_update_initial['ID'].isin(ids_not_allowed)]
                items_to_update_initial_table = self.get_table_class(filter_qs)
                items_to_update_initial_table = TableExport('xlsx', items_to_update_initial_table,
                                                            exclude_columns=self.table_class.Meta.exclude_from_template)
                items_to_update_initial_df_original = items_to_update_initial_table.dataset.df
                items_to_update_initial_df_original.fillna(value='-', inplace=True)

                template_mapping = self._get_template_mapping()
                items_to_update_initial = self._format_datetime_df(items_to_update_initial, template_mapping)
                items_to_update_initial_df_original = self._format_datetime_df(items_to_update_initial_df_original,
                                                                               template_mapping)

                items_to_update_initial = self._format_number_df(items_to_update_initial, template_mapping)
                items_to_update_initial_df_original = self._format_number_df(items_to_update_initial_df_original,
                                                                             template_mapping)

                items_to_update_initial.drop(columns=self.get_columns_to_ignore_on_template(), inplace=True)
                items_to_update_initial_df_original.drop(columns=self.get_columns_to_ignore_on_template(), inplace=True)

                items_to_update = pd.concat(
                    [items_to_update_initial.astype(str), items_to_update_initial_df_original.astype(str),
                     items_to_update_initial_df_original.astype(str)]).drop_duplicates(keep=False)

                if force_insert_with_id:
                    items_to_insert = template_df.loc[
                        (template_df.ID.isnull()) | (template_df.ID.isin(ids_not_allowed))].fillna(value='-')
                else:
                    items_to_insert = template_df.loc[template_df.ID.isnull() | template_df['ID'] == 0].fillna(value='-')

                items_to_insert = items_to_insert.astype(str)
                items_to_insert = self._format_datetime_df(items_to_insert, template_mapping)
                items_to_insert = self._format_number_df(items_to_insert, template_mapping)
                items_to_insert.drop(columns=self.get_columns_to_ignore_on_template(), inplace=True)

                items_to_update = self._format_datetime_df(items_to_update, template_mapping)
                items_to_update = self._format_number_df(items_to_update, template_mapping)

                dict_to_insert = self._format_template_df(items_to_insert, template_mapping).to_dict(orient='records')

                dict_to_update = self._format_template_df(items_to_update, template_mapping).to_dict(orient='records')

                self._insert_from_dict(dict_to_insert, user, request, force_insert_with_id)
                self._update_from_dict(dict_to_update, user, request)
                self._delete_by_ids(items_to_delete, request)
                transaction.savepoint_commit(sid)

                if request is not None:
                    messages.success(request, _('Records updated successfully.'))
                else:
                    return True

                # get objects with ID and compare to update
                # insert new objects
            except Exception as e:
                try:
                    transaction.savepoint_rollback(sid)
                except:
                    pass
                if request is not None:
                    messages.error(request, _('It was not possible to process template. Check messages and try again.'))
                    messages.warning(request, e)
                else:
                    raise Exception(e)

    def post(self, request, *args, **kwargs):

        # to deal with actions

        action = request.POST.get('action', None)
        ids = json.loads(request.POST.get('ids', '[]'))
        action_item = self.actions.get(action, None)
        template = request.POST.get('_template', None)
        file = request.FILES.get('file', None)

        if template == 'import' and file:
            template_df = pd.read_excel(file, dtype=self.custom_template_dtype)
            table_columns = [v.verbose_name for k, v in self.table_class.base_columns.items() if
                             not v.exclude_from_export and v.verbose_name is not None and k not in self.table_class.Meta.exclude_from_template]
            if sorted(template_df.columns.tolist()) == sorted(table_columns):

                self.import_template(template_df, request.user, request)

            else:
                messages.warning(request, _('Import and export template columns must match.'))
        elif action_item and self.object:

            use_filter_as_qs = action_item.get('use_filter_as_qs', False)
            if use_filter_as_qs:
                ids = list(self.filter_class(request.GET, queryset=self.get_queryset()).qs.values_list('id', flat=True))

            if len(ids) > 0:
                try:
                    is_return_type = action_item.get('return_type', False)
                    method_to_call = getattr(self.object, action_item['function'])
                    if method_to_call:

                        if is_return_type:
                            return method_to_call(request, ids)
                        else:
                            level, message = method_to_call(request, ids)
                            messages.add_message(request, level, message)
                except Warning as w:
                    messages.warning(request, w)
                except Exception as e:
                    messages.error(request, e)
            else:
                messages.warning(request, _('Select at least one item.'))

        else:
            messages.error(request, _('Invalid action'))

        url_encode = request.GET.urlencode()

        if url_encode != '':
            return redirect(request.path_info + '?' + request.GET.urlencode())

        return redirect(request.path_info)


class DashboardDetailView(DashboardBaseView):
    resource_type = 'detail'

    query_string = ''

    rows_before = {}
    rows_based_on_form = None
    rows_after = {}
    rows_set = {}

    show_button_back = True
    show_button_update = True
    show_button_delete = True

    template_name = 'switchblade_dashboard/detail.html'

    validate_owner = False

    @abstractmethod
    def get_queryset(self):
        return None

    def get_context(self):

        data = {}

        if self.rows_based_on_form:
            data['RowsBasedOnForm'] = self.rows_based_on_form
        if self.rows_before:
            data['RowsBefore'] = self.rows_before
        if self.rows_after:
            data['RowsAfter'] = self.rows_after
        if self.rows_set:
            data['RowsSet'] = self.rows_set
        if self.object:
            data['Object'] = self.object
        data['ButtonBack'] = self.show_button_back
        data['ButtonUpdate'] = self.show_button_update
        data['ButtonDelete'] = self.show_button_delete

        data['detail_data'] = data

        return data

    def set_object(self, request, pk):

        if not pk:
            raise ValidationError('Needs pk')

        if hasattr(self, 'get_queryset'):
            obj = get_object_or_404(self.get_queryset(), pk=pk)
        else:
            obj = get_object_or_404(self.object, pk=pk)

        if self.validate_owner and obj.owner != request.user:
            raise PermissionDenied()

        self.object = obj

    def _render_dashboard(self, request, pk=None):

        self.query_string = request.META['QUERY_STRING']

        data_dict = self.get_render_context()

        if not self.query_string:
            return render(request, self.template_name, data_dict)

        data_dict['query_string'] = self.query_string

        return render(request, self.template_name, data_dict)

    # @silk_profile(name='detail-view')
    def get(self, request, pk, *args, **kwargs):

        check_dashboard_permission(self.request, self.get_resource())

        self.set_object(request, pk)

        return self._render_dashboard(request, pk)


class DashboardCreateView(DashboardBaseView):
    resource_type = 'create'

    form_class = None

    show_button_back = True
    show_button_save_add = True
    show_button_save_continue = False

    owner_include = False

    success_message = ''
    presave_message = ''
    success_redirect = ''
    query_string = ''

    initial = {}

    inlines = []
    inlines_formsets = []

    form_helper = FormSetHelper

    template_name = 'switchblade_dashboard/form.html'

    def set_extra_include(self, obj):
        return obj

    def set_inlines_formsets(self, request=None, obj=None):

        formsets = []

        for fs in self.inlines:

            formset = inlineformset_factory(
                self.object, fs['model'], form=fs['form'], extra=1, fk_name=fs.get('fk_name', None))

            if request:

                formsets.append(
                    (
                        fs,
                        formset(
                            request.POST or None,
                            request.FILES or None,
                            instance=obj,
                            prefix=fs['model']._meta.model_name
                        ),
                        fs['helper'],
                        {'sortable': fs.get('sortable', False)}
                    )
                )

            else:
                formsets.append(
                    (
                        fs,
                        formset(
                            prefix=fs['model']._meta.model_name
                        ),
                        fs['helper'],
                        {'sortable': fs.get('sortable', False)}
                    )
                )

        self.inlines_formsets = formsets

    def get_context(self):

        data = {}

        if self.form_class:
            data['Form'] = self.form_class
        if self.form_helper:
            data['FormHelper'] = self.form_helper
        data['ButtonBack'] = self.show_button_back
        data['ButtonSaveAdd'] = self.show_button_save_add
        data['ButtonSaveContinue'] = self.show_button_save_continue
        if self.inlines:
            if not self.inlines_formsets:
                self.set_inlines_formsets()
            data['Inlines'] = self.inlines_formsets
        if self.show_button_save_add:
            data['ButtonSaveAddUrl'] = self.request.path

        return {'form_data': data}

    def get(self, request, parent=None, *args, **kwargs):

        check_dashboard_permission(self.request, self.get_resource())

        if self.presave_message:
            messages.info(request, self.presave_message)

        if kwargs:
            self.form_class = self.get_form(request, initial=kwargs)

        self.query_string = request.META['QUERY_STRING']

        data_dict = self.get_render_context()

        if not self.query_string:
            return render(request, self.template_name, data_dict)

        data_dict['query_string'] = self.query_string

        return render(request, self.template_name, data_dict)

    def get_form(self, request, initial=None, *args, **kwargs):

        self.form_class = self.form_class(request.POST or None, request.FILES or None, initial=initial)

        return self.form_class

    def post(self, request, parent=None, *args, **kwargs):

        check_dashboard_permission(self.request, self.get_resource())

        form = self.get_form(request)
        self.set_inlines_formsets(request)
        self.query_string = request.META['QUERY_STRING']

        btn_save_add = request.POST.get('btn_save_add', None)
        btn_save_continue = request.POST.get('btn_save_continue', None)

        if form.is_valid():

            obj = form.save(commit=False)
            self.set_inlines_formsets(request, obj)
            formsets = [inline[1] for inline in self.inlines_formsets]

            if all_valid(formsets):

                if self.owner_include:
                    obj.created_by = request.user
                    obj.modified_by = request.user

                obj = self.set_extra_include(obj)

                try:

                    with transaction.atomic():

                        obj.full_clean()
                        obj.save()
                        form.save_m2m()

                        for inlines_formset in self.inlines_formsets:
                            formset = inlines_formset[1]
                            inline_objs = formset.save(commit=False)

                            for inline_obj in inline_objs:
                                if inlines_formset[0].get('owner_include', False):
                                    inline_obj.modified_by = request.user
                                if not inline_obj.pk and inlines_formset[0].get('owner_include', False):
                                    inline_obj.created_by = request.user

                                inline_obj.save()

                            formset.save_m2m()

                        messages.success(request, self.success_message)

                        if btn_save_add:
                            return redirect(btn_save_add)

                        if btn_save_continue:
                            return redirect(obj.get_update_url())

                        if self.query_string:
                            return redirect(reverse(self.success_redirect) + '?' + self.query_string)

                        return redirect(self.success_redirect)

                except Warning as w:
                    messages.warning(request, w)
                except Exception as e:
                    has_messages = hasattr(e, 'message_dict')
                    if has_messages:
                        for item, message in e.message_dict:
                            messages.error(request, f'{item}: {message}')
                    else:
                        messages.error(request, e)
        else:
            messages.warning(request, _('Please check the errors below.'))

        return render(request, self.template_name, self.get_render_context())


class DashboardUpdateView(DashboardBaseView):
    resource_type = 'update'

    form_class = None
    show_button_back = True

    success_message = ''
    success_redirect = ''
    query_string = ''

    validate_owner = False
    owner_include = False

    form_helper = FormSetHelper

    template_name = 'switchblade_dashboard/form.html'

    inlines = []
    inlines_formsets = []

    @abstractmethod
    def get_queryset(self):
        return None

    def set_extra_include(self, obj):
        return obj

    def set_initial_form(self):
        return None

    def get_form(self):
        return self.form_class

    def set_inlines_formsets(self, request=None):

        formsets = []

        for fs in self.inlines:

            formset = inlineformset_factory(
                self.object.__class__, fs['model'], form=fs['form'], extra=1, fk_name=fs.get('fk_name', None)
            )

            if request:
                formset_instance = formset(
                    request.POST or None,
                    request.FILES or None,
                    queryset=fs.get('queryset', fs['model'].objects.all()),
                    instance=self.object,
                    prefix=fs['model']._meta.model_name
                )
            else:
                formset_instance = formset(
                    queryset=fs.get('queryset', fs['model'].objects.all()),
                    instance=self.object,
                    prefix=fs['model']._meta.model_name
                )

            formsets.append((fs, formset_instance, fs['helper'], {'sortable': fs.get('sortable', False)}))

        self.inlines_formsets = formsets

    def get_context(self):

        data = {}

        if self.form_class:
            data['Form'] = self.form_class
        if self.object:
            data['Object'] = self.object
        if self.form_helper:
            data['FormHelper'] = self.form_helper
        if self.inlines:
            if not self.inlines_formsets:
                self.set_inlines_formsets()
            data['Inlines'] = self.inlines_formsets
        data['ButtonBack'] = self.show_button_back

        return data

    def set_form(self, request, *args, **kwargs):

        self.form_class = self.get_form()(request.POST or None, request.FILES or None, instance=self.object,
                                          initial=self.set_initial_form())

    def set_object(self, request, pk):
        if not pk:
            raise ValidationError(_('Needs pk'))

        if hasattr(self, 'get_queryset'):
            obj = get_object_or_404(self.get_queryset(), pk=pk)
        else:
            obj = get_object_or_404(self.object, pk=pk)

        if self.validate_owner and obj.owner != request.user:
            raise PermissionDenied()

        self.object = obj

    def get(self, request, pk=None, *args, **kwargs):

        check_dashboard_permission(self.request, self.get_resource())

        self.set_object(request, pk)
        self.set_form(request)

        context = self.get_render_context()
        context.update({'form_data': context})

        return render(request, self.template_name, context)

    def post(self, request, pk=None, *args, **kwargs):

        check_dashboard_permission(self.request, self.get_resource())

        self.set_object(request, pk)
        self.set_form(request)
        self.set_inlines_formsets(request)
        self.query_string = request.META['QUERY_STRING']

        form = self.form_class

        formsets = [inline[1] for inline in self.inlines_formsets]

        if form.is_valid() and all_valid(formsets):

            obj = form.save(commit=False)

            try:

                with transaction.atomic():

                    if self.owner_include:
                        obj.modified_by = request.user

                    obj = self.set_extra_include(obj)

                    obj.full_clean()
                    obj.save()
                    form.save_m2m()

                    for inlines_formset in self.inlines_formsets:
                        formset = inlines_formset[1]
                        inline_objs = formset.save(commit=False)

                        for inline_obj in inline_objs:
                            if inlines_formset[0].get('owner_include', False):
                                inline_obj.modified_by = request.user
                            if not inline_obj.pk and inlines_formset[0].get('owner_include', False):
                                inline_obj.created_by = request.user

                            inline_obj.save()

                        formset.save_m2m()

                        for deleted_object in formset.deleted_objects:
                            deleted_object.delete()

                    messages.success(request, self.success_message)

                    if self.query_string:
                        return redirect(reverse(self.success_redirect) + '?' + self.query_string)

                    return redirect(self.success_redirect)

            except ProtectedError:
                messages.warning(request, _("Cannot delete some objects because they are related to others."))
            except Warning as w:
                messages.warning(request, w)
            except Exception as e:
                has_messages = hasattr(e, 'messages')
                if has_messages:
                    for message in e.messages:
                        messages.error(request, message)
                else:
                    messages.error(request, e)
        else:
            messages.warning(request, _('Please check the errors below.'))

        return render(request, self.template_name, {'form_data': self.get_render_context()})


class DashboardDeleteView(DashboardBaseView):
    resource_type = 'delete'

    success_message = ''
    success_redirect = ''
    query_string = ''

    validate_owner = False

    def set_object(self, request, pk):

        if not pk:
            raise ValidationError(_('Needs pk'))

        if hasattr(self, 'get_queryset'):
            obj = get_object_or_404(self.get_queryset(), pk=pk)
        else:
            obj = get_object_or_404(self.object, pk=pk)

        if self.validate_owner and obj.created_by != request.user:
            raise PermissionDenied()

        self.object = obj

    def custom_validation(self):
        pass

    def post(self, request, pk=None, *args, **kwargs):

        check_dashboard_permission(self.request, self.get_resource())

        self.set_object(request, pk)
        self.query_string = request.META['QUERY_STRING']

        try:
            self.custom_validation()
            if hasattr(self.object, 'dict_repr'):
                try:
                    pre_delete.disconnect(receiver=model_action_delete_log, sender=self.object.__class__)
                    model_action_delete_log(self.object.__class__, self.object, user_id=request.user.id)
                except:
                    pass
            self.object.delete()
            messages.success(request, self.success_message)
        except ProtectedError:
            messages.warning(request, _("Cannot delete some objects because they are related to others."))
        except Warning as w:
            messages.warning(request, w)
        except Exception as e:
            has_messages = hasattr(e, 'messages')
            if has_messages:
                for message in e.messages:
                    messages.error(request, message)
            else:
                messages.error(request, e)

        if self.query_string:
            return redirect(reverse(self.success_redirect) + '?' + self.query_string)

        return redirect(self.success_redirect)


class DashboardReportView(DashboardBaseView):
    resource_type = 'report'

    form_class = None

    show_button_back = True
    allow_export_xls = True
    allow_export_screen = True

    data = {}
    presave_message = ''

    form_helper = FormSetHelper

    form_template_name = 'switchblade_dashboard/form_report.html'
    list_template_name = 'switchblade_dashboard/list_report.html'

    @abstractmethod
    def process_data(self):

        # dict self.data available
        # example of formatters: formatters = {'created_on': lambda x: '<b>' + str(x) + '</b>'}

        df = pd.DataFrame()
        formatters = {}
        show_index = False

        return df, formatters, show_index

    def get_context(self):

        data = {}

        if self.form_class:
            data['Form'] = self.form_class
        if self.form_helper:
            data['FormHelper'] = self.form_helper
        data['ButtonBack'] = self.show_button_back
        data['AllowExportXLS'] = self.allow_export_xls
        data['AllowExportScreen'] = self.allow_export_screen

        return {'form_data': data}

    def get(self, request, parent=None, *args, **kwargs):

        check_dashboard_permission(self.request, self.get_resource())

        if self.presave_message:
            messages.info(request, self.presave_message)

        if kwargs:
            self.form_class = self.get_form(request, initial=kwargs)

        return render(request, self.form_template_name, self.get_render_context())

    def get_form(self, request, initial=None, *args, **kwargs):

        self.form_class = self.form_class(request.POST or None, request.FILES or None, initial=initial)

        return self.form_class

    def post(self, request, *args, **kwargs):

        check_dashboard_permission(self.request, self.get_resource())

        form = self.get_form(request)

        if form.is_valid():

            self.data = form.cleaned_data

            report_data = self.process_data()

            if request.POST.get('submit-btn', None) == 'export':
                with BytesIO() as b:
                    # Use the StringIO object as the filehandle.
                    writer = pd.ExcelWriter(b, engine='xlsxwriter')
                    report_data[0].to_excel(writer, sheet_name=text.slugify(self.header[:30]))
                    writer.save()
                    writer.close()
                    b.seek(0)
                    response = HttpResponse(b,
                                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    filename = f'report-{text.slugify(self.header)}-{timezone.localtime(timezone.now()).strftime("%Y%m%d%H%M")}.xlsx'
                    response['Content-Disposition'] = 'attachment; filename=%s' % filename

                    return response

                # return to excel

            context = self.get_render_context()
            context.update({'list_data': context, 'report_data': report_data})

            return render(request, self.list_template_name, context)

        else:
            messages.warning(request, 'Please check the errors below.')

        return render(request, self.form_template_name, self.get_render_context())


class DashboardSmartReportView(DashboardBaseView):
    resource_type = 'smart_report'

    form_class = None

    show_button_back = True
    allow_export_xls = True
    allow_export_screen = True

    use_celery = False

    data = {}
    presave_message = ''

    form_helper = FormSetHelper

    form_template_name = 'switchblade_dashboard/form_report.html'
    list_template_name = 'switchblade_dashboard/smart_report.html'

    process_data_without_form = False
    process_data_with_custom_filter = False

    _charts = []
    _tables = []

    @staticmethod
    def _format_table_response(df, title, icon=None, formatters={}, show_index=False, custom_response=None,
                               show_on=('xls', 'screen')):
        r = {
            'df': df,
            'title': title,
            'icon': icon,
            'formatters': formatters,
            'show_index': show_index,
            'custom_response': custom_response,
            'show_on': show_on
        }
        return r

    def _save_table(self, df, title, icon=None, formatters={}, show_index=False, custom_response=None,
                    show_on=('xls', 'screen')):

        self._tables.append(
            self._format_table_response(df, title, icon, formatters, show_index, custom_response, show_on))

    @abstractmethod
    def process_data(self, filter=None):

        # self._save_table(pd.DataFrame(), title="Table 1", icon='fa-users')
        #
        # graph1_df = pd.DataFrame(pd.np.array([['Yes', 60], ['No', 40]]), columns=['labels', 'values'])
        # graph1_data = go.Pie(labels=graph1_df['labels'].values.tolist(), values=graph1_df['values'].values.tolist())
        # self._save_chart([graph1_data], title='Graph 1 Title', icon='fa-gears')

        return self._tables, self._charts

    @staticmethod
    # @shared_task
    def process_data_async(user_id, btn_export=False, form_data=None, filter=None):
        _tables = []
        _charts = []

        _basedf = pd.DataFrame()

        _tables.append(DashboardSmartReportView._format_table_response(_basedf, title="TITLE", icon='FA_ICON'))

        raw_io_file = False

        # if len(_basedf) > 3000:
        #     raw_io_file = True
        #     _tables = DashboardSmartReportView._generate_raw_io_file(_tables)

        results = {
            'user_id': user_id,
            'btn_export': btn_export,
            'raw_io_file': raw_io_file,
            'extra_context': {},
            '_tables': _tables,
            '_charts': _charts,
        }

        return results

    @staticmethod
    def _generate_raw_io_file(table_data):

        b = BytesIO()
        # Use the StringIO object as the filehandle.
        writer = pd.ExcelWriter(b, engine='xlsxwriter')
        for table in table_data:
            if 'xls' in table['show_on']:
                table['df'].to_excel(writer,
                                     sheet_name=text.slugify(table['title'][:30]),
                                     index=table['show_index']
                                     )

        writer.save()
        writer.close()
        b.seek(0)

        return b

    def _render_dashboard(self, request, table_data, chart_data, task_id=None, btn_export=False, raw_io_file=False):

        if task_id is not None:
            context = self.get_render_context()

            context.update({'is_running_celery': True, 'task_id': task_id})

            return render(request, self.list_template_name, context)

        if (btn_export and self.allow_export_xls) or raw_io_file:

            b = self._generate_raw_io_file(table_data) if not raw_io_file else table_data

            response = HttpResponse(
                b, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            filename = f'report-{text.slugify(self.header)}-' \
                       f'{timezone.localtime(timezone.now()).strftime("%Y%m%d%H%M")}.xlsx'

            response['Content-Disposition'] = 'attachment; filename=%s' % filename

            return response

        # return to excel
        elif self.allow_export_screen:

            context = self.get_render_context()
            table_data = [table for table in table_data if 'screen' in table['show_on']]

            context.update({'list_data': self.get_render_context(), 'table_data': table_data, 'chart_data': chart_data})

            return render(request, self.list_template_name, context)

        else:

            return HttpResponseForbidden()

    def get_context(self):

        data = {}

        if self.form_class:
            data['Form'] = self.form_class
        if self.form_helper:
            data['FormHelper'] = self.form_helper
        data['ButtonBack'] = self.show_button_back
        data['AllowExportXLS'] = self.allow_export_xls
        data['AllowExportScreen'] = self.allow_export_screen

        return {'form_data': data}

    def get(self, request, parent=None, *args, **kwargs):

        check_dashboard_permission(self.request, self.get_resource())

        task_id = request.GET.get('task_id', None)

        if task_id is not None and self.use_celery and settings.USE_CELERY:

            try:
                task_result = AsyncResult(task_id)

                if task_result.ready() and task_result.successful():

                    result = task_result.result

                    user_id = result.get('user_id', request.user.id)
                    btn_export = result.get('btn_export', False)
                    raw_io_file = result.get('raw_io_file', False)
                    table_data = result.get('_tables', [])
                    chart_data = result.get('_charts', [])
                    extra_context = result.get('extra_context', {})

                    if extra_context:
                        self.extra_context = extra_context

                    # clear results
                    task_result.forget()

                    if user_id != request.user.id:
                        return HttpResponseForbidden()

                    return self._render_dashboard(request, table_data, chart_data, btn_export=btn_export,
                                                  raw_io_file=raw_io_file)
                else:
                    return self._render_dashboard(request, None, None, task_id=task_id)

            except:
                return self._render_dashboard(request, None, None, task_id=task_id)

        if self.process_data_without_form:

            if self.use_celery and settings.USE_CELERY:
                table_data, chart_data = None, None
                task_id = self.process_data_async.apply_async(queue='reports',
                                                              kwargs={'user_id': request.user.id}).task_id

            else:
                table_data, chart_data = self.process_data()
                task_id = None

            return self._render_dashboard(request, table_data, chart_data, task_id=task_id)

        if self.presave_message:
            messages.info(request, self.presave_message)

        if kwargs:
            self.form_class = self.get_form(request, initial=kwargs)

        return render(request, self.form_template_name, self.get_render_context())

    def get_form(self, request, initial=None, *args, **kwargs):

        self.form_class = self.form_class(request.POST or None, request.FILES or None, initial=initial)

        return self.form_class

    def post(self, request, *args, **kwargs):

        check_dashboard_permission(self.request, self.get_resource())

        filter = request.POST.get('filter', None)
        filter_export = request.POST.get('filter_export', False)
        btn_export = request.POST.get('submit-btn', None) == 'export'

        if self.process_data_with_custom_filter and filter:

            if self.use_celery and settings.USE_CELERY:
                table_data, chart_data = None, None
                task_id = self.process_data_async.apply_async(queue='reports', kwargs={'user_id': request.user.id,
                                                                                       'btn_export': btn_export,
                                                                                       'filter': filter}).task_id

            else:
                table_data, chart_data = self.process_data(filter)
                task_id = None

            return self._render_dashboard(request, table_data, chart_data, task_id=task_id, btn_export=btn_export)

        form = self.get_form(request)

        if form.is_valid():

            if self.use_celery and settings.USE_CELERY:
                # data = form.cleaned_data
                table_data, chart_data = None, None
                task_id = self.process_data_async.apply_async(queue='reports', kwargs={'user_id': request.user.id,
                                                                                       'btn_export': btn_export,
                                                                                       'form_data': form.cleaned_data}).task_id

            else:
                self.data = form.cleaned_data
                table_data, chart_data = self.process_data()
                task_id = None

            return self._render_dashboard(request, table_data, chart_data, task_id=task_id, btn_export=btn_export)

        else:
            messages.warning(request, 'Please check the errors below.')

        return render(request, self.form_template_name, self.get_render_context())


class DashboardSmartMapView(DashboardBaseView):

    page_title = 'Sites Map'

    dashboard_template = 'switchblade_dashboard/map.html'

    action = None

    use_themes = False
    default_theme = None
    themes = {}

    legend = {}
    cluster_legend = {}
    filter_form_class = None

    bounds = {}

    use_polygons = False
    use_marker_cluster = False
    use_svg_marker = False
    svg_template = 'switchblade_dashboard/map_svg_icon.html'

    def _get_theme(self, theme=None):
        return self.themes.get(theme, {})

    def _get_legend(self, theme={}):

        if self.use_themes:
            return theme.get('legend', self.legend)

        return self.legend

    def _get_cluster_legend(self, theme={}):

        if self.use_themes:
            return theme.get('cluster_legend', self.cluster_legend)

        return self.cluster_legend

    def _get_polygons(self, theme={}):

        if self.use_themes:
            return theme.get('use_polygons', self.use_polygons)

        return self.use_polygons

    def _get_marker_cluster(self, theme={}):

        if self.use_themes:
            return theme.get('use_marker_cluster', self.use_marker_cluster)

        return self.use_marker_cluster

    def _get_svg_marker(self, theme={}):

        if self.use_themes:
            return theme.get('use_svg_marker', self.use_svg_marker)

        return self.use_svg_marker

    def _get_filter_form(self, theme={}):

        form_class = self.filter_form_class

        if self.use_themes:
            form_class = theme.get('filter_form_class', None)

        if form_class is not None:

            form = form_class()

            return {
                'form': render_crispy_form(form),
                'form_fields': [key for key in form.fields.keys()]
            }

        return None

    def _format_points(self, data):
        df = data.get('data', pd.DataFrame())
        point_columns = data.get('point_columns', [])
        coordinates_columns = data.get('coordinates_columns', [])
        marker = data.get('marker', {})
        cluster = data.get('cluster', {})

        points = []

        if df.empty:
            return points

        if not point_columns or not coordinates_columns:
            return points

        for index, row in df.iterrows():
            point = (
                row[coordinates_columns].values.tolist(),
                row[point_columns].to_dict(),
            )

            marker_data = {
                'color': '#000',
                'text': ''
            }

            cluster_data = 1

            if marker:
                color_column = marker.get('color_column', None)
                text_column = marker.get('text_column', None)

                marker_data = {
                    'color': row[color_column] if color_column else '#000',
                    'text': row[text_column] if text_column else ''
                }

            point = point + (marker_data,)

            if cluster:
                cluster_level_column = cluster.get('level_column', None)
                cluster_data = cluster_level_column if cluster_level_column is not None else 1

            point = point + (cluster_data,)

            points.append(point)

        return points

    def _format_points_to_remove(self, data):
        points_to_remove = data.get('points_to_remove', [])
        return points_to_remove

    def _format_polygons(self, data):
        df = data.get('data', pd.DataFrame())
        polygon_columns = data.get('polygon_columns', [])
        coordinates_column = data.get('coordinates_column', None)
        style = data.get('style', {})

        polygons = []

        if df.empty:
            return polygons

        if not polygon_columns or not coordinates_column:
            return polygons

        for index, row in df.iterrows():
            polygon_center = list(MultiPoint(row[coordinates_column]).buffer(0.05).centroid)
            polygon_data = {**row[polygon_columns].to_dict(), **{'center': polygon_center}}
            polygon_style = {'color': '#000', 'inner_color': '#000'}

            if style:
                color_column = style.get('color_column', None)
                inner_color_column = style.get('inner_color_column', None)

                if color_column:
                    if not inner_color_column:
                        polygon_style = {
                            'color': row[color_column],
                            'inner_color': row[color_column]
                        }
                    else:
                        polygon_style = {
                            'color': row[color_column],
                            'inner_color': row[inner_color_column]
                        }

            polygon_data = {**polygon_data, **polygon_style}

            polygons.append((
                row[coordinates_column],
                polygon_data
            ))

        return polygons

    def _format_polygons_to_remove(self, data):
        polygons_to_remove = data.get('polygons_to_remove', [])
        return polygons_to_remove

    def _format_points_to_geojson(self, list_data, theme=None):

        results = []
        theme = self._get_theme(theme)

        for data in list_data:

            geo_json = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': data[0]
                }
            }

            result_json = data[1]

            if self.use_themes:

                theme_use_svg_marker = theme.get('use_svg_marker', None)
                theme_use_marker_cluster = theme.get('use_marker_cluster', None)

                if self.use_svg_marker or theme_use_svg_marker:
                    result_json = dict(result_json, **{'icon': self._get_svg_icon(data[2], theme)})

                if self.use_marker_cluster or theme_use_marker_cluster:
                    result_json = dict(result_json, **{'cluster_level': data[3]})

            geo_json['properties'] = result_json

            results.append(geo_json)

        return results

    def _format_polygons_to_geojson(self, list_data):

        results = []

        for data in list_data:
            results.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [MultiPoint(data[0]).buffer(0.05).convex_hull.tuple[0]]
                },
                'properties': data[1]
            })

        return results

    def _get_svg_icon(self, data={}, theme={}):

        if self.use_themes:
            svg_template = theme.get('svg_template', self.svg_template)
        else:
            svg_template = self.svg_template

        return render_to_string(svg_template, context=data)

    def api_config(self, request):

        theme = request.GET.get('theme', self.default_theme)
        theme = self._get_theme(theme)

        data = {
            'legend': self._get_legend(theme),
            'cluster_legend': self._get_cluster_legend(theme),
            'use_polygons': self._get_polygons(theme),
            'use_marker_cluster': self._get_marker_cluster(theme),
            'use_svg_marker': self._get_svg_marker(theme),
            'filter': self._get_filter_form(theme)
        }

        return JsonResponse(data)

    def api_themes(self, request):

        default_theme = self.default_theme if self.use_themes else None
        themes = {k: {'verbose_name': v['verbose_name']} for k, v in self.themes.items()} if self.use_themes else {}

        return JsonResponse({'default_theme': default_theme, 'themes': themes})

    # @silk_profile(name='Map')
    def api_points(self, request):
        body = json.loads(request.body)
        theme = body.get('theme', None)
        filter = body.get('filter', None)
        self.bounds = body.get('bounds', None)

        if self.use_themes and theme is None:
            theme = self.default_theme

        if not self.bounds:
            return JsonResponse({'message': 'Please inform the bounds!'}, status=400)

        if 'minX' not in self.bounds or 'minY' not in self.bounds or 'maxX' not in self.bounds or 'maxY' not in self.bounds:
            return JsonResponse({'message': 'Please inform all bounds coordinates to proceed!'}, status=400)

        try:
            bbox = (self.bounds['minX'], self.bounds['minY'], self.bounds['maxX'], self.bounds['maxY'])
            geometry = Polygon.from_bbox(bbox)

            try:
                points_data_method = getattr(self.__class__, 'get_points_data')
                points_data = points_data_method(geometry, theme, filter)
            except AttributeError:
                points_data = {}

            try:
                polygons_data_method = getattr(self.__class__, 'get_polygons_data')
                polygons_data = polygons_data_method(geometry, theme, filter)
            except AttributeError:
                polygons_data = {}

            points = self._format_points(points_data) if points_data else []
            points_to_remove = self._format_points_to_remove(points_data) if points_data else []
            polygons = self._format_polygons(polygons_data) if polygons_data else []
            polygons_to_remove = self._format_polygons_to_remove(polygons_data) if polygons_data else []

            points_geojson = self._format_points_to_geojson(points, theme)
            polygons_geojson = self._format_polygons_to_geojson(polygons)

        except Exception as e:
            return JsonResponse({'message': 'Error while trying to get the Points/Polygons: {}'.format(str(e))}, status=500)

        return JsonResponse({
            'points': points_geojson,
            'points_to_remove': points_to_remove,
            'polygons': polygons_geojson,
            'polygons_to_remove': polygons_to_remove
        })

    def api_click(self, request):
        body = json.loads(request.body)
        point_id = body.get('id', None)
        point_coordinates = body.get('coordinates', None)
        theme = body.get('theme', self.default_theme)

        if not point_id and not point_coordinates:
            return JsonResponse({'message': _('Please, inform the Point ID or Coordinates do proceed!')}, status=400)

        try:
            try:
                point_info_method = getattr(self.__class__, f'get_point_info')
            except AttributeError:
                raise Exception(_(f'The method "get_point_info" must be implemented!'))

            title, info = point_info_method(point_id, point_coordinates, theme)

        except ValueError as e:
            return JsonResponse(
                {'message': _('Error while trying to get the Point Information') + ': {}'.format(str(e))}, status=404
            )
        except Exception as e:
            return JsonResponse(
                {'message': _('Error while trying to get the Point Information') + ': {}'.format(str(e))}, status=500
            )

        return JsonResponse({'title': title, 'info': info})

    def api_search(self, request):

        q = request.GET.get('q', None)
        theme = request.GET.get('theme', self.default_theme)

        if not q:
            return JsonResponse({'message': _('Please, inform the Query to proceed!')}, status=400)

        try:
            try:
                search_points_method = getattr(self.__class__, f'search_points')
            except AttributeError:
                raise Exception(_(f'The method "search_points" must be implemented!'))

            points = search_points_method(q, theme)

            for point in points:
                if 'loc' not in point:
                    continue

                point['loc'].reverse()

        except Exception as e:
            return JsonResponse(
                {'message': _('Error while trying to get the Physical Sites') + '{}'.format(str(e))}, status=500
            )

        return JsonResponse({'points': points})

    def _render_map(self, request):

        theme = request.GET.get('theme', None)

        if theme:
            self.default_theme = theme

        context = self.get_render_context()

        context['default_theme'] = self.default_theme

        return render(request, self.dashboard_template, context)

    def get(self, request, *args, **kwargs):

        if self.action == 'config':
            return self.api_config(request)
        elif self.action == 'themes':
            return self.api_themes(request)
        elif self.action == 'search':
            return self.api_search(request)
        elif self.action is None:
            return self._render_map(request)

        return HttpResponseForbidden()

    def post(self, request, *args, **kwargs):

        if self.action == 'points':
            return self.api_points(request)
        elif self.action == 'click':
            return self.api_click(request)

        return HttpResponseForbidden()


class PermissionView(View):
    resource = None
    header = ''

    resource_type = None

    def dispatch(self, request, *args, **kwargs):
        check_dashboard_permission(request, self.get_resource())

        return super().dispatch(request, *args, **kwargs)

    @classmethod
    def get_resource(cls, type_name=None):
        return cls.resource


class AuditLogList(DashboardListView):
    page_title = 'Audit log'
    header = 'Audit log list'

    # add_button_title = 'New audit lgo'
    # add_button_url = reverse_lazy('audit-log-create')

    table_class = AuditLogTable
    filter_class = AuditLogFilter
    object = AuditLog

    def get_queryset(self):
        qs = AuditLog.objects.filter()
        return qs


class DashboardSmartDashView(DashboardBaseView):

    # Dashboard
    theme_path = None
    charts_theme_path = ''
    charts_theme_name = ''

    # Page
    template_name = 'switchblade_dashboard/dashboard.html'
    logo = 'img/logo-white.png'
    page_title = ''
    header = ''
    pages = []

    # Filter
    filter = None
    filter_helper = DashboardFilterHelper

    # Nav Extra Commands
    nav_extra_commands = None
    nav_extra_commands_helper = DashboardExtraCommandsHelper

    action = None

    def _get_filter(self):
        return self.filter, self.filter_helper

    def _get_page_filter(self, page):
        page_filter = page.get('filter', None)
        page_filter_helper = page.get('filter_helper', None)

        if page_filter is None:
            return self._get_filter()
        else:
            if page_filter_helper:
                return page_filter, self.filter_helper
            else:
                return page_filter, page_filter_helper

    def _get_nav_extra_commands(self):
        return self.nav_extra_commands, self.nav_extra_commands_helper

    def _get_page_nav_extra_commands(self, page):
        page_nav_extra_commands = page.get('nav_extra_commands', None)
        page_nav_extra_commands_helper = page.get('nav_extra_commands_helper', None)

        if page_nav_extra_commands is None:
            return self._get_nav_extra_commands()
        else:
            if page_nav_extra_commands_helper:
                return page_nav_extra_commands, self.nav_extra_commands_helper
            else:
                return page_nav_extra_commands, page_nav_extra_commands_helper

    def _get_page_rows(self, page):
        page_rows = page.get('rows', [])
        page_export_option = page.get('export_option', True)
        rows = []

        for row_index, row in enumerate(page_rows):
            columns = []
            row_height = row.get('height', '30%')
            row_columns = row.get('columns', [])

            if 'vh' in row_height:
                row_height = f'calc({row_height} - 4vh)'

            for column_index, column in enumerate(row_columns):
                column_components = column.get('components', [])
                width = column.get('width', 12)
                components = []

                for component_index, component in enumerate(column_components):
                    component_id = component.get('id', None)
                    component_title = component.get('title', '')
                    component_class = component.get('component_class', None)
                    component_export_option = component.get('export_option', True)
                    component_height = component.get('height', '50vh')  # In vh. Default: 50vh
                    component_extra_options = component.get('extra_options', {})

                    if 'vh' in component_height:
                        component_height = f'calc({component_height} - 4vh)'

                    if component_id is None or component_class is None:
                        continue

                    if component_class.component_type == COMPONENT_CHART_TYPE:
                        component_show_legend = component.get('show_legend', True)
                        component_charts_theme_name = self._get_charts_theme_name()

                        component_instance = component_class(
                            chart_id=component_id,
                            title=component_title,
                            show_legend=component_show_legend,
                            extra_options=component_extra_options,
                            charts_theme_name=component_charts_theme_name
                        )
                    elif component_class.component_type == COMPONENT_TABLE_TYPE:
                        component_entries = component.get('entries', 25)

                        if component_title:

                            component_extra_options['title'] = {}
                            title_extra_options = component_extra_options.get('title', None)

                            if not component_extra_options or not title_extra_options:
                                font_size = '24px'
                                font_weight = 700
                                color = '#C2C3CD'
                                font_family = 'Source Sans Pro, Helvetica Neue, Helvetica, Arial, sans-serif'
                                padding_top = '6px'
                                margin_bottom = '0px'

                            else:
                                font_size = title_extra_options.get('fontSize', '24px')
                                font_weight = title_extra_options.get('fontWeight', 700)
                                color = title_extra_options.get('color', '#C2C3CD')
                                font_family = title_extra_options.get('fontFamily', 'Source Sans Pro, Helvetica Neue, '
                                                                                    'Helvetica, Arial, sans-serif')
                                padding_top = title_extra_options.get('paddingTop', '6px')
                                margin_bottom = title_extra_options.get('marginBottom', '0px')

                            component_extra_options['title']['fontSize'] = font_size
                            component_extra_options['title']['fontWeight'] = font_weight
                            component_extra_options['title']['color'] = color
                            component_extra_options['title']['fontFamily'] = font_family
                            component_extra_options['title']['paddingTop'] = padding_top
                            component_extra_options['title']['marginBottom'] = margin_bottom

                        component_instance = component_class(
                            table_id=component_id,
                            title=component_title,
                            entries=component_entries,
                            extra_options=component_extra_options
                        )
                    elif component_class.component_type == COMPONENT_CARD_TYPE:

                        component_export_option = component_class.export

                        component_instance = component_class(
                            card_id=component_id,
                            title=component_title,
                            extra_options=component_extra_options
                        )
                    elif component_class.component_type == COMPONENT_CUSTOM_HTML_TYPE:
                        component_instance = component_class(
                            component_id=component_id,
                            title=component_title,
                        )
                    else:
                        continue

                    components.append({
                        'id': component_id,
                        'index': component_index,
                        'instance': component_instance,
                        'type': dict(COMPONENT_TYPES).get(component_class.component_type),
                        'export_option': True if page_export_option and component_export_option else False,
                        'height': component_height,
                    })

                columns.append({
                    'index': column_index,
                    'width': width,
                    'components': components
                })

            rows.append({
                'index': row_index,
                'height': row_height,
                'columns': columns
            })

        return rows

    def _get_pages(self):
        pages = []

        for index, page in enumerate(self.pages):

            if not page:
                pass

            page_filter, filter_helper = self._get_page_filter(page)
            page_nav_extra_commands, page_nav_extra_commands_helper = self._get_page_nav_extra_commands(page)
            rows = self._get_page_rows(page)

            pages.append({
                'index': index,
                'title': page.get('title', ''),
                'filter': page_filter(prefix=f'filter_{str(index)}') if page_filter is not None else None,
                'filter_helper': filter_helper,
                'nav_extra_commands': page_nav_extra_commands(
                    prefix=f'nav_extra_commands_{str(index)}') if page_nav_extra_commands is not None else None,
                'nav_extra_commands_helper': page_nav_extra_commands_helper,
                'print': page.get('print', False),
                'sync_zoom': page.get('sync_zoom', False),
                'rows': rows
            })

        return pages

    def _get_logo(self):
        return self.logo

    def _get_default_theme_path(self):
        return 'switchblade_dashboard/css/dashboard/dashboard-default-theme.css'

    def _get_theme_path(self):
        theme = '' if self.theme_path is None else self.theme_path
        return theme

    def _get_charts_theme_path(self):
        return self.charts_theme_path

    def _get_charts_theme_name(self):
        return self.charts_theme_name

    def _get_component(self, pages, position):

        component = None
        page = None
        component_row = None
        component_column = None

        try:
            page = pages[position['page']]
        except IndexError:
            raise IndexError('Invalid page index!')

        try:
            component_row = page['rows'][position['row']]
        except IndexError:
            raise IndexError('Invalid row index!')

        try:
            component_column = component_row['columns'][position['column']]
        except IndexError:
            raise IndexError('Invalid column index!')

        try:
            component = component_column['components'][position['component_index']]
        except IndexError:
            raise IndexError('Invalid component index!')

        return component

    def process_data(self, component_id, request, filters, **kwargs):

        try:
            data_method = getattr(self.__class__, f'data_{component_id}')
        except AttributeError:
            raise Exception(_(f'The method data_{component_id} must be implemented!'))

        try:
            extra_options_method = getattr(self.__class__, f'extra_options_{component_id}')
        except AttributeError:
            extra_options_method = None

        data = data_method(request, filters, **kwargs)

        extra_options = extra_options_method(request, data, filters) if extra_options_method else {}

        return {'data': data, 'extra_options': extra_options}

    def get_context(self):
        data = self._get_base_context()
        data['Logo'] = self._get_logo()
        data['Pages'] = self._get_pages()
        data['Default_Theme_Path'] = static(self._get_default_theme_path())
        data['Theme_Path'] = static(self._get_theme_path())
        data['Charts_Theme_Path'] = static(self._get_charts_theme_path()) if self._get_charts_theme_path() else None

        return data

    def api_data(self, request):
        body = json.loads(request.body)
        req_component_id = body.get('id', None)
        page = body.get('page', None)
        position = body.get('position', None)
        extra_params = body.get('extra_params', None)
        filters = body.get('filters', {})
        pagination_index = body.get('pagination_index', 1)

        if req_component_id is None or page is None or position is None:
            return JsonResponse({'message': _('Please, inform the Component ID and Page Index to proceed!')},
                                status=400)

        try:
            processed_data = self.process_data(req_component_id, request, filters, extra_params=extra_params,
                                               pagination_index=pagination_index)

            data = processed_data.get('data', {})
            extra_options = processed_data.get('extra_options', {})

            if not data:
                return JsonResponse({'message': _(f'Unprocessed component {req_component_id}!')}, status=400)

            component_data = {}

            pages = self.pages

            try:
                component = self._get_component(pages, position)
                component_id = component.get('id', None)
                component_class = component.get('component_class', None)

                if component and component_id is not None and component_class is not None:
                    if component_class.component_type == COMPONENT_CHART_TYPE:
                        component_legend = component.get('legend', {})
                        component_data_legend = data.get('legend', {})

                        if not component_legend and not component_data_legend:
                            legend = {}
                        else:
                            legend = component_data_legend if component_data_legend else component_legend

                        component_data['data'] = component_class.get_data(data, legend)

                        if component_class.custom_actions:
                            component_data['custom_actions_data'] = component_class.get_custom_actions_data(data)

                    else:
                        component_data = component_class.get_data(data)

                    component_extra_options = component.get('extra_options', {})
                    component_data['extra_options'] = extra_options if extra_options else component_extra_options

            except IndexError:
                raise IndexError('Invalid position indexes!')

        except IndexError as e:
            return JsonResponse({'message': f'"{str(e)}"'}, status=400)

        except Exception as e:
            return JsonResponse({'message': _('Error while trying to get the Component Data') + f': "{str(e)}"'},
                                status=500)

        return JsonResponse(component_data)

    def api_detail(self, request):
        body = json.loads(request.body)
        req_component_id = body.get('id', None)
        position = body.get('position', None)
        click_event_obj = body.get('click_event_obj', {})
        filters = body.get('filters', {})

        if req_component_id is None or position is None:
            return JsonResponse({'message': 'Please, inform the Component ID and Page Index and Series Index to proceed!'}, status=400)

        pages = self.pages

        try:
            component = self._get_component(pages, position)
            component_id = component.get('id', None)

            if component_id is not None and component_id == req_component_id:

                try:
                    detail_method = getattr(self.__class__, f'detail_{req_component_id}')
                    content = detail_method(request, filters, click_event_obj=click_event_obj)
                except IndexError:
                    raise Http404('The series has not a detail method')
                except AttributeError:
                    raise Http404(f'The method "detail_{req_component_id}" must be implemented!')

        except IndexError:
            raise IndexError('Invalid position indexes!')

        return JsonResponse({'content': content})

    def api_export(self, request):
        body = json.loads(request.body)
        req_component_id = body.get('id', None)
        page = body.get('page', None)
        position = body.get('position', None)
        filters = body.get('filters', {})

        if req_component_id is None or page is None:
            return JsonResponse({'message': _('Please, inform the Component ID and Page Index to proceed!')},
                                status=400)

        pages = self.pages

        try:
            component = self._get_component(pages, position)
            component_id = component.get('id', None)

            if component_id is not None and component_id == req_component_id:

                component_title = component.get('title', '')

                try:
                    data_method = getattr(self.__class__, f'export_{req_component_id}')
                except AttributeError:
                    raise Exception(_(f'The method export_{req_component_id} must be implemented!'))

                data = data_method(request, filters)

                with BytesIO() as b:
                    writer = pd.ExcelWriter(b, engine='xlsxwriter')
                    data.to_excel(writer, sheet_name=component_title)
                    writer.save()
                    writer.close()
                    b.seek(0)
                    response = HttpResponse(b,
                                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    filename = f'export-{req_component_id}-{timezone.localtime(timezone.now()).strftime("%Y%m%d%H%M")}.xlsx'
                    response['Content-Disposition'] = filename

                    return response
        except IndexError:
            raise IndexError('Invalid position indexes!')

    def _render(self, request):
        context = self.get_render_context()
        return render(request, self.template_name, context)

    def get(self, request):
        return self._render(request)

    def post(self, request):
        if self.action == 'data':
            return self.api_data(request)
        if self.action == 'detail':
            return self.api_detail(request)
        if self.action == 'export':
            return self.api_export(request)

        return HttpResponseForbidden()
