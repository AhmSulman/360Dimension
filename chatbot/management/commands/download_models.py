from django.core.management.base import BaseCommand, CommandError
from chatbot.models import ChatbotConfig, ModelDownloader


class Command(BaseCommand):
    help = 'Download Mistral models for active chatbot configurations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--config-id',
            type=int,
            help='Download model for specific config ID only',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-download even if model exists',
        )

    def handle(self, *args, **options):
        if options['config_id']:
            try:
                config = ChatbotConfig.objects.get(id=options['config_id'])
                configs = [config]
            except ChatbotConfig.DoesNotExist:
                raise CommandError(f'ChatbotConfig with id {options["config_id"]} does not exist')
        else:
            configs = ChatbotConfig.objects.filter(is_active=True)

        if not configs:
            self.stdout.write(
                self.style.WARNING('No active chatbot configurations found.')
            )
            return

        self.stdout.write(f'Found {len(configs)} configuration(s) to process.')

        for config in configs:
            try:
                self.stdout.write(
                    self.style.SUCCESS(f'Downloading model for config: {config.name}')
                )

                # Check if model path exists and handle force option
                if config.models_path.exists() and not options['force']:
                    self.stdout.write(
                        self.style.WARNING(f'Model already exists for {config.name}, skipping. Use --force to re-download.')
                    )
                    continue

                model_path = config.ensure_models_downloaded()
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully downloaded model for: {config.name} to {model_path}')
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to download model for {config.name}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS('Model download process completed.')
        )
