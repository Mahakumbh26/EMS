import os
from django.core.management.base import BaseCommand
from django.conf import settings
from accounts.models import Profile

class Command(BaseCommand):
    help = "Delete orphaned profile images"

    def handle(self, *args, **kwargs):
        media_dir = os.path.join(settings.MEDIA_ROOT,"profile_images")

        if not os.path.exists(media_dir):
            self.stdout.write("No media directory found.")
            return

        # Files currently referenced in DB
        used_files = set(
            Profile.objects.exclude(Photo_link="")
            .values_list("Photo_link", flat=True)
        )

        deleted = 0

        for file_name in os.listdir(media_dir):
            if file_name not in used_files:
                full_path = os.path.join(media_dir,file_name)
                os.remove(full_path)
                deleted += 1

        self.stdout.write(f"Deleted {deleted} orphaned files.")
