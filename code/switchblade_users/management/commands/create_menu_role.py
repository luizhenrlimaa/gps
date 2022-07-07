from django.core.management.base import BaseCommand

from switchblade_users.models import UserResource, Role, User
from django import db


class Command(BaseCommand):
    help = 'Sync resources'

    def add_arguments(self, parser):
        parser.add_argument('role_name', nargs=1, type=str)
        parser.add_argument('--menu-only', nargs='?', const=True,  default=False)
        parser.add_argument('--set-to-user', nargs='?', const=True,  default=False)

    def handle(self, *args, **options):

        role_name = options['role_name'][0]
        menu_only = options['menu_only']
        set_to_user = options['set_to_user']

        # get resources
        self.stdout.write(self.style.NOTICE(f'Getting menu resources.'))

        menu_resources = UserResource.objects.filter()

        if menu_only:
            menu_resources = menu_resources.filter(menu_type=True)

        new_role = Role.objects.create(
            description=role_name
        )

        new_role.permissions.set(menu_resources)

        new_role.save()

        self.stdout.write(self.style.SUCCESS(f'Role {role_name} created.'))

        if set_to_user:

            all_users = User.objects.all()
            for user in all_users:
                user.roles.add(new_role)
                user.save()

            self.stdout.write(self.style.SUCCESS(f'Role {role_name} added to users.'))

        db.connections.close_all()
