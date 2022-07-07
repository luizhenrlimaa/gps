
class Resource:
    def __init__(self):
        self._resources = []

    def register(self, resource, description, order=0, recursive=True):
        if resource not in self._resources:
            self._resources.append((resource, (description,  order)))
            if recursive:
                splitted_resource = resource.split('.')
                parent_resources = ['.'.join(splitted_resource[0:i]) + '.*' for i in range(1, len(splitted_resource))]
                for parent_resource in parent_resources:
                    self.register(parent_resource, parent_resource, recursive=False)

    def register_extra_resources(self, resources):

        for resource_item in resources:
            resource_name, resource_detail = resource_item
            description, order = resource_detail
            self.register(resource_name, description, order)

    def register_menus(self):

        from proj.config_menus import MENUS
        listed_menus = [(f'menu.{menu.slug}', menu.title, menu.order) for menu in MENUS]
        for menu in listed_menus:
            self.register(menu[0], menu[1], menu[2], recursive=False)

    def get_resources_as_tuple(self):
        return self._resources


baseResource = Resource()


