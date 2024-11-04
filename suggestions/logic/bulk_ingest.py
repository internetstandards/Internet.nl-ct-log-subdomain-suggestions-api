from datetime import datetime

import simdjson

from suggestions.logic import log
from suggestions.logic.domains import case_optimized_bulk_insert_domain, case_optimized_write_inserts


def ingest_merklemap(file: str = "merklemap_data.jsonl"):
    # python3.12 manage.py bulk_ingest --file=merklemap_dns_records_database_25_10_2024.jsonl
    # This script parses the jsonl.xz dataset from merklemap.com and then imports this data into the database.

    # todo: add testcases using real test data. Verify that everything is written as intended.

    """
    This method parses the DNS database from merklemap and inserts all hostnames with subdomains.
    The database can be downloaded from: https://www.merklemap.com/dns-records-database

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

    # todo: script stops after 14.7% without any exceptions.
    """
    14.69%, 734,600,000 records processed, 5988655 domains added, current time: 2024-11-04 14:38:35.978075, time per iteration: 0.339215 seconds
    14.69%, 734,700,000 records processed, 5989339 domains added, current time: 2024-11-04 14:38:36.109885, time per iteration: 0.13181 seconds
    14.7%, 734,800,000 records processed, 5990143 domains added, current time: 2024-11-04 14:38:36.450732, time per iteration: 0.340847 seconds
    14.7%, 734,900,000 records processed, 5990892 domains added, current time: 2024-11-04 14:38:36.577851, time per iteration: 0.127119 seconds
    14.7%, 735,000,000 records processed, 5991577 domains added, current time: 2024-11-04 14:38:36.705463, time per iteration: 0.127612 seconds

    wc -l merklemap_dns_records_database_25_10_2024.jsonl -> 735024820
    The amount of lines is just: 735024820 (735.024.820). It promises 4 billion records... so where are they?
    This amount is FAR too low to be even remotely usable. Perhaps we are required to use some other data in this record
    and then still use the deque.
    
    If we process the text file with sift, do we see more records hidden somewhere? Merklemap doesn't know more it
    seems. See https://www.merklemap.com/search?query=basisbeveiliging&page=1.
    """

    log.info("Ingesting file: %s", file)

    # Merklemap says 'more than 4 billion records', so the progressbar goes to 5 billion:
    total_records = 5000000000
    counter = 0
    total_added_domains = 0
    previous_time = datetime.now()
    start_time = datetime.now()
    processing_date = start_time.date()

    parser = simdjson.Parser()

    # Don't use with xz.open(file, 'rt') as f, as that is slow. But if you don't want to inflate the file, you still can
    # by just replacing the open(... code.
    try:
        with open(file, "r") as f:
            for line in f:
                data = parser.parse(line)
                hostname = data["hostname"]
                # performance trick from the simdjson manual
                del data

                total_added_domains += case_optimized_bulk_insert_domain(hostname, processing_date)

                # only print output once every 10000 records, to keep the output clean
                if counter % 100000 == 0:
                    now = datetime.now()
                    print(
                        f"{round(counter / total_records * 100, 2)}%, "
                        f"{'{:,}'.format(counter)} records processed, "
                        f"{total_added_domains} domains added, "
                        f"current time: {now}, "
                        f"time per iteration: {(now - previous_time).total_seconds()} seconds",
                        flush=True,
                    )
                    previous_time = now
                counter += 1

        # After we're done, make sure everything is written, also the current data in the insert buffer:
        case_optimized_write_inserts()

    except KeyboardInterrupt:
        print("Processing interrupted. Exiting...")
        duration = (datetime.now() - start_time).total_seconds()
        domains_per_second = round(counter / duration)
        hours_needed_to_import_all = round(total_records / domains_per_second / 60 / 60, 2)
        print(
            f"Processed {counter} domains in {(datetime.now() - start_time).total_seconds()} seconds. {domains_per_second} domains per second."
        )
        print(f"It will take {hours_needed_to_import_all} hours to process 4 billion records...")
