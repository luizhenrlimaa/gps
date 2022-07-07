from dal import autocomplete
from django import forms
from django.utils.translation import gettext as _

from .models import User, Role, RolePermission


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
    password2 = forms.CharField(
        label=_('Password confirmation'), widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'roles', 'individual_permissions')

        widgets = {
            'roles': autocomplete.ModelSelect2Multiple(url='role-autocomplete'),
            'individual_permissions': autocomplete.ModelSelect2Multiple(url='userresource-autocomplete'),
        }

        help_texts = {
            'email': _('Must be unique and cannot be changed later'),
        }

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Passwords does not match"))
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserPasswordForm(forms.Form):
    password1 = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
    password2 = forms.CharField(
        label=_('Password confirmation'), widget=forms.PasswordInput)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Passwords does not match"))
        return password2


class UserChangeForm(forms.ModelForm):

    # password = ReadOnlyPasswordHashField(
    #     label=_("Password"),
    #     help_text=_(
    #         "Raw passwords are not stored, so there is no way to see this "
    #         "user's password, but you can change the password using "
    #         "<a href=\"{}\">this form</a>."
    #     ),
    # )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'roles', 'individual_permissions', 'is_active']
        widgets = {
            'roles': autocomplete.ModelSelect2Multiple(url='role-autocomplete'),
            'individual_permissions': autocomplete.ModelSelect2Multiple(url='userresource-autocomplete'),
        }

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['password'].help_text = self.fields['password'].help_text.format(
    #         '../password/')
    #     f = self.fields.get('user_permissions')
    #     if f is not None:
    #         f.queryset = f.queryset.select_related('content_type')

    # def clean_password(self):
    #     # Regardless of what the user provides, return the initial value.
    #     # This is done here, rather than on the field, because the
    #     # field does not have access to the initial value
    #     return self.initial["password"]


class UserProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name')
        widgets = {
            'first_name': forms.TextInput(attrs={'class':'form-control'}),
            'last_name': forms.TextInput(attrs={'class':'form-control'}),
        }


class UserTemplateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('is_active',)


class RoleForm(forms.ModelForm):

    class Meta:
        model = Role
        fields = ('description', 'active')


class RolePermissionForm(forms.ModelForm):

    class Meta:
        model = RolePermission
        fields = ('resource', )
        widgets = {
            'resource': autocomplete.ModelSelect2(url='userresource-autocomplete'),
        }
