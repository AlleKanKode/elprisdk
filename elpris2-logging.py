import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pytz
import pandas as pd
import matplotlib.dates as mdates
import argparse
import logging
import json

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_arguments():
    """Håndterer kommandolinjeargumenter."""
    logger.info("Parsing command line arguments")
    parser = argparse.ArgumentParser(description='Hent og vis strømpriser for Danmark.')
    parser.add_argument('--region', type=str, choices=['dk1', 'dk2'], default='dk1',
                        help='Vælg region: dk1 (Vestdanmark) eller dk2 (Østdanmark)')
    parser.add_argument('--output', type=str, default='strompriser_dag.png',
                        help='Filnavn for den gemte graf')
    parser.add_argument('--no-show', action='store_true',
                        help='Undlad at vise grafen interaktivt (kun gem den)')
    args = parser.parse_args()
    logger.info(f"Arguments parsed: region={args.region}, output={args.output}, no_show={args.no_show}")
    return args

def hent_stroem_priser(region):
    """Henter strømpriser fra Energinet API og beregner slutpriser med afgifter."""
    logger.info(f"Fetching electricity prices for region: {region}")
    price_area = region.upper()
    
    try:
        url = "https://api.energidataservice.dk/dataset/Elspotprices"
        now = datetime.now(pytz.timezone('Europe/Copenhagen'))
        params = {
            'start': now.strftime('%Y-%m-%d'),
            'end': (now + timedelta(days=1, hours=1)).strftime('%Y-%m-%d'),
            'filter': json.dumps({"PriceArea": [price_area]})
        }
        
        logger.debug(f"Making API request to {url} with params: {params}")
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json().get('records', [])
            if not data:
                logger.warning(f"No price data received from API for region {region}")
                raise ValueError(f"Ingen prisdata modtaget fra API'et for region {region}")
            
            logger.info(f"Successfully fetched {len(data)} price records")
            df = pd.DataFrame(data)
            df['HourDK'] = pd.to_datetime(df['HourDK']).dt.tz_localize(None)
            
            # Calculations...
            df['SpotPriceDKK_kWh'] = df['SpotPriceDKK'].astype(float) / 1000
            
            moms_rate = 0.25
            elafgift = 0.699
            systemtarif = 0.054
            nettarif = 0.213
            
            df['TotalPris'] = df['SpotPriceDKK_kWh'] + elafgift + systemtarif + nettarif
            df['TotalPrisMedMoms'] = df['TotalPris'] * (1 + moms_rate)
            
            logger.debug("Price calculations completed")
            return df
        else:
            logger.error(f"API request failed with status code: {response.status_code}")
            raise Exception(f"Fejl ved hentning af data: {response.status_code}")
    except Exception as e:
        logger.exception(f"An error occurred while fetching electricity prices: {e}")
        return None
    finally:
        logger.info("Finished attempting to fetch electricity prices")

def vis_aktuel_pris_og_graf(region, output_filename, show_plot=True):
    """Viser den aktuelle strømpris og en graf over dagens priser."""
    logger.info(f"Visualizing current price and graph for region: {region}")
    region_names = {'dk1': 'Vestdanmark', 'dk2': 'Østdanmark'}
    region_name = region_names.get(region.lower(), region)
    
    df = hent_stroem_priser(region)
    
    if df is None or df.empty:
        logger.error("Failed to retrieve price data, aborting visualization")
        return
    
    try:
        # Get the current time in Copenhagen timezone and make it naive
        nu = datetime.now(pytz.timezone('Europe/Copenhagen')).replace(tzinfo=None)
        
        # Round down to the nearest hour
        aktuel_time = nu.replace(minute=0, second=0, microsecond=0)
        
        # Find the closest hour in the data
        closest_hour = min(df['HourDK'], key=lambda x: abs(x - aktuel_time))
        aktuel_pris_række = df[df['HourDK'] == closest_hour]
        
        if not aktuel_pris_række.empty:
            aktuel_pris = aktuel_pris_række['TotalPrisMedMoms'].values[0]
            logger.info(f"Closest electricity price in {region_name} (for {closest_hour}): {aktuel_pris:.2f} kr/kWh")
            print(f"Nærmeste strømpris i {region_name} (for {closest_hour}): {aktuel_pris:.2f} kr/kWh (inkl. alle afgifter og moms)")
        else:
            logger.warning(f"Could not find a close price for {region_name}")
            print(f"Kunne ikke finde en nær pris for {region_name}.")
        
        logger.info("Creating price graph")
        plt.figure(figsize=(12, 6))
        plt.plot(df['HourDK'], df['TotalPrisMedMoms'], marker='o', linestyle='-', color='#1f77b4')
        
        if not aktuel_pris_række.empty:
            plt.axvline(x=closest_hour, color='r', linestyle='--', alpha=0.7, label='Nærmeste tidspunkt')
            plt.plot(closest_hour, aktuel_pris, 'ro', markersize=8)
        
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
        
        plt.xticks(rotation=45)
        
        plt.title(f'Strømpriser i {region_name} (inkl. alle afgifter og moms)')
        plt.xlabel('Tidspunkt')
        plt.ylabel('Pris (kr/kWh)')
        plt.grid(True, alpha=0.3)
        plt.legend(['Strømpris', 'Nærmeste tidspunkt'])
        plt.tight_layout()
        
        logger.info(f"Saving graph to file: {output_filename}")
        plt.savefig(output_filename, dpi=300)
        print(f"Graf over dagens strømpriser er gemt som '{output_filename}'")
        
        if show_plot:
            logger.info("Displaying graph")
            plt.show()
        else:
            logger.info("Skipping graph display (--no-show option used)")
    except Exception as e:
        logger.exception(f"An error occurred while creating or saving the graph: {e}")
    finally:
        plt.close()  # Ensure the plot is closed even if an exception occurs
        logger.info("Finished visualization process")

if __name__ == "__main__":
    logger.info("Script started")
    try:
        args = parse_arguments()
        vis_aktuel_pris_og_graf(
            region=args.region, 
            output_filename=args.output,
            show_plot=not args.no_show
        )
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
    finally:
        logger.info("Script completed")
