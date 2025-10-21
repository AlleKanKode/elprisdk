from datetime import datetime
from typing import List
from enum import Enum
from pydantic import BaseModel


class PriceArea(str, Enum):
    DK1 = "DK1"
    DK2 = "DK2"

class ElspotRecord(BaseModel):
    """
    Pydantic model for a single electricity price record.
    Felter er med store bogstaver for at matche JSON-data direkte.
    Pydantic håndterer automatisk konvertering fra JSON-typer til Python-typer.
    """
    HourUTC: datetime
    HourDK: datetime
    PriceArea: PriceArea
    SpotPriceDKK: float
    SpotPriceEUR: float

    # Ingen grund til from_dict eller to_dict - Pydantic klarer det.


class ElspotResponse(BaseModel):
    """Pydantic model for the entire API response from Energinet Elspotprices."""
    total: int
    dataset: str
    sort: str
    filters: str
    records: List[ElspotRecord] 

    # Pydantic vil automatisk bruge ElspotRecord-modellen til at parse
    # hvert element i 'records'-listen.
