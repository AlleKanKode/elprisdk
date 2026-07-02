import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Tilføj projekt-roden til sys.path så elpris-pakken kan importeres
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from elpris.control.spot_prices import hent_spotpriser
from elpris.control.calculations import juster_aar

def main():
    parser = argparse.ArgumentParser(
        description="Hent strømpriser fra Energinet API og gem som JSON"
    )
    parser.add_argument(
        "--region", default="dk1", choices=["dk1", "dk2"],
        help="Prisområde (default: dk1)"
    )
    parser.add_argument(
        "--output", type=str,
        help="Output filsti (default: data/elspot_{region}.json)"
    )
    parser.add_argument(
        "--date", type=str,
        help="Dato for hentning (YYYY-MM-DD). Default: i går"
    )
    args = parser.parse_args()

    if args.date:
        from_date = datetime.strptime(args.date, "%Y-%m-%d")
    else:
        from_date = juster_aar(datetime.now() - timedelta(days=1))

    to_date = from_date + timedelta(days=1)
    output = args.output or f"data/elspot_{args.region}.json"

    print(
        f"Henter strømpriser for {args.region.upper()} "
        f"fra {from_date.date()} til {to_date.date()}..."
    )

    response = hent_spotpriser(args.region, from_date, to_date)

    if response is None:
        print("Fejl: Kunne ikke hente data fra Energinet API", file=sys.stderr)
        sys.exit(1)

    data = response.json()

    with open(output, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    records_count = len(data.get("records", []))
    print(f"Gemt {records_count} records til {output}")


if __name__ == "__main__":
    main()
