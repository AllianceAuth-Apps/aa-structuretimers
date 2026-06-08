from django.core.management import call_command
from django.core.management.base import BaseCommand

from allianceauth.services.hooks import get_extension_logger

logger = get_extension_logger(__name__)


class Command(BaseCommand):
    help = "Preloads data required for this app from the EVE SDE"

    def handle(self, *args, **options):
        call_command(
            "esde_load_sde",
        )
