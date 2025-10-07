from pydantic import BaseModel, Field
from datetime import datetime
from typing import List
import json

# Dette er en Pydantic-version af elpris_models.py.
# Hovedforskellen er, at Pydantic ikke kun er en datastruktur,
# men også et validerings- og parsing-bibliotek.
#
# Fordele ved Pydantic her:
# - Automatisk type-konvertering: Strengen "2025-08-18T22:00:00" bliver automatisk
#   konverteret til et datetime-objekt uden behov for en helper-funktion.
# - Indbygget serialisering/deserialisering: .dict() og .json() metoder er standard.
#   Man behøver ikke skrive to_dict() eller from_dict() manuelt.
# - Robust fejlhåndtering: Hvis data ikke matcher modellen, får man en klar
#   ValidationError.


class ElspotRecord(BaseModel):
    """
    Pydantic model for a single electricity price record.
    Felter er med store bogstaver for at matche JSON-data direkte.
    Pydantic håndterer automatisk konvertering fra JSON-typer til Python-typer.
    """
    HourUTC: datetime
    HourDK: datetime
    PriceArea: str
    SpotPriceDKK: float
    SpotPriceEUR: float

    # Ingen grund til from_dict eller to_dict - Pydantic klarer det.


class ElspotResponse(BaseModel):
    """Pydantic model for the entire API response from Energinet Elspotprices."""
    total: int
    dataset: str
    sort: str
    filters: str
    records: List[ElspotRecord] = Field(default_factory=list)

    # Pydantic vil automatisk bruge ElspotRecord-modellen til at parse
    # hvert element i 'records'-listen.


def load_elspot_response_from_json(json_path: str) -> ElspotResponse:
    """
    Loads and deserializes elspot data from a JSON file into Pydantic models.
    Pydantic's `parse_file` metode læser, parser og validerer filen i ét kald.
    """
    try:
        return ElspotResponse.parse_file(json_path)
    except FileNotFoundError:
        print(f"Fejl: Filen '{json_path}' blev ikke fundet.")
        # Returner en tom eller default response for at undgå at crashe
        return ElspotResponse(total=0, dataset="", sort="", filters="", records=[])
    except Exception as e:
        print(f"Fejl under parsing af JSON fra '{json_path}': {e}")
        return ElspotResponse(total=0, dataset="", sort="", filters="", records=[])


def save_elspot_response_to_json(response_data: ElspotResponse, json_path: str, indent: int = 4):
    """
    Serializes an ElspotResponse object and saves it to a JSON file.
    Pydantic-modeller har en indbygget .json() metode, der konverterer til en JSON-streng.
    """
    with open(json_path, 'w', encoding='utf-8') as f:
        # .json() metoden klarer konverteringen. Vi skriver bare strengen til filen.
        f.write(response_data.json(indent=indent, ensure_ascii=False))

# Eksempel på brug (kan køres for at teste)
if __name__ == '__main__':
    # Sti til din JSON-fil
    input_json_path = 'elpris-raw.json'
    output_json_path = 'elpris-pydantic-output.json'

    print(f"Indlæser data fra '{input_json_path}' med Pydantic...")
    elspot_data = load_elspot_response_from_json(input_json_path)

    if elspot_data.records:
        print(f"Fandt {len(elspot_data.records)} records.")
        print("Første record:", elspot_data.records[0])
        print("Type af HourUTC:", type(elspot_data.records[0].HourUTC)) # Vil være <class 'datetime.datetime'>

        print(f"\nGemmer data til '{output_json_path}'...")
        save_elspot_response_to_json(elspot_data, output_json_path)
        print("Færdig.")
