import collections
from datetime import date, datetime, timezone
from typing import List

import tldextract
from django.conf import settings

from ..models import Domain

# store the latest N domains or so in a buffer, to prevent adding many duplicates. As some certificates
# are requested a few times in a short period, while this does not add any value.
# A better number would be the average number of domains per day or so... we'll figure this value out...
recently_added = collections.deque(maxlen=settings.DEQUE_LENGTH)


def add_domains(all_domains: List[str]) -> int:
    # this doesn't need a buffer as the amount of new domains for the .nl zone is pretty small.

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


class CaseOptimizedBulkInsert:
    # This class is an optimized version of the add_domains function that supports bulk inserts and
    # uses some tricks to improve performance, mainly in splitting domains and subdomains using stupid functions
    # instead of running tldextract. This approach will not work out of the box when using .co.uk domains(!)
    # It doesn't use a deque as that slows downs performance as well...

    # Share some data so bulk inserts are possible.
    new_data = []
    auto_write_batch_size = 2000

    # no init means a singleton
    def __init__(self):
        self.new_data = []
        self.auto_write_batch_size = settings.AUTO_WRITE_BATCH_SIZE

    def add_domain(self, domain: str, processing_date: date):
        # wildcards do not exist in the hostname field, so no need to filter.

        # we can use this shortcut as there are no two level top level domains in the dutch zones
        # the partition method is the fastest:
        rest, delimiter, suffix = domain.rpartition(".")
        subdomain, delimiter, domain = rest.rpartition(".")

        # inserting empty subdomains is slow / expensive. This is the fastest comparison, so run this one first.
        if subdomain == "":
            return 0

        if suffix not in settings.ACCEPTED_TLDS:
            return 0

        self.new_data.append(Domain(domain=domain, subdomain=subdomain, suffix=suffix, last_seen=processing_date))

        # add this to the buffer and just return 1 that this domain has been added, so the total number of domains
        # can be counted.
        if len(self.new_data) >= self.auto_write_batch_size:
            self.write_domains()

        return 1

    def write_domains(self):
        Domain.objects.bulk_create(self.new_data)
        amount_of_records = len(self.new_data)
        self.new_data = []
        return amount_of_records
