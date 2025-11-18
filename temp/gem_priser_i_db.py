import json
import pandas as pd
import duckdb
from typing import List, Dict, Any

def upsert_elspotpriser(con: duckdb.DuckDBPyConnection, df: pd.DataFrame, table_name: str = 'elspotpriser'):
    """
    Opretter eller opdaterer (upsert) elprisdata i en DuckDB-tabel.
    Tabellen oprettes med en primærnøgle på (HourUTC, PriceArea) for at undgå dubletter.

    Args:
        con (duckdb.DuckDBPyConnection): En aktiv DuckDB-forbindelse.
        df (pd.DataFrame): DataFrame med de nye prisdata, der skal indsættes/opdateres.
        table_name (str): Navnet på tabellen.
    """
    # Trin 1: Opret tabellen, hvis den ikke allerede eksisterer.
    # Vi definerer en primærnøgle for at sikre, at hver time/prisområde-kombination er unik.
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

    # Trin 2: Brug INSERT ... ON CONFLICT til at indsætte nye rækker eller opdatere eksisterende.
    # Dette kaldes en "upsert"-operation.
    # Hvis en række med samme (HourUTC, PriceArea) allerede findes, opdateres de andre felter.
    # 'excluded' refererer til værdierne fra den række, vi forsøger at indsætte.
    con.execute(f"""
        INSERT INTO {table_name}
        SELECT * FROM df
        ON CONFLICT (HourUTC, PriceArea) DO UPDATE SET
            HourDK = excluded.HourDK,
            SpotPriceDKK = excluded.SpotPriceDKK,
            SpotPriceEUR = excluded.SpotPriceEUR;
    """)
    print(f"{con.last_changes} rækker blev ændret/indsat i tabellen.")

def load_records_from_json(json_path: str) -> List[Dict[str, Any]]:
    """Indlæser 'records' fra en JSON-fil."""
    print(f"Indlæser data fra '{json_path}'...")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('records', [])
    except FileNotFoundError:
        print(f"Fejl: Filen '{json_path}' blev ikke fundet.")
        return []
    except json.JSONDecodeError:
        print(f"Fejl: Kunne ikke parse JSON fra filen '{json_path}'.")
        return []

def main():
    """
    Hovedfunktion til at indlæse data fra JSON og gemme i DuckDB.
    """
    json_file = '/home/henrik/source/akk/live/ts30/elpris/elpris-raw.json'
    db_file = 'elpriser.duckdb'
    table_name = 'elspotpriser'

    records = load_records_from_json(json_file)
    if not records:
        print("Ingen 'records' fundet i JSON-filen.")
        return

    # Konverter data til en Pandas DataFrame
    df = pd.DataFrame(records)
    df['HourUTC'] = pd.to_datetime(df['HourUTC'])
    df['HourDK'] = pd.to_datetime(df['HourDK'])
    print(f"Fandt {len(df)} rækker data i JSON-filen.")

    # Opret forbindelse til DuckDB og udfør upsert-operationen
    with duckdb.connect(database=db_file, read_only=False) as con:
        print(f"Åbner forbindelse til DuckDB-databasen '{db_file}'...")
        upsert_elspotpriser(con, df, table_name)
        print("Data er gemt med succes.")

        # Verificer ved at vise de seneste data og det totale antal rækker
        print(f"\nVerificering: Viser de seneste 5 rækker fra tabellen '{table_name}':")
        result = con.sql(f"SELECT * FROM {table_name} ORDER BY HourUTC DESC LIMIT 5").to_df()
        print(result)
        total_rows = con.sql(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"\nTabellen '{table_name}' indeholder nu i alt {total_rows} rækker.")

if __name__ == '__main__':
    main()