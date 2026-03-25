# your_app/management/commands/clear_meetings.py
from django.core.management.base import BaseCommand
from events.models import Meeting

class Command(BaseCommand):
    help = 'Clears all Meeting records'

    def handle(self, *args, **options):
        deleted_count, _ = Meeting.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_count} meetings.'))
