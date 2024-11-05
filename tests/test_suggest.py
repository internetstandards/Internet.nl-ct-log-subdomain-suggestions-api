from django.core.management import call_command
from freezegun import freeze_time

from ctlssa.suggestions.logic.suggest import suggest_subdomains


def test_suggest_subdomains(db):
    # the testdata.json file has been compiled using live data. It has been reduced to improve test performance
    # and some changes to domains have been made. But the duplicate entries and such are real (this data is from when
    # the deque was not implemented yet).

    # empty database, or not existing domains just delivers an empty list
    assert suggest_subdomains("example", "com", 365) == []

    # load the testdata.json fixture
    call_command("loaddata", "testdata.json", verbosity=0)

    with freeze_time("2024-10-30 12:00:00"):
        # in time, will deliver a set of subdomains
        assert suggest_subdomains("example", "nl", 365) == [
            "autodiscover",
            "cpanel",
            "cpcalendars",
            "cpcontacts",
            "ipv6",
            "mail",
            "webdisk",
            "webmail",
            "www",
        ]

        # incomplete call of the method yields no data:
        assert suggest_subdomains("example", "nl", 0) == []
        assert suggest_subdomains("example", "", 365) == []
        assert suggest_subdomains("", "nl", 365) == []

    # this will yield the same data as above as we don't support time travel in search
    with freeze_time("2024-1-30 12:00:00"):
        assert suggest_subdomains("example", "nl", 10) == [
            "autodiscover",
            "cpanel",
            "cpcalendars",
            "cpcontacts",
            "ipv6",
            "mail",
            "webdisk",
            "webmail",
            "www",
        ]

    # data is not present yet in this period, so don't suggest it.
    with freeze_time("2025-12-30 12:00:00"):
        assert suggest_subdomains("example", "nl", 10) == []
