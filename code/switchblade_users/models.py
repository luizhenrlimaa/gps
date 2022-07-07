import datetime
from django.contrib import messages
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

import pandas as pd

from switchblade_dashboard.models import DashboardBaseModel


class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password):
        user = self.create_user(
            email,
            first_name,
            last_name
        )
        user.set_password(password)
        user.is_admin = True
        user.is_staff = True
        self.save = user.save(using=self._db)
        return user


class UserResource(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    menu_type = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} ({self.description})'

    @classmethod
    def get_resource_tree(cls, selected_ids=[], custom_root_parent=[]):

        base_qs = cls.objects.filter(menu_type=False).order_by('order', 'name')

        def get_children(node, parent_id, parent_ids=[]):

            children = base_qs.filter(name__regex=r'(^{}\.[^*][\w]*$)|(^{}\.[^*][\w]*\.\*)'.format(node, node))

            return_list = []

            for child in children:
                item = {
                    'id': child.id,
                    'name': child.name,
                    'description': child.description,
                    'selected': True if child.id in selected_ids else False,
                    'children': [],
                    'parents': parent_ids + [parent_id] + custom_root_parent
                }

                if child.name.split('.')[-1] == '*':
                    item['children'] = get_children(child.name.replace('.*', ''), child.id, item['parents'])

                return_list.append(item)

            return return_list

        results = []
        support_list = []
        leafs = {}

        roots = base_qs.filter(name__regex=r'^[^.]*\.\*')

        for root in roots:

            root_name = root.name.replace('.*', '')

            item = {
                'id': root.id,
                'name': root.name,
                'description': root.description,
                'selected': True if root.id in selected_ids else False,
                'children': get_children(root_name, root.id, []),
                'parents': custom_root_parent
            }

            results.append(item)

        return results



    @classmethod
    def get_menu_tree(cls, selected_ids=[], custom_root_parent=[]):

        result = []

        roots = cls.objects.filter(name__regex=r'menu.([^.]*)\.\*', menu_type=True).order_by('order', 'name')

        for root in roots:
            root_name = root.name.replace('.*', '')

            item = {
                'id': root.id,
                'name': root.name,
                'description': root.description,
                'selected': True if root.id in selected_ids else False,
                'children': [],
                'parents': custom_root_parent
            }

            children_1st_level = cls.objects.filter(name__regex=r'{}.([^*]\w*\.\*|\w[^.]*$)'.format(root_name), menu_type=True).order_by('order', 'name')

            for child_1st in children_1st_level:

                children_1st = []
                root_name = child_1st.name.replace('.*', '')
                is_child_root = True if child_1st.name.split('.')[-1] == '*' else False

                if is_child_root:

                    children_2nd_level = cls.objects.filter(name__regex=r'{}.[^*].*'.format(root_name), menu_type=True).order_by('order', 'name')

                    for child_2nd in children_2nd_level:

                        child_2nd_item = {
                            'id': child_2nd.id,
                            'name': child_2nd.name,
                            'description': child_2nd.description,
                            'selected': True if child_2nd.id in selected_ids else False,
                            'children': [],
                            'parents': [root.id, child_1st.id] + custom_root_parent
                        }

                        children_1st.append(child_2nd_item)

                item['children'].append({
                    'id': child_1st.id,
                    'name': child_1st.name,
                    'description': child_1st.description,
                    'selected': True if child_1st.id in selected_ids else False,
                    'children': children_1st,
                    'parents': [root.id] + custom_root_parent
                })

            result.append(item)

        return result


class Role(models.Model):
    description = models.CharField(max_length=80, unique=True)
    permissions = models.ManyToManyField(UserResource, through="switchblade_users.RolePermission")
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('description',)

    def __str__(self):
        return self.description

    def get_delete_url(self):
        return reverse('users-role-delete', kwargs={'pk': self.pk})

    def get_update_url(self):
        return reverse('users-role-update', kwargs={'pk': self.pk})

    def get_absolute_url(self):
        return reverse('users-role-detail', kwargs={'pk': self.pk})


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    resource = models.ForeignKey(UserResource, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.role} - {self.resource}'

    class Meta:
        ordering = ('role', 'resource')


class User(AbstractBaseUser, PermissionsMixin):

    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    email = models.EmailField(unique=True)
    phone = models.CharField(db_column='Phone', max_length=50, blank=True, null=True)
    password = models.CharField(max_length=128, db_column="Password")

    last_login = models.DateTimeField(blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)

    roles = models.ManyToManyField(Role, blank=True)
    individual_permissions = models.ManyToManyField(UserResource, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ('first_name', 'last_name')

    def __str__(self):
        return self.get_full_name()

    @classmethod
    def _filter_by_str(cls, q, first_match_id=True, raise_when_not_found=True):

        qs = cls.objects.filter()
        qs = qs.annotate(full_name=Concat('first_name', Value(' '), 'last_name')).filter(full_name__unaccent__icontains=q)

        if first_match_id:
            if qs.exists():
                return qs.first().id
            elif raise_when_not_found:
                raise ValueError(f'User {q} not found.')
            return None

        return qs

    @property
    def is_superuser(self):
        return self.is_admin

    def get_full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def get_short_name(self):
        return self.first_name

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return static('switchblade_dashboard/img/default_user.png')

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        if self.is_admin:
            return True
        allowed_resources = self.get_allowed_resources
        if perm in allowed_resources:
            return True
        return False

    def get_all_permissions(self, obj=None):

        return self.get_allowed_resources

    def get_delete_url(self):
        return reverse('users-delete', kwargs={'pk': self.pk})

    def get_update_url(self):
        return reverse('users-update', kwargs={'pk': self.pk})

    def get_absolute_url(self):
        return reverse('users-detail', kwargs={'pk': self.pk})

    @cached_property
    def get_allowed_resources(self):

        roles_list = list(RolePermission.objects.select_related('role', 'resource').filter(role__pk__in=self.roles.all().values_list('id', flat=True),
                                                        role__active=True).values_list('resource__name', flat=True))

        individual_list = list(self.individual_permissions.all().values_list('name', flat=True))

        return list(set(roles_list + individual_list))

    @classmethod
    def change_password(cls, request, ids):

        from .views import UserChangePassword

        return UserChangePassword().get(request, ids)
