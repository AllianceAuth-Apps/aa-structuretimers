from django.core.management import call_command
from django.core.management.base import BaseCommand

from allianceauth.services.hooks import get_extension_logger
from app_utils.logging import LoggerAddTag

from structuretimers import __title__

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


class Command(BaseCommand):
    help = "Preloads data required for this app from the EVE SDE"

    def handle(self, *args, **options):
        call_command(
            "esde_load_sde",
        )
