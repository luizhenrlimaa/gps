from django.contrib import admin

# Register your models here.
from .forms import UserChangeForm, UserCreationForm
from .models import User, Role, RolePermission, UserResource

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'first_name',
                    'last_name', 'is_active', 'is_staff', 'is_admin', 'last_login')
    list_filter = ('is_admin', 'is_staff', 'is_active', 'last_login')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Information'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_admin',
                                      'roles', 'individual_permissions')}),
        (_('Important Dates'), {'fields': ('last_login', 'creation_date')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2')}
         ),
    )
    search_fields = ('email', 'first_name', 'last_name')
    readonly_fields = ('creation_date', 'last_login')
    ordering = ('first_name', 'last_name')
    filter_horizontal = ('roles', 'individual_permissions')

class RolePermissionAdminInline(admin.TabularInline):
    model = RolePermission


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    inlines = [
        RolePermissionAdminInline
    ]


@admin.register(UserResource)
class UserResourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'menu_type']
    list_filter = ['menu_type']
    search_fields = ['name', 'description']

