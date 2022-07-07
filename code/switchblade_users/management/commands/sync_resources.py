from django.core.management.base import BaseCommand

from switchblade_dashboard.permissions import baseResource
from switchblade_users.models import UserResource
from django import db


class Command(BaseCommand):
    help = 'Sync resources'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):

        # get resources
        self.stdout.write(self.style.NOTICE(f'Getting software resources.'))
        resources = {k:v for k, v in baseResource.get_resources_as_tuple()}
        resources_to_delete = UserResource.objects.exclude(name__in=list(resources.keys()))
        self.stdout.write(self.style.SUCCESS(f'{resources_to_delete.count()} resources removed.'))
        resources_to_delete.delete()

        created_count = 0

        for slug, info in resources.items():

            obj, created = UserResource.objects.update_or_create(
                name=slug,
                defaults={'description': info[0], 'menu_type': 'menu.' in slug, 'order': info[1]}
            )

            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'{created_count} resources created.'))

        self.stdout.write(self.style.NOTICE(f'Resources sync done. Total: {UserResource.objects.count()}'))

        db.connections.close_all()