from menu import Menu, MenuItem

from proj.config_menus import MENUS


class MenuItemResource(MenuItem):
    """Custom MenuItem that checks permissions based on allowed menu resources"""

    resource = None

    def __init__(self, menu_obj, menu_slug, resource, menu_children=()):

        params = {
            'title': menu_obj.title,
            'url': menu_obj.url,
            'resource': resource,
            'weight': menu_obj.order,
            'icon': menu_obj.icon,
            'list': menu_obj.visible,
            'iframe': menu_obj.iframe,
            'area': menu_slug,
            'has_help': menu_obj.has_help,
        }

        if menu_children:
            params['children'] = menu_children

        if menu_obj.extra_info:
            params.update(menu_obj.extra_info)

        super().__init__(**params)

    def check(self, request):

        is_visible = True
        user_roles = request.user.get_allowed_resources

        allowed_menus = [user_role for user_role in user_roles if "menu." in user_role]

        # if self.resource not in allowed_menus:
        if self.resource not in allowed_menus and not request.user.is_admin:
            is_visible = False

        self.visible = is_visible


for menu in MENUS:

    if len(menu.slug.split('.')) > 1 and menu.slug.split('.')[1] != '*':

        menu_resource = f'menu.{menu.slug}'

        slug = menu.slug.split('.')
        if len(slug) == 2:
            Menu.add_item("sidebar", MenuItemResource(menu, slug[0], menu_resource))
        elif len(slug) == 3 and slug[2] == '*':
            group_slug = f'{slug[0]}.{slug[1]}.'
            children_selected = [
                child for child in MENUS if group_slug in child.slug and f'{group_slug}*' not in child.slug
            ]
            children = []
            for child in children_selected:
                child_resource = f'menu.{child.slug}'
                children.append(MenuItemResource(child, menu.slug.split('.')[0], child_resource))
            Menu.add_item("sidebar", MenuItemResource(menu, slug[0], menu_resource, children))

    # menu areas
    if len(menu.slug.split('.')) == 2 and menu.slug.split('.')[1] == '*':
        menu_resource = f'menu.{menu.slug}'
        slug = menu.slug.split('.')
        Menu.add_item("main", MenuItemResource(menu, slug[0], menu_resource))
