from django.core.management.base import BaseCommand

from ...logic.ingest import ingest_certstream


class Command(BaseCommand):
    help = "Ingests data from the configured certstream instance."

    def handle(self, *args, **options):
        ingest_certstream()
