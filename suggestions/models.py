from django.db import models


class Domain(models.Model):
    """
    In theory this subdivision can go down to 127 levels deep, and each DNS label can contain up to 63 characters,
    as long as the whole domain name does not exceed a total length of 255 characters. But in practice most domain
    registries limit at 253 characters.
    https://stackoverflow.com/questions/10552665/names-and-maximum-lengths-of-the-parts-of-a-url

    Longest domain in the world:
    https://llanfairpwllgwyngyllgogerychwyrndrobwllllantysiliogogogoch.co.uk
    """

    subdomain = models.CharField(max_length=2000)

    # this is what we search on. Simple search is enough probably.
    # Let's assume that the same cert if repeatedly requested multiple times a day, this might contain some duplicates.
    # probably these two fields have to be joined into one field. This allows one-hit searching and saves the creation
    # of an extra index. Perhaps only when very big datasets are used the separate index makes sense? I don't think so.
    # -> punycode is also < 64. (64 is used as it's a round number and 63 hurts my eyes)
    domain = models.CharField(max_length=64, db_index=True)
    suffix = models.CharField(max_length=64, db_index=True)

    # this is some information that makes searching faster, as we can use a shorter timespan or a more relevant
    # selection. We're not using datetime as the time of day is really not relevant, much to granular.
    # during the research phase it's nice to see when the most certs are created (at what time of day)
    # and we'll have to figure out how many per day. And on what days there will be more, for example on the first.
    # Perhaps there are some articles about that written by let's encrypt.
    # Current estimate: 4.5 million domains * 10 subdomains = 45.000.000 domains a year. A cert is regenerated every 90
    # days. So in a year 180.000.000 certs in NL are generated. So about 500.000 requests a day. So that's for www +
    # non www. So about a million records a day at least. So it's about 11 a second. 1000000 domains / 86400 seconds/day
    # We're currently seeing about between 0.5 to 2 per second, with some batches appearing.
    last_seen = models.DateField(db_index=True)
