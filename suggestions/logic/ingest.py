import collections
import logging
from datetime import datetime, timezone
from typing import List

import certstream
import tldextract
from django.conf import settings

from suggestions.models import Domain

log = logging.getLogger(__package__)

# store the latest N domains or so in a buffer, to prevent adding many duplicates. As some certificates
# are requested a few times in a short period, while this does not add any value.
# A better number would be the average number of domains per day or so... we'll figure this value out...
recently_added = collections.deque(maxlen=settings.DEQUE_LENGTH)


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


def add_domains(all_domains: List[str]) -> None:
    # from here on out just work with the heuristics of the data we get. The heuristics are written in comments.
    for domain in set(all_domains):
        # prevent double requests and other behavior that causes redundancies to create duplicate records
        # this saves a TON of space. Run this first, before extracting the domain, a small optimization.
        if domain in recently_added:
            continue

        extracted = tldextract.extract(domain)
        if settings.ACCEPTED_TLDS and extracted.suffix not in settings.ACCEPTED_TLDS:
            continue

        # wildcard does not add value, most wildcards are just '*', a wildcard under a subdomain also happens
        # frequently and is dealt with below
        if extracted.subdomain == "*":
            continue

        # Storing all domains without a subdomain will yield into a 1/3rd larger database without the benefit of
        # having new subdomains to suggest. We _might_ always suggest the www subdomain, just to save a large portion
        # of the data again.
        # www: 2903
        # "": 3976
        # non-www: 4400
        if extracted.subdomain == "":
            continue

        # Any wildcard is not usable. Only if the subdomain that hosts the wildcard also has a cert, it is seen
        # as a valid domain. This check is performed *after* the == '*' check as this is a bit slower.
        if "*" in extracted.subdomain:
            continue

        # For now do not perform a database lookup when the last domain was seen and update it. Just add a new record
        # and that's it. It's much faster.
        log.debug(f"ingesting {domain}")
        recently_added.append(domain)
        Domain.objects.create(
            domain=extracted.domain,
            subdomain=extracted.subdomain,
            suffix=extracted.suffix,
            # the actual time does not matter, the date is just fine.
            last_seen=datetime.now(timezone.utc).date(),
        )
