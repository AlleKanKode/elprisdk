import duckdb
from elpris.models.elpris_models import ElspotRecord


class ElspotRepository:
    def __init__(self, db_path: str = "data/elpriser.duckdb"):
        self._db_path = db_path

    def upsert_records(self, records: list[ElspotRecord]) -> int:
        if not records:
            return 0

        with duckdb.connect(self._db_path) as con:
            con.sql("""
                CREATE TABLE IF NOT EXISTS elspotpriser (
                    HourUTC TIMESTAMP,
                    HourDK TIMESTAMP,
                    PriceArea VARCHAR,
                    SpotPriceDKK DOUBLE,
                    SpotPriceEUR DOUBLE,
                    PRIMARY KEY (HourUTC, PriceArea)
                )
            """)
            data = [
                (r.HourUTC, r.HourDK, r.PriceArea.value, r.SpotPriceDKK, r.SpotPriceEUR)
                for r in records
            ]
            con.executemany("""
                INSERT INTO elspotpriser
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT (HourUTC, PriceArea) DO UPDATE SET
                    HourDK = excluded.HourDK,
                    SpotPriceDKK = excluded.SpotPriceDKK,
                    SpotPriceEUR = excluded.SpotPriceEUR
            """, data)
            return len(data)
