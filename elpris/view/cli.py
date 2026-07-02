import argparse
from datetime import datetime
import pytz
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from elpris.control.calculations import round_down_to_hour, juster_aar
from elpris.control.spot_prices import hent_stroem_priser

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

def vis_aktuel_pris_og_graf(region, output_filename, show_plot=True):
    """Viser den aktuelle strømpris og en graf over dagens priser."""
    region_names = {'dk1': 'Vestdanmark', 'dk2': 'Østdanmark'}
    region_name = region_names.get(region.lower(), region)

    resultater = hent_stroem_priser(region)

    if resultater is None:
        return

    df = pd.DataFrame(resultater)

    # Find nuværende time
    nu = juster_aar(datetime.now(pytz.timezone('Europe/Copenhagen')))

    aktuel_time_dt = round_down_to_hour(nu)
    aktuel_time = aktuel_time_dt

    # Find den aktuelle pris
    aktuel_række = df[df['hour_dk'] == aktuel_time]
    if not aktuel_række.empty:
        aktuel_pris = aktuel_række['total_med_moms'].values[0]
        print(f"Aktuel strømpris i {region_name}: {aktuel_pris:.2f} kr/kWh (inkl. alle afgifter og moms)")
    else:
        print(f"Kunne ikke finde den aktuelle pris for {region_name}.")

    # Plot graf over dagens priser
    plt.figure(figsize=(12, 6))
    plt.plot(df['hour_dk'], df['total_med_moms'], marker='o', linestyle='-', color='#1f77b4')

    # Marker nuværende tidspunkt
    if not aktuel_række.empty:
        plt.axvline(x=aktuel_time, color='r', linestyle='--', alpha=0.7, label='Nuværende tidspunkt')
        plt.plot(aktuel_time, aktuel_pris, 'ro', markersize=8)

    # Formatér x-aksen til at vise timer hver time
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M', tz=pytz.timezone('Europe/Copenhagen')))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))

    # Rotér x-aksens etiketter for bedre læsbarhed
    plt.xticks(rotation=45)

    plt.title(f'Strømpriser i {region_name} (inkl. alle afgifter og moms)')
    plt.xlabel('Tidspunkt')
    plt.ylabel('Pris (kr/kWh)')
    plt.grid(True, alpha=0.3)
    plt.legend(['Strømpris', 'Nuværende tidspunkt'])
    plt.tight_layout()

    # Gem grafen
    plt.savefig(output_filename, dpi=300)
    print(f"Graf over dagens strømpriser er gemt som '{output_filename}'")

    # Vis grafen hvis ønsket
    if show_plot:
        plt.show()
