import collections
from datetime import date, datetime, timezone
from typing import List

import tldextract
from django.conf import settings

from suggestions.models import Domain

# store the latest N domains or so in a buffer, to prevent adding many duplicates. As some certificates
# are requested a few times in a short period, while this does not add any value.
# A better number would be the average number of domains per day or so... we'll figure this value out...
recently_added = collections.deque(maxlen=settings.DEQUE_LENGTH)

# this anti pattern is used to drastically speed up database inserts, from single to bulk inserts.
bulk_insert_data = []
auto_write_batch_size = 2000


def add_domains(all_domains: List[str]) -> int:
    total_domains_added = 0

    # from here on out just work with the heuristics of the data we get. The heuristics are written in comments.
    for domain in set(all_domains):
        # prevent double requests and other behavior that causes redundancies to create duplicate records
        # this saves a TON of space. Run this first, before extracting the domain, a small optimization.

        # Warning: in bulk operations the deque is EXTREMELY slow. A longer deque with 100k records will slow down
        # imports to a near halt. So assume in bulk-imports that this deque is not needed.
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
        # log.debug(f"ingesting {domain}")
        recently_added.append(domain)

        Domain.objects.create(
            domain=extracted.domain,
            subdomain=extracted.subdomain,
            suffix=extracted.suffix,
            # the actual time does not matter, the date is just fine.
            last_seen=datetime.now(timezone.utc).date(),
        )

        total_domains_added += 1

    return total_domains_added


def case_optimized_bulk_insert_domain(domain: str, processing_date: date):
    global bulk_insert_data

    # prevents working with "modes" which is very convoluting.
    # don't use a deque, as that is very slow.
    # use simple string manipulation to prevent tldextract slowing stuff down.
    # don't filter on wildcards, those don't exist in the dataset.
    # assume all hostname records are unique (same with the other insert method)

    # we can use this shortcut as there are no two level top level domains in the dutch zones
    # the partition method is the fastest:
    rest, delimiter, suffix = domain.rpartition(".")
    subdomain, delimiter, domain = rest.rpartition(".")

    # inserting empty subdomains is slow / expensive. This is the fastest comparison, so run this one first.
    if subdomain == "":
        return 0

    if suffix not in settings.ACCEPTED_TLDS:
        return 0

    # is_last_call is used to also add the last records that are not flushed to the database yet...
    bulk_insert_data.append(Domain(domain=domain, subdomain=subdomain, suffix=suffix, last_seen=processing_date))

    if len(bulk_insert_data) >= auto_write_batch_size:
        case_optimized_write_inserts()

    return 1


def case_optimized_write_inserts():
    global bulk_insert_data
    Domain.objects.bulk_create(bulk_insert_data)
    amount_of_records = len(bulk_insert_data)
    bulk_insert_data = []
    return amount_of_records
