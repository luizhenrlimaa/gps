import pandas as pd
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.inclusion_tag('switchblade_dashboard/tags/crud_table.html')
def crud_table(data):

    return {'data': data}


@register.inclusion_tag('switchblade_dashboard/tags/crud_table_report.html')
def report_simple_table(data, report_data):

    formatters = report_data[1]
    pd.set_option('display.max_colwidth', -1)
    table = report_data[0].to_html(na_rep='-',
                                   classes=['table', 'table-bordered', 'table-striped', 'dataTable'],
                                   index=report_data[2],
                                   formatters=formatters,
                                   escape=False)

    return {'data': data, 'table': table}


@register.inclusion_tag('switchblade_dashboard/tags/crud_smart_report.html')
def report_smart(data, table_data, chart_data):

    pd.set_option('display.max_colwidth', None)

    _tables = []
    _charts = []

    for table in table_data:

        if table['custom_response'] is None:

            html_table = table['df'].to_html(na_rep='-',
                                             classes=['table', 'table-bordered', 'table-striped', 'dataTable'],
                                             index=table['show_index'],
                                             formatters=table['formatters'],
                                             escape=False)
        else:
            html_table = table['custom_response']

        _tables.append({
            'title': table['title'],
            'icon': table['icon'],
            'table': html_table,
        })

    return {'data': data, 'tables': _tables, 'charts': chart_data}


@register.inclusion_tag('switchblade_dashboard/tags/crud_form.html')
def crud_form(data):
    return {'data': data}


@register.inclusion_tag('switchblade_dashboard/tags/crud_form_report.html')
def report_form(data):
    return {'data': data}


@register.inclusion_tag('switchblade_dashboard/tags/tabbed_header_box.html')
def tabbed_header_box(data, title, tab_title='Options', tab_icon='fa-circle-o', menu_info=None):
    return {'title': title, 'data': data, 'tab_title': tab_title, 'tab_icon': tab_icon, 'menu_info': menu_info}


@register.inclusion_tag('switchblade_dashboard/tags/crud_form_export_template.html')
def export_template_form(data):
    return {'data': data}


@register.inclusion_tag('switchblade_dashboard/tags/crud_detail.html')
def crud_detail(data):
    return {'data': data}


@register.inclusion_tag('switchblade_dashboard/tags/render_field.html')
def crud_render_field(field):
    return {'field': field}

@register.inclusion_tag('switchblade_dashboard/tags/dashboard_grid.html')
def dashboard_grid(page):
    return {'page': page}

@register.filter
def get_attribute(obj, attribute):

    try:

        if hasattr(obj, f'get_{attribute}_display'):
            return getattr(obj, f'get_{attribute}_display')()

        attr =  obj.__getattribute__(attribute)

        if attr.__class__.__name__ == 'ManyRelatedManager':
            return ', '.join([value.__str__() for value in attr.all()])

        if attr.__class__.__name__ == 'ImageFieldFile':
            return mark_safe(f'<img class="img-responsive" src="{attr.url}"></img>')

        if isinstance(attr, bool) and attr:
            return mark_safe('<i class="fa fa-check-circle text-green"></i>')

        if isinstance(attr, bool) and not attr:
            return mark_safe('<i class="fa fa-times-circle text-red"></i>')

        if isinstance(attr, dict):
            return mark_safe(f'<pre><code>{attr}</code></pre>')

        if attr is None or attr == '':
            return '-'

        return attr
    except:
        return attribute


@register.filter
def get_field(obj, field_name):

    return obj[field_name]


@register.filter
def in_links(url, areas):

    area_page = url.split('-')[1]

    areas = areas.split(',')

    if area_page in areas:
        return True

    return False


@register.filter
def in_area(url, area):

    if url.split('-')[0] == area:
        return True

    return False


@register.filter
def get_item(dictionary, key):

    if isinstance(dictionary, dict):

        return dictionary.get(key)

    return None


@register.filter()
def has_resource_permission(user, resource):

    user_roles = user.get_allowed_resources

    if resource not in user_roles and not user.is_admin:
        return False

    return True
