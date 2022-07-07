from dal import autocomplete
from django.db.models import Q, Value
from django.db.models.functions import Concat
from .models import User, UserResource, Role


class UserAutocomplete(autocomplete.Select2QuerySetView):
    # def get_selected_result_label(self, item):
    #     url_avatar = item.get_avatar_url()
    #     return format_html('<img src="' + url_avatar + '" class="img-circle" style="width:20px; height:20px"> {}',
    #                        item.first_name)
    #
    # def get_result_label(self, item):
    #     url_avatar = item.get_avatar_url()
    #     return format_html('<div class="row">'
    #                        '<div class="col-sm-2" style="display:absolute; margin-right:auto; margin-left:auto;">'
    #                        '<img class="img-circle" src="' + url_avatar + '" style="width:27px; height:27px;">'
    #                        '</div>'
    #                        '<div class="col-sm-10">'
    #                        '{} {} </br>'
    #                        '{}'
    #                        '</div>'
    #                        '</div>', item.first_name, item.last_name, item.email)

    def get_queryset(self):

        qs = User.objects.filter()

        if self.q:
            qs = qs.annotate(full_name=Concat('first_name', Value(' '), 'last_name')).filter(full_name__unaccent__icontains=self.q)

        return qs.distinct()


class UserResourceAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):

        qs = UserResource.objects.filter()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class RoleAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):

        qs = Role.objects.filter()

        if self.q:
            qs = qs.filter(description__icontains=self.q)
        return qs


