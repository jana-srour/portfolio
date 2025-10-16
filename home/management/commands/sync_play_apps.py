from django.core.management.base import BaseCommand
from home.models import App
from home.views import fetch_play_store_app


class Command(BaseCommand):
    help = 'Sync all App records from Play Store'

    def handle(self, *args, **options):
        apps = App.objects.all()
        count = 0
        for app in apps:
            data = fetch_play_store_app(app.package)
            if data:
                app.sync(fetch_play_store_app)
                count += 1
                self.stdout.write(self.style.SUCCESS(f'Synced {app.package}'))
            else:
                self.stdout.write(self.style.WARNING(f'Failed to fetch {app.package}'))
        self.stdout.write(self.style.SUCCESS(f'Done. Synced {count} apps.'))
