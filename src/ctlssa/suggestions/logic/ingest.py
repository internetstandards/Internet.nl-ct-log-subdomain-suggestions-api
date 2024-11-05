import certstream
from django.conf import settings

from suggestions.logic import log
from suggestions.logic.domains import add_domains


def certstream_callback(message, context):
    # Perform some parsing of the certstream message

    if message["message_type"] == "heartbeat":
        return

    all_domains = []
    if message["message_type"] == "certificate_update":
        all_domains = message["data"]["leaf_cert"]["all_domains"]

    add_domains(all_domains)


def ingest_certstream():
    log.info("Starting certstream ingestion from %s", settings.CERTSTREAM_SERVER_URL)
    certstream.listen_for_events(certstream_callback, url=settings.CERTSTREAM_SERVER_URL)
