import contextlib
from datetime import date, datetime, timedelta, timezone

from ..models import Domain


def suggest_subdomains(domain: str, suffix: str = "nl", period_in_days: int = 365, max_date: str = ""):
    if not domain or not suffix or not period_in_days:
        return []
    # Results are not distinct, as ct logs contain certificate requests and requests can be processed multiple times
    # per day. But even if a request is performed a few times per day for a domain the below logic will be
    # more than fast enough to reduce this set to unique values. A 'distinct' query is not needed and if performance
    # issues arise, distinct might be worth considering.

    # The reason for using two distinct queries is to see if there are performance differences between the two for
    # current and historical data. The assumption is that less filtering results in better performance. We'll see
    # on the long run how this pans out.

    # silently fall back if the date value is not according to specification
    with contextlib.suppress(ValueError):
        # suppress "isoformat must be a string"
        if not max_date:
            max_date = ""
        max_date = date.fromisoformat(max_date)

    if max_date:
        some_time_ago = max_date - timedelta(days=period_in_days)
        query = Domain.objects.filter(
            # not performing a last_seen__lte=now() as that is yet another thing for the database to process,
            # which makes querying slower. There is no strict need for windowing over time, only a need for showing
            # accurate results today.
            domain=domain,
            suffix=suffix,
            last_seen__gte=some_time_ago,
            last_seen__lte=max_date,
        ).values_list("subdomain", flat=True)
    else:
        some_time_ago = datetime.now(timezone.utc) - timedelta(days=period_in_days)
        query = Domain.objects.filter(
            # not performing a last_seen__lte=now() as that is yet another thing for the database to process,
            # which makes querying slower. There is no strict need for windowing over time, only a need for showing
            # accurate results today.
            domain=domain,
            suffix=suffix,
            last_seen__gte=some_time_ago,
        ).values_list("subdomain", flat=True)

    return sorted(set(query))
