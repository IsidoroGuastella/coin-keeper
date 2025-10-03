# accounts/management/commands/cleanup_unverified.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = "Elimina utenti non verificati più vecchi di X ore (default 24h)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--hours", type=int, default=24,
            help="Numero di ore dopo cui eliminare gli utenti non verificati."
        )

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(hours=options["hours"])
        to_delete = User.objects.filter(is_verified=False, date_joined__lt=cutoff)
        count = to_delete.count()
        to_delete.delete()
        self.stdout.write(self.style.SUCCESS(f"Eliminati {count} utenti non verificati."))
