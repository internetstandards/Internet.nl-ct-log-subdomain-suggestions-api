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

        assert suggest_subdomains("example", "com", 365) == ["www"]
        assert suggest_subdomains("dubbelresultaat", "nl", 365) == ["www"]

        # incomplete call of the method yields no data:
        assert suggest_subdomains("example", "nl", 0) == []
        assert suggest_subdomains("example", "", 365) == []
        assert suggest_subdomains("", "nl", 365) == []

    with freeze_time("2024-12-30 12:00:00"):
        # This will result in no data, as in 10 days no domains from 2024 have been seen after december first,
        # so looking 10 days in the past results in no data.
        assert suggest_subdomains("2024", "nl", 10) == []

        # broaden the time frame to get results.
        assert suggest_subdomains("2024", "nl", 30) == ["december"]
        assert suggest_subdomains("2024", "nl", 65) == ["december", "november"]

    with freeze_time("2023-12-30 12:00:00"):
        # Now you will get everything from 2024, because in real life you cannot go back in time :)
        assert suggest_subdomains("2024", "nl", 365) == [
            "april",
            "augustus",
            "december",
            "februari",
            "januari",
            "juli",
            "juni",
            "maart",
            "mei",
            "november",
            "oktober",
            "september",
        ]

    # testing a time-window
    with freeze_time("2024-12-30 12:00:00"):
        assert suggest_subdomains("2023", "nl", 10, "2023-10-01") == ["oktober"]
        assert suggest_subdomains("2023", "nl", 65, "2023-10-01") == ["augustus", "oktober", "september"]

    # data is not present yet in this period, so don't suggest it.
    with freeze_time("2025-12-30 12:00:00"):
        assert suggest_subdomains("example", "nl", 10) == []
