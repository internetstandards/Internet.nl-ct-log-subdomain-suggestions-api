from datetime import datetime

from suggestions.logic.bulk_ingest import ingest_merklemap
from suggestions.logic.domains import CaseOptimizedBulkInsert
from suggestions.models import Domain


def test_ingest_merklemap(db):
    ingest_merklemap("suggestions/tests/sample_merklemap_data.jsonl")
    assert Domain.objects.count() == 33

    # test that the Domain objects are not stored or shared between CaseOptimizedBulkInsert instances.
    bulk_insert = CaseOptimizedBulkInsert()
    bulk_insert.write_domains()
    assert Domain.objects.count() == 33

    ingest_merklemap("suggestions/tests/sample_merklemap_data.xz")
    assert Domain.objects.count() == 66


def test_bulk_ingesting(db):
    bulk_insert = CaseOptimizedBulkInsert()

    # test that the buffer works: the buffer is filled but not yet written as it does not reach the limit:
    bulk_insert.add_domain("www.example.nl", datetime.now().date())
    assert Domain.objects.count() == 0

    bulk_insert.write_domains()
    assert Domain.objects.count() == 1

    # make sure nothing sticks
    bulk_insert.write_domains()
    assert Domain.objects.count() == 1
