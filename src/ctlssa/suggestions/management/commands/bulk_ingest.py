from django.core.management.base import BaseCommand

from ...logic.bulk_ingest import ingest_merklemap


class Command(BaseCommand):
    help = (
        "Ingests the locally present merklemap data file called merklemap_data.jsonl.xz. "
        "Use --file to specify a different file."
    )

    # The arguments API is garbage, so here is the direct link to the documentation:
    # https://docs.djangoproject.com/en/5.1/howto/custom-management-commands/
    def add_arguments(self, parser):
        # parser.add_argument("--file", action="store_true")
        # accept a custom file:
        parser.add_argument("--file", type=str)

    def handle(self, *args, **options):
        ingest_merklemap(options.get("file", "merklemap_data.jsonl"))
