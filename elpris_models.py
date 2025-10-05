from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any
import json

# Skrevet af terminator, ved en fejl, men det er faktisk bedre skrevet end mit eksempel pt.
# Ret jupyter filerne så det er lettere at lege med. Men dette eksempel her er faktisk ok 
# til at håndtere serialisering og deserialisering via dataclasser...

def _parse_datetime(dt_str: str) -> datetime:
    """Helper function to parse ISO format datetime strings."""
    return datetime.fromisoformat(dt_str)


@dataclass
class ElspotRecord:
    """
    Dataclass for a single electricity price record.
    Felter er med store bogstaver for at matche JSON-data direkte.
    """
    HourUTC: datetime
    HourDK: datetime
    PriceArea: str
    SpotPriceDKK: float
    SpotPriceEUR: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ElspotRecord':
        """Creates an ElspotRecord instance from a dictionary."""
        return cls(
            HourUTC=_parse_datetime(data['HourUTC']),
            HourDK=_parse_datetime(data['HourDK']),
            PriceArea=data['PriceArea'],
            SpotPriceDKK=data['SpotPriceDKK'],
            SpotPriceEUR=data['SpotPriceEUR'],
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the ElspotRecord instance to a dictionary."""
        return {
            "HourUTC": self.HourUTC.isoformat(),
            "HourDK": self.HourDK.isoformat(),
            "PriceArea": self.PriceArea,
            "SpotPriceDKK": self.SpotPriceDKK,
            "SpotPriceEUR": self.SpotPriceEUR,
        }


@dataclass
class ElspotResponse:
    """Dataclass for the entire API response from Energinet Elspotprices."""
    total: int
    dataset: str
    sort: str
    filters: str
    records: List[ElspotRecord] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ElspotResponse':
        """Creates an ElspotResponse instance from a dictionary."""
        records_data = data.get('records', [])
        return cls(
            total=data['total'],
            dataset=data['dataset'],
            sort=data['sort'],
            filters=data['filters'],
            records=[ElspotRecord.from_dict(rec) for rec in records_data]
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the ElspotResponse instance to a dictionary."""
        return {
            "total": self.total,
            "dataset": self.dataset,
            "sort": self.sort,
            "filters": self.filters,
            "records": [record.to_dict() for record in self.records]
        }

def load_elspot_response_from_json(json_path: str) -> ElspotResponse:
    """Loads and deserializes elspot data from a JSON file into dataclasses."""
    with open(json_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    return ElspotResponse.from_dict(raw_data)

def save_elspot_response_to_json(response_data: ElspotResponse, json_path: str, indent: int = 4):
    """Serializes an ElspotResponse object and saves it to a JSON file."""
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(response_data.to_dict(), f, ensure_ascii=False, indent=indent)