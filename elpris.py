import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pytz
import pandas as pd
import matplotlib.dates as mdates
import argparse

def parse_arguments():
    """Håndterer kommandolinjeargumenter."""
    parser = argparse.ArgumentParser(description='Hent og vis strømpriser for Danmark.')
    parser.add_argument('--region', type=str, choices=['dk1', 'dk2'], default='dk1',
                        help='Vælg region: dk1 (Vestdanmark) eller dk2 (Østdanmark)')
    parser.add_argument('--output', type=str, default='strompriser_dag.png',
                        help='Filnavn for den gemte graf')
    parser.add_argument('--no-show', action='store_true',
                        help='Undlad at vise grafen interaktivt (kun gem den)')
    return parser.parse_args()

def hent_stroem_priser(region):
    """Henter strømpriser fra Energinet API og beregner slutpriser med afgifter."""
    # Konverter region til korrekt format for API
    price_area = region.upper()
    
    try:
        # API-kald til Energinet
        url = "https://api.energidataservice.dk/dataset/Elspotprices"
        params = {
            'start': datetime.now(pytz.timezone('Europe/Copenhagen')).strftime('%Y-%m-%d'),
            'end': (datetime.now(pytz.timezone('Europe/Copenhagen')) + timedelta(days=1)).strftime('%Y-%m-%d'),
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
            df['HourDK'] = pd.to_datetime(df['HourDK'])
            
            # Konvertér øre/kWh til kr/kWh (SpotPriceDKK er i kr/MWh)
            df['SpotPriceDKK_kWh'] = df['SpotPriceDKK'] / 1000
            
            # Tilføj afgifter (dette er eksempelværdier - brug aktuelle satser)
            moms_rate = 0.25  # 25% moms
            elafgift = 0.699  # kr/kWh (eksempelværdi)
            systemtarif = 0.054  # kr/kWh (eksempelværdi)
            nettarif = 0.213  # kr/kWh (eksempelværdi)
            
            # Beregn total pris inklusive afgifter
            df['TotalPris'] = df['SpotPriceDKK_kWh'] + elafgift + systemtarif + nettarif
            df['TotalPrisMedMoms'] = df['TotalPris'] * (1 + moms_rate)
            
            return df
        else:
            raise Exception(f"Fejl ved hentning af data: {response.status_code}")
    except Exception as e:
        print(f"Der opstod en fejl: {e}")
        return None

def vis_aktuel_pris_og_graf(region, output_filename, show_plot=True):
    """Viser den aktuelle strømpris og en graf over dagens priser."""
    region_names = {'dk1': 'Vestdanmark', 'dk2': 'Østdanmark'}
    region_name = region_names.get(region.lower(), region)
    
    df = hent_stroem_priser(region)
    
    if df is None:
        return
    
    # Find nuværende time
    nu = datetime.now(pytz.timezone('Europe/Copenhagen'))
    aktuel_time = nu.replace(minute=0, second=0, microsecond=0)
    
    # Find den aktuelle pris
    aktuel_pris_række = df[df['HourDK'] == aktuel_time]
    if not aktuel_pris_række.empty:
        aktuel_pris = aktuel_pris_række['TotalPrisMedMoms'].values[0]
        print(f"Aktuel strømpris i {region_name}: {aktuel_pris:.2f} kr/kWh (inkl. alle afgifter og moms)")
    else:
        print(f"Kunne ikke finde den aktuelle pris for {region_name}.")
    
    # Plot graf over dagens priser
    plt.figure(figsize=(12, 6))
    plt.plot(df['HourDK'], df['TotalPrisMedMoms'], marker='o', linestyle='-', color='#1f77b4')
    
    # Marker nuværende tidspunkt
    if not aktuel_pris_række.empty:
        plt.axvline(x=aktuel_time, color='r', linestyle='--', alpha=0.7, label='Nuværende tidspunkt')
        plt.plot(aktuel_time, aktuel_pris, 'ro', markersize=8)
    
    # Formatér x-aksen til at vise timer hver time
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M', tz=pytz.timezone('Europe/Copenhagen')))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))  # Ændret fra 2 til 1 for at vise hver time
    
    # Rotér x-aksens etiketter for bedre læsbarhed
    plt.xticks(rotation=45)
    
    plt.title(f'Strømpriser i {region_name} (inkl. alle afgifter og moms)')
    plt.xlabel('Tidspunkt')
    plt.ylabel('Pris (kr/kWh)')
    plt.grid(True, alpha=0.3)
    plt.legend(['Strømpris', 'Nuværende tidspunkt'])
    plt.tight_layout()  # Sikrer god layout med roterede etiketter
    
    # Gem grafen
    plt.savefig(output_filename, dpi=300)  # Øget DPI for bedre kvalitet
    print(f"Graf over dagens strømpriser er gemt som '{output_filename}'")
    
    # Vis grafen hvis ønsket
    if show_plot:
        plt.show()

if __name__ == "__main__":
    args = parse_arguments()
    vis_aktuel_pris_og_graf(
        region=args.region, 
        output_filename=args.output,
        show_plot=not args.no_show
    )