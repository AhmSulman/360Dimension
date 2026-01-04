from django.core.management.base import BaseCommand
from dusty_jukebox.models import GuitarTuning, MusicalScale


class Command(BaseCommand):
    help = 'Populate default guitar tunings and musical scales'

    def handle(self, *args, **options):
        # Populate guitar tunings
        GuitarTuning.create_default_tunings()

        # Populate musical scales
        MusicalScale.create_default_scales()

        # Count created objects
        tunings_count = GuitarTuning.objects.count()
        scales_count = MusicalScale.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated {tunings_count} tunings and {scales_count} scales'
            )
        )
