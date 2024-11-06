import time

import certstream
from django.conf import settings

from . import log
from .domains import add_domains


def certstream_callback(message, context):
    # Perform some parsing of the certstream message

    if message["message_type"] == "heartbeat":
        return

    all_domains = []
    if message["message_type"] == "certificate_update":
        all_domains = message["data"]["leaf_cert"]["all_domains"]

    add_domains(all_domains)


def listen_for_events(
    message_callback, url, skip_heartbeats=True, setup_logger=True, on_open=None, on_error=None, **kwargs
):
    try:
        while True:
            c = certstream.core.CertStreamClient(
                message_callback, url, skip_heartbeats=skip_heartbeats, on_open=on_open, on_error=on_error
            )
            c.run_forever(ping_interval=15, **kwargs)
            time.sleep(5)
    except KeyboardInterrupt:
        log.info("Kill command received, exiting!!")
    except:
        log.exception("unhandled exception")


def ingest_certstream():
    log.info("Starting certstream ingestion from %s", settings.CERTSTREAM_SERVER_URL)
    listen_for_events(certstream_callback, url=settings.CERTSTREAM_SERVER_URL)
