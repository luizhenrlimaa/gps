import json

from django.contrib import messages
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.exceptions import PermissionDenied
from django.db.models import Value
from django.db.models.functions import Concat
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.timesince import timesince
from django.views.generic.base import View
from django.utils.translation import gettext as _

from switchblade_dashboard.forms import StackedFormSetHelper, FormSetHelper
from switchblade_dashboard.views import DashboardListView, DashboardDetailView, DashboardCreateView, \
    DashboardUpdateView, \
    DashboardDeleteView, DashboardBaseView
from .filters import UserFilter
from .forms import UserCreationForm, UserChangeForm, RoleForm, UserPasswordForm, UserTemplateForm, UserProfileForm
from .models import User, Role, UserResource
from .tables import UserTable, RoleTable


class UserNotification(View):

    def get(self, request):
        notifications = request.user.notifications.select_related('actor_content_type').unread()

        notification_list = []

        for notification in notifications:

            notification_item = {}

            notification_item['slug'] = notification.slug
            notification_item['verb'] = notification.verb
            notification_item['description'] = notification.description
            if notification.data:
                notification_item['url'] = notification.data.get('url', None)
            else:
                notification_item['url'] = '#'
            notification_item['timestamp'] = timesince(notification.timestamp)

            if notification.actor == request.user:
                notification_item['actor'] = 'System'
                notification_item['actor_avatar'] = static('dist/img/huawei.png')
            else:
                notification_item['actor'] = notification.actor.get_short_name()
                notification_item['actor_avatar'] = notification.actor.get_avatar_url()

            notification_list.append(notification_item)
        return JsonResponse({'results': notification_list})


class UserProfileChangeView(DashboardBaseView):

    page_title = _('Personal Info')

    def post(self, request):

        form = UserProfileForm(request.POST or None, request.FILES or None, instance=request.user)

        if form.is_valid():
            form.save()

            return redirect("dashboard-index")
        else:
            messages.warning(request, 'Unable to update user profile')
        return render(request, 'users/user_profile_change.html',
                      {'form': form, 'avatar_url': request.user.get_avatar_url()})

    def get(self, request):
        user = request.user
        form = UserProfileForm(instance=user)
        avatar_url = user.get_avatar_url()

        context = self.get_render_context()
        context.update({
            'form': form,
            'avatar_url': avatar_url
        })

        return render(request, 'users/user_profile_change.html', context)


class UserUpdateAvatarView(DashboardBaseView):

    page_title = _('Update Avatar')

    def get(self, request):
        user = request.user
        avatar_url = user.get_avatar_url()
        context = self.get_render_context()

        context.update({
            'avatar_url': avatar_url
        })

        return render(request, 'users/update_avatar.html', context)


class UserListView(DashboardListView):
    page_title = _('Users')
    header = _('Users')

    add_button_title = _('New User')
    add_button_url = reverse_lazy('users-create')

    table_class = UserTable
    filter_class = UserFilter

    object = User

    allow_export_import = True
    allow_insert_by_template = False
    allow_delete_by_template = False
    form_template_class = UserTemplateForm

    actions = {
        'change_password': {
            'text': 'Change password',
            'function': 'change_password',
            'return_type': True
        }
    }

    def get_queryset(self):
        return User.objects.filter()


class UserDetailView(DashboardDetailView):
    object = User

    page_title = _('User Detail')
    header = _('User detail')

    rows_based_on_form = UserChangeForm

    def get_queryset(self):
        return User.objects.filter()


class UserCreateView(DashboardCreateView):
    page_title = _('User')
    header = _('New user')

    form_class = UserCreationForm
    owner_include = True
    object = User

    show_button_save_continue = True

    success_message = _('User created successfully.')
    success_redirect = _('users-list')

    # inlines = [
    #     {
    #         'title': "Profile",
    #         'model': User,
    #         'form': UserCreationForm,
    #         'helper': StackedFormSetHelper,
    #         'owner_include': True,
    #         'fk_name': 'user'
    #     },
    # ]


class UserUpdateView(DashboardUpdateView):
    object = User
    page_title = _('User')
    header = _('Edit user')

    form_class = UserChangeForm

    success_message = _('User updated successfully')
    success_redirect = _('users-list')

    # inlines = [
    #     {
    #         'title': "Profile",
    #         'model': User,
    #         'form': UserProfileForm,
    #         'helper': StackedFormSetHelper,
    #         'owner_include': True,
    #         'fk_name': 'user'
    #     },
    # ]

    def get_queryset(self):
        return User.objects.filter()


class UserDeleteView(DashboardDeleteView):
    success_message = _('User deleted successfully')
    success_redirect = _('users-list')

    object = User
    validate_owner = False

    def get_queryset(self):
        return User.objects.filter()


class RoleList(DashboardListView):
    page_title = _('Roles')
    header = _('Roles')

    add_button_title = _('New role')
    add_button_url = reverse_lazy('users-role-create')

    table_class = RoleTable

    object = Role

    def get_queryset(self):
        return Role.objects.filter()


class RoleDetail(DashboardDetailView):
    object = Role

    page_title = _('Roles')
    header = _('Role detail')
    rows_based_on_form = RoleForm

    def get_queryset(self):
        return Role.objects.filter()


class RoleCreate(DashboardCreateView):
    page_title = _('Roles')
    header = _('Create new Role')

    form_class = RoleForm
    owner_include = False

    success_message = _('Role created successfully. Update role to select permissions.')
    success_redirect = _('users-role-list')

    object = Role

    # inlines = [
    #     {
    #         'title': "Permissions",
    #         'model': RolePermission,
    #         'form': RolePermissionForm,
    #         'helper': TabularFormSetHelper
    #     },
    # ]


class RoleUpdate(View):

    def get(self, request, pk, *args, **kwargs):

        role = get_object_or_404(Role, pk=pk)

        resources_selected = list(set(role.permissions.filter().values_list('id', flat=True)))

        context = {
            'role_form': RoleForm(instance=role),
            'helper': StackedFormSetHelper,
            'id': role.id,
            'description': role.description,
            'menu_tree': json.dumps(UserResource.get_menu_tree(selected_ids=resources_selected, custom_root_parent=[0.2])),
            'resources_tree': json.dumps(UserResource.get_resource_tree(selected_ids=resources_selected, custom_root_parent=[0.1])),
            'selected_data': json.dumps(resources_selected)

        }

        return render(request, 'users/roles.html', context)

    def post(self, request, *args, **kwargs):

        id = request.POST.get('id', None)
        instance = get_object_or_404(Role, pk=id)
        form_role = RoleForm(request.POST, instance=instance)

        if form_role.is_valid():

            obj = form_role.save(commit=False)
            selected_data = json.loads(request.POST.get('selected_data', '[]'))
            obj.permissions.set(UserResource.objects.filter(pk__in=selected_data))
            obj.save()

            messages.success(request, _('Role updated successfully.'))

        else:
            messages.error(request, _('Something is wrong. Please update again.'))

        return redirect('users-role-list')


class RoleDelete(DashboardDeleteView):
    success_message = _('Role deleted successfully.')
    success_redirect = _('users-role-list')

    header = _('Delete role')

    object = Role
    validate_owner = False

    def get_queryset(self):
        qs = Role.objects.filter()

        return qs


class UserChangePassword(View):
    http_method_names = ['post']

    def get(self, request, ids, *args, **kwargs):

        form = UserPasswordForm()

        user_list = User.objects.filter(pk__in=ids).annotate(full_name=Concat('first_name', Value(' '), 'last_name')).values_list('full_name', flat=True)

        context = {
            'form': form,
            'helper': FormSetHelper,
            'user_list': list(user_list),
            'ids': ','.join(ids)
        }
        return render(request, 'users/change_password.html', context=context)

    def post(self, request, *args, **kwargs):

        # only admins can change passwords
        if not request.user.is_admin:
            raise PermissionDenied()

        ids = request.POST.get('ids', None)

        if not ids:
            raise PermissionDenied()
        else:
            ids = ids.split(',')

        form = UserPasswordForm(request.POST)

        user_list = User.objects.filter(pk__in=ids).annotate(full_name=Concat('first_name', Value(' '), 'last_name'))

        if form.is_valid():

            for user in user_list:
                user.set_password(form.cleaned_data['password1'])
                user.save()

            messages.success(request, _('Password successfully changed.'))

            return redirect('users-list')

        context = {
            'form': form,
            'helper': FormSetHelper,
            'user_list': list(user_list.values_list('full_name')),
            'ids': ids
        }
        return render(request, 'users/change_password.html', context=context)
