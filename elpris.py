import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pytz
import pandas as pd
import matplotlib.dates as mdates
import argparse

'''
# Tilføj afgifter (dette er eksempelværdier - brug aktuelle satser)
            moms_rate = 0.25  # 25% moms
            elafgift = 0.72  # kr/kWh (eksempelværdi)
            systemtarif = 0.050  # kr/kWh (eksempelværdi)
            nettarif = 0.43  # kr/kWh (eksempelværdi)
            transmis_tarif = 0.07 # Har vi fundet ud af vi app
'''

class TaxAndFees:
    """
    A class to encapsulate electricity taxes and fees.
    """

    def __init__(self, moms_rate=0.25, elafgift=0.699, systemtarif=0.054, nettarif=0.213, trans_tarif=0.07):
        """
        Initializes the TaxAndFees object with the given tax and fee rates.

        Args:
            moms_rate (float): The VAT rate (default: 0.25).
            elafgift (float): The electricity tax rate in kr/kWh (default: 0.699).
            systemtarif (float): The system tariff rate in kr/kWh (default: 0.054).
            nettarif (float): The network tariff rate in kr/kWh (default: 0.213).
        """
        self._moms_rate = moms_rate
        self._elafgift = elafgift
        self._systemtarif = systemtarif
        self._nettarif = nettarif
        self._trans_tarif = trans_tarif

    def get_moms_rate(self):
        """
        Returns the VAT rate.

        Returns:
            float: The VAT rate.
        """
        return self._moms_rate

    def get_elafgift(self):
        """
        Returns the electricity tax rate.

        Returns:
            float: The electricity tax rate in kr/kWh.
        """
        return self._elafgift * 2

    def get_systemtarif(self):
        """
        Returns the system tariff rate.

        Returns:
            float: The system tariff rate in kr/kWh.
        """
        return self._systemtarif

    def get_nettarif(self, charge_time: pd.Timestamp = None):
        """
        Returns the network tariff rate in øre/kWh based on month and hour.
        """
        if charge_time is None:
            return self._nettarif  # fallback

        # Define winter months (October to March)
        winter_months = [10, 11, 12, 1, 2, 3]

        # Det kan være en god ide selv at definere variablerne
        # så vi får hjælp af kode værktøjet 
        low_hour_tariff : float = 0.0
        high_hour_tariff : float = 0.0
        peak_hour_tariff : float = 0.0

        if charge_time.month in winter_months:
            # Winter tariffs (in øre/kWh)
            low_hour_tariff = 5.17
            high_hour_tariff = 15.50
            peak_hour_tariff = 46.49
        else:
            # Summer tariffs (in øre/kWh)
            low_hour_tariff = 5.17
            high_hour_tariff = 7.74
            peak_hour_tariff = 20.14

        # Define hour ranges
        hour = charge_time.hour
        
        if 17 <= hour <= 21:
            return peak_hour_tariff / 100  # convert to kr/kWh
        elif (6 <= hour < 17) or (21 < hour <= 23):
            return high_hour_tariff / 100
        else:
            return low_hour_tariff / 100
    
    def get_transmis_tarif(self):
        """
        Returns the transmision tariff rate.

        Returns:
            float: The network transmission tariff rate in kr/kWh.
        """
        return self._trans_tarif

    def add_tarrifs(self, charge : float, charge_time : pd.Timestamp) -> float:
        """_summary_

        Args:
            charge (float): _description_
            charge_time (pd.Timestamp): _description_

        Returns:
            float: _description_
        """
        return charge + self._elafgift + self._systemtarif + self._nettarif + self._trans_tarif

    def add_taxes(self, carge_ex_tax) -> float:

        return carge_ex_tax * (1 + self._moms_rate)
    
    

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

def round_down_to_hour(dt: datetime) -> datetime:    
    """
    Denne funktion runder et datetime-objekt ned til den nærmeste hele time


    Args:
        dt (datetime): The datetime object to round down.

    Returns:
        datetime: A new datetime object rounded down to the nearest hour.
    """
    return dt.replace(minute=0, second=0, microsecond=0)

def apply_taxes(df : pd.DataFrame) -> pd.DataFrame:
    """Metoden retter dataframe med elpriser så der kommer data inklusiv afgifter

    Args:
        df (pd.DataFrame): Pandas dataframe

    Returns:
        pd.DataFrame: Pandas dataframe med afgifter. 
    """

    # Afgifts objekt
    tariffs = TaxAndFees()   
    
    #df['HourDK'] = pd.to_datetime(df['HourDK'])
    df['HourDK'] = pd.to_datetime(df['HourDK'], utc=True).dt.tz_convert('Europe/Copenhagen')
    
    # Konvertér øre/kWh til kr/kWh (SpotPriceDKK er i kr/MWh)
    df['SpotPriceDKK_kWh'] = df['SpotPriceDKK'] / 1000
    
    # # Beregn total pris inklusive afgifter
    # df['TotalPris'] = df['SpotPriceDKK_kWh'] + elafgift + systemtarif + nettarif + transmis_tarif
    df['TotalPris'] = tariffs.add_tarrifs(df['SpotPriceDKK_kWh'])
    # df['TotalPrisMedMoms'] = df['TotalPris'] * (1 + moms_rate)
    df['TotalPrisMedMoms'] = tariffs.add_taxes(df['TotalPris'])

    return df

def hent_stroem_priser(region : str) -> pd.DataFrame | None:
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
            
            df = apply_taxes(df)

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
    #aktuel_time = nu.replace(minute=0, second=0, microsecond=0)

    # Vi laver aktuel time om til en Pandas timestamp da det er den der slås op med i dataframen nedenfor. 
    aktuel_time_dt = round_down_to_hour(nu)
    aktuel_time = pd.Timestamp(aktuel_time_dt) 
        
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