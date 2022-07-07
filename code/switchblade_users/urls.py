from django.contrib.auth.decorators import login_required
from django.urls import path, include, reverse_lazy
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

from switchblade_dashboard.forms import FormSetHelper

from switchblade_dashboard.decorators import register_resource
from switchblade_dashboard.views import DashboardIndexView
from .apis import UserUpdateAvatarAPI
from .autocomplete import UserAutocomplete, UserResourceAutocomplete, RoleAutocomplete
from .views import UserNotification, UserListView, UserCreateView, UserDetailView, \
    UserUpdateView, UserDeleteView, UserUpdateAvatarView, RoleList, RoleCreate, RoleDetail, \
    RoleUpdate, RoleDelete, UserChangePassword, UserProfileChangeView

urlpatterns = [

    path('auth/', include([
        path('login/', auth_views.LoginView.as_view(template_name='auth/login.html', redirect_authenticated_user=True),
             name='login'),
        path('logout/', auth_views.LogoutView.as_view(), name='logout'),

        path('reset-password/', auth_views.PasswordResetView.as_view(template_name='auth/password_reset.html',
                                                                     extra_context={'helper': FormSetHelper}),
             name='password_reset'),

        path('reset-password-done/', auth_views.PasswordResetDoneView.as_view(template_name='auth/password_reset_done.html'),
             name='password_reset_done'),

        path('reset-password-confirm/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(
            template_name='auth/password_reset_confirm.html',
            extra_context={'helper': FormSetHelper}),
            name='password_reset_confirm'),

        path('reset-password-complete/', auth_views.PasswordResetCompleteView.as_view(
            template_name='auth/password_reset_complete.html'),
            name='password_reset_complete'),

        path('notifications', login_required(UserNotification.as_view()), name='user-notifications'),
        path('autocomplete/', login_required(UserAutocomplete.as_view()), name='user-autocomplete'),
    ])),

    path('profile/', include([
        path('', register_resource(
            DashboardIndexView.as_view(page_title='Profile', header='Profile', columns=[3, 3, 3, 3])),
             name='dashboard-profile'),
        path('personal-info/', register_resource(UserProfileChangeView), name='profile-personal-info'),
        path('avatar/', register_resource(UserUpdateAvatarView), name='profile-avatar-update'),
        path('change-password/', auth_views.PasswordChangeView.as_view(success_url=reverse_lazy('profile-password-done'), template_name='auth/password_change.html',
                                                                       extra_context={'helper': FormSetHelper, 'PageTitle': 'Change Password'}),

             name='profile-password-change'),
        path('change-password-done/',
             auth_views.PasswordChangeDoneView.as_view(template_name='auth/password_change_done.html'),
             name='profile-password-done'),
    ])),


    path('config/', include([
        path('change-password/', login_required(UserChangePassword.as_view()), name='users-change-password'),

        path('users/', include([
            path('', register_resource(UserListView), name='users-list'),
            path('create/', register_resource(UserCreateView), name='users-create'),
            path('detail/<int:pk>', register_resource(UserDetailView), name='users-detail'),
            path('update/<int:pk>', register_resource(UserUpdateView), name='users-update'),
            path('delete/<int:pk>', register_resource(UserDeleteView), name='users-delete'),
        ])),

        path('roles/', include([
            path('', register_resource(RoleList), name='users-role-list'),
            path('create/', register_resource(RoleCreate), name='users-role-create'),
            path('detail/<int:pk>', register_resource(RoleDetail), name='users-role-detail'),
            path('update/<int:pk>', register_resource(RoleUpdate.as_view(), as_view=False, resource='role.update',description="Update Roles"), name='users-role-update'),
            path('delete/<int:pk>', register_resource(RoleDelete), name='users-role-delete'),
            path('autocomplete/', login_required(RoleAutocomplete.as_view()), name='role-autocomplete'),
            path('resources/autocomplete/', login_required(UserResourceAutocomplete.as_view()),
                 name='userresource-autocomplete'),
        ])),

    ])),


    path('api/', include([
        path('users/avatar/update/', UserUpdateAvatarAPI.as_view(), name='api-users-avatar-update'),
    ])),
]
