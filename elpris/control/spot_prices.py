import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz
from elpris.control.calculations import apply_taxes

def hent_spotpriser(region : str, from_date_time : datetime = None, to_date_time : datetime = None) -> requests.Response | None:
    """Henter strømpriser i en given periode for en given region. Perioden er i UTC tid for nu

    Args:
        region (str): Region streng
        from_date_time (datetime, optional): Fra tidspunkt. Defaults to datetime.now().
        to_date_time (datetime, optional): Til tidspunkt. Defaults to datetime.now()+timedelta(days=1).

    Returns:
        Response: Et Request response objekt
    """
    if from_date_time is None:
        from_date_time = datetime.now()
        # WORKAROUND: System time is 2026, but API has no data. Map 2026 to 2025.
        if from_date_time.year == 2026:
            from_date_time = from_date_time.replace(year=2025)
            
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

def hent_stroem_priser(region : str) -> pd.DataFrame | None:
    """Henter strømpriser fra Energinet API og beregner slutpriser med afgifter."""
    # Konverter region til korrekt format for API
    price_area = region.upper()
    
    try:
        # API-kald til Energinet
        url = "https://api.energidataservice.dk/dataset/Elspotprices"
        start_date = datetime.now(pytz.timezone('Europe/Copenhagen'))
        # WORKAROUND: System time is 2026, but API has no data. Map 2026 to 2025.
        if start_date.year == 2026:
            start_date = start_date.replace(year=2025)
            
        end_date = start_date + timedelta(days=1)

        params = {
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d'),
            'filter': f'{{"PriceArea":"{price_area}"}}',
            'sort': 'HourDK'
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json().get('records', [])
            if not data:
                raise ValueError(f"Ingen prisdata modtaget fra API'et for region {region}")
                
            # Konvertér til pandas DataFrame for nemmere databehandling
            df = pd.DataFrame(data)
            
            df = apply_taxes(df)

            return df
        else:
            raise Exception(f"Fejl ved hentning af data: {response.status_code}")
    except Exception as e:
        print(f"Der opstod en fejl: {e}")
        return None
