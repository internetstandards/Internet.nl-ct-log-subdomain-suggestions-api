from datetime import datetime

import simdjson
import xz

from ..logic import log
from ..logic.domains import CaseOptimizedBulkInsert


def ingest_merklemap(file: str = "merklemap_data.jsonl"):
    """
    This method parses the DNS database from merklemap and inserts all hostnames with subdomains.
    The database can be downloaded from: https://www.merklemap.com/dns-records-database

    Merklemap states having about 4 billion records, which is correct. This is split up between 735024820 hostnames
    in the file from the 25th of october. This is verified through the web interface and sifting through the extracted
    xz file.

    Working with compressed data is not ideal. Therefore this code just reads the binary data from the extracted xz
    file. If you don't have 448 gigabytes of free space, you can resort to reading the data from the xz file directly.
    Some sample code is provided below and will be a lot slower, but it should work very neatly where python is great
    at hiding all the pain with dealing with buffers, lines and all that type of junk.

    Uncompressing the xz data can be done using the following command and takes about 30 to 40 minutes on an m1 max:
    unxz --keep --threads=8 --decompress merklemap_dns_records_database_25_10_2024.xz

    We assume that the records in the jsonl file are unique per hostname. This makes importing straightforward, as only
    the hostname needs to be read and inserted into the database. There are still some challenges, which have been met.

    We assume the jsonl file has a unique hostname per line. The data inside this hostname, the set of DNS records,
    are not relevant for us as every possible relevant domain is already in the list of hostnames.

    A separate bulk-insert method is used as that cuts processing time from 0.488631 to 0.162816 seconds per 100k
    processed records.

    The use of python 3.12, the highest possible with simdjson, cuts about 10% of total processing time.

    The use of simdjson also cuts a significant part of processing time compared to the stock json parser shipping with
    python. The optimziations suggested in the optimization part of the simdjson manual are applied here. These are
    only parsing the field that we need and reusing the parser.
    See: https://pysimdjson.tkte.ch/performance.html

    Methods use precalculated dates / values as much as possible.

    The add_domains record has been rewritten to not make use of tldextract, it exploits the fact that all dutch domain
    names end on a single word, such as '.amsterdam' or '.nl'. This script needs a small rewrite to also support .co.uk
    and such. We don't use the deque, as that also seriously reduces the speed of adding data. Especially at a high
    value,

    Running this script takes about 150 megabyte of ram :)
    """

    log.info("Ingesting file: %s", file)

    # Merklemap says 'more than 4 billion records', that amounts to about 800M hostnames
    total_records = 750000000
    counter = 0
    bulk_insert = CaseOptimizedBulkInsert()
    parser = simdjson.Parser()
    total_added_domains = 0

    # stats
    show_status_per = 1000000
    previous_time = datetime.now()
    processing_date = datetime.now().date()

    try:
        with my_open(file) as f:
            for line in f:
                data = parser.parse(line)
                hostname = data["hostname"]
                # performance trick from the simdjson manual
                del data

                total_added_domains += bulk_insert.add_domain(hostname, processing_date)

                if counter % show_status_per == 0:
                    now = datetime.now()
                    records_left = total_records - counter
                    time_left = round(records_left / show_status_per * (now - previous_time).total_seconds() / 60, 2)
                    log.info(
                        f"{'%.2f' % round(counter / total_records * 100, 2)}%, "
                        f"{'{:,}'.format(counter).replace(',', '.')} processed, "
                        f"+{'{:,}'.format(total_added_domains).replace(',', '.')} domains, "
                        f"time/iteration: {(now - previous_time).total_seconds()} s, "
                        f"time left: {time_left} m",
                        # flush=True,
                    )
                    previous_time = now
                counter += 1

        # After we're done, make sure everything is written, also the current data in the insert buffer:
        bulk_insert.write_domains()
        log.info(f"Import finished, added {total_added_domains} records in total.")

    except KeyboardInterrupt:
        log.info("Processing interrupted. Exiting...")


def my_open(filename):
    if filename.endswith(".xz"):
        return xz.open(filename, "rt")
    else:
        return open(filename, "rb")
