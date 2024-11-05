from datetime import datetime, timedelta, timezone

from ..models import Domain


def suggest_subdomains(domain: str, suffix: str = "nl", period_in_days: int = 365):
    if not domain or not suffix or not period_in_days:
        return []

    some_time_ago = datetime.now(timezone.utc) - timedelta(days=period_in_days)

    # These are not distinct, as ct logs contain certificate requests and requests can be processed multiple times
    # per day. But even if a request is performed a few times per day for a domain the below logic will be
    # more than fast enough to reduce this set to unique values. A 'distinct' query is not needed and if performance
    # issues arise, distinct might be worth considering.
    return sorted(
        set(
            Domain.objects.filter(
                # not performing a last_seen__lte=now() as that is yet another thing for the database to process,
                # which makes querying slower. There is no strict need for windowing over time, only a need for showing
                # accurate results today.
                domain=domain,
                suffix=suffix,
                last_seen__gte=some_time_ago,
            ).values_list("subdomain", flat=True)
        )
    )
