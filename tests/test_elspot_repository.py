from datetime import datetime
from elpris.models.elpris_models import ElspotRecord
from elpris.models.enums.price_area import PriceArea
from elpris.storage.elspot_repository import ElspotRepository


def test_upsert_opretter_tabel_og_indsætter():
    repo = ElspotRepository(":memory:")
    records = [
        ElspotRecord(
            HourUTC=datetime(2025, 6, 20, 0, 0, 0),
            HourDK=datetime(2025, 6, 20, 2, 0, 0),
            PriceArea=PriceArea.DK1,
            SpotPriceDKK=100.0,
            SpotPriceEUR=13.4,
        )
    ]
    n = repo.upsert_records(records)
    assert n == 1


def test_upsert_opdaterer_eksisterende():
    repo = ElspotRepository(":memory:")
    record = ElspotRecord(
        HourUTC=datetime(2025, 6, 20, 0, 0, 0),
        HourDK=datetime(2025, 6, 20, 2, 0, 0),
        PriceArea=PriceArea.DK1,
        SpotPriceDKK=100.0,
        SpotPriceEUR=13.4,
    )
    repo.upsert_records([record])

    record.SpotPriceDKK = 200.0
    n = repo.upsert_records([record])
    assert n == 1


def test_upsert_flere_records():
    repo = ElspotRepository(":memory:")
    records = [
        ElspotRecord(
            HourUTC=datetime(2025, 6, 20, h, 0, 0),
            HourDK=datetime(2025, 6, 20, h, 0, 0),
            PriceArea=PriceArea.DK1,
            SpotPriceDKK=100.0 + h,
            SpotPriceEUR=13.4,
        )
        for h in range(3)
    ]
    n = repo.upsert_records(records)
    assert n == 3


def test_upsert_tom_liste():
    repo = ElspotRepository(":memory:")
    n = repo.upsert_records([])
    assert n == 0
