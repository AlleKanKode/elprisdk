
import requests
from datetime import datetime, timedelta
import pytz

def probe_api(target_date_str):
    print(f"--- Probing API for date: {target_date_str} ---")
    url = "https://api.energidataservice.dk/dataset/Elspotprices"
    # Energidataservice API expects start and end. 
    # If we want data for 'target_date_str', we need start=target_date, end=target_date+1 day
    
    start_date = datetime.strptime(target_date_str, "%Y-%m-%d")
    end_date = start_date + timedelta(days=1)
    
    params = {
        'start': start_date.strftime('%Y-%m-%d'),
        'end': end_date.strftime('%Y-%m-%d'),
        'filter': '{"PriceArea":"DK1"}',
        'sort': 'HourDK'
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json().get('records', [])
            print(f"Record Count: {len(data)}")
            if len(data) > 0:
                print("First record:", data[0])
            else:
                print("No records found.")
        else:
            print("Error response:", response.text)
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    # 1. Try "Today" according to system (2026-01-27)
    # Note: timezone is important if we use datetime.now() but here we hardcode for test.
    # System says it is 2026-01-27.
    probe_api("2026-01-27")
    
    # 2. Try a known valid past date (e.g. 2024-01-01)
    probe_api("2024-01-01")
