import requests
from datetime import datetime, timedelta
import pytz
from elpris.control.calculations import beregn_totalpris, juster_aar
from elpris.models.elpris_models import ElspotResponse


def hent_spotpriser(region: str, from_date_time: datetime = None, to_date_time: datetime = None) -> requests.Response | None:
    """Henter strømpriser i en given periode for en given region. Perioden er i UTC tid for nu

    Args:
        region (str): Region streng
        from_date_time (datetime, optional): Fra tidspunkt. Defaults to datetime.now().
        to_date_time (datetime, optional): Til tidspunkt. Defaults to datetime.now()+timedelta(days=1).

    Returns:
        Response: Et Request response objekt
    """
    if from_date_time is None:
        from_date_time = juster_aar(datetime.now())
            
    if to_date_time is None:
        to_date_time = from_date_time + timedelta(days=1)
        
    # Koknverter region til Uppercase. 
    price_area = region.upper()
    
    try:
        # API-kald til Energinet
        url = "https://api.energidataservice.dk/dataset/Elspotprices"
        params = {
            'start': from_date_time.strftime('%Y-%m-%d'),
            'end': to_date_time.strftime('%Y-%m-%d'),
            'filter': f'{{"PriceArea":"{price_area}"}}',
            'sort': 'HourDK'
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json().get('records', [])
            
            if not data:
                raise ValueError(f"Ingen prisdata modtaget fra API'et for region {region}")
                
            return response
        else:
            raise Exception(f"Fejl ved hentning af data: {response.status_code}")
    except Exception as e:
        print(f"Der opstod en fejl: {e}")
        return None

def hent_stroem_priser(region: str) -> list[dict] | None:
    """Henter strømpriser fra Energinet API og beregner slutpriser med afgifter."""
    try:
        response = hent_spotpriser(region)
        if response is None:
            return None

        json_data = response.json()
        elspot_response = ElspotResponse(**json_data)

        resultater = []
        for record in elspot_response.records:
            pris_data = beregn_totalpris(record.SpotPriceDKK, record.HourDK)
            pris_data["price_area"] = record.PriceArea
            resultater.append(pris_data)

        return resultater
    except Exception as e:
        print(f"Der opstod en fejl: {e}")
        return None
