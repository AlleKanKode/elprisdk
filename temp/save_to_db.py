import duckdb
#import pandas as pd
from pydantic import ValidationError
import sys
from pathlib import Path

# --> Terminator har lavet nedenstående for at importere modellerne, det er lidt crazy rodet hvis du spørger mig <--

# Tilføj 'src' til sys.path for at kunne importere fra 'models'
# Dette gør scriptet mere robust, da det kan køres fra forskellige steder
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

from src.models.elpris_models import ElspotResponse, ElspotRecord


def load_elspot_response_from_json(json_path: str) -> ElspotResponse | None:
    """
    Indlæser og deserialiserer elspot-data fra en JSON-fil til Pydantic-modeller.
    Bruger Pydantic's `parse_file` til at læse, parse og validere i ét kald.
    """
    print(f"Indlæser og validerer data fra '{json_path}'...")
    try:
        return ElspotResponse.parse_file(json_path)
    except FileNotFoundError:
        print(f"Fejl: Filen '{json_path}' blev ikke fundet.")
        return None
    except ValidationError as e:
        print(f"Fejl: Data i '{json_path}' matcher ikke ElspotResponse-modellen.\n{e}")
        return None
    except Exception as e:
        print(f"En uventet fejl opstod under læsning af '{json_path}': {e}")
        return None


def upsert_elspotpriser(con: duckdb.DuckDBPyConnection, records: list[ElspotRecord], table_name: str = 'elspotpriser'):
    """
    Opretter eller opdaterer (upsert) elprisdata i en DuckDB-tabel.
    Tabellen oprettes med en primærnøgle på (HourUTC, PriceArea) for at undgå dubletter.
    Bruger duckdb.register() til at behandle listen af Pydantic-objekter som en tabel.

    Args:
        con (duckdb.DuckDBPyConnection): En aktiv DuckDB-forbindelse.
        records (list[ElspotRecord]): En liste af ElspotRecord-objekter.
        table_name (str): Navnet på tabellen.
    """
    
    # Opret tabellen, hvis den ikke eksisterer, med en primærnøgle.
    con.sql(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            HourUTC TIMESTAMP,
            HourDK TIMESTAMP,
            PriceArea VARCHAR,
            SpotPriceDKK DOUBLE,
            SpotPriceEUR DOUBLE,
            PRIMARY KEY (HourUTC, PriceArea)
        );
    """)
    print(f"Tabel '{table_name}' er sikret eksisterer.")

    # Registrer listen af Pydantic-objekter som en virtuel tabel ved navn 'new_records_view'
    # Dette er meget effektivt, da data ikke kopieres.
    con.register('new_records_view', records)

    # Brug INSERT ... ON CONFLICT til at indsætte nye rækker eller opdatere eksisterende.
    # 'excluded' refererer til værdierne fra den række, vi forsøger at indsætte.
    con.execute(f"""
        INSERT INTO {table_name}
        SELECT * FROM new_records_view
        ON CONFLICT (HourUTC, PriceArea) DO UPDATE SET
            HourDK = excluded.HourDK,
            SpotPriceDKK = excluded.SpotPriceDKK,
            SpotPriceEUR = excluded.SpotPriceEUR;
    """)
    print(f"{con.last_changes} rækker blev ændret/indsat i tabellen '{table_name}'.")

    # Ryd op ved at fjerne den virtuelle tabel
    con.unregister('new_records_view')


def main():
    """
    Hovedfunktion: Indlæser validerede data fra JSON og gemmer dem i DuckDB.
    """
    # Brug Path til at håndtere stier - det er mere platformsuafhængigt.
    json_file = Path(__file__).resolve().parent / 'elpris-raw.json'
    db_file = Path(__file__).resolve().parent / 'elpriser.duckdb'
    table_name = 'elspotpriser'

    # 1. Indlæs og valider data med Pydantic-modellen
    elspot_data = load_elspot_response_from_json(str(json_file))
    if not elspot_data or not elspot_data.records:
        print("Ingen gyldige 'records' fundet. Afslutter.")
        return

    print(f"Valideret {len(elspot_data.records)} records fra JSON-fil.")

    # 2. Opret forbindelse til DuckDB og gem data direkte fra Pydantic-objekterne
    with duckdb.connect(database=str(db_file), read_only=False) as con:
        print(f"Åbner forbindelse til DuckDB-databasen '{db_file}'...")
        upsert_elspotpriser(con, elspot_data.records, table_name)
        print("Data er gemt med succes.")


if __name__ == '__main__':
    main()
