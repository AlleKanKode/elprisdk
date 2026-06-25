from datetime import datetime
from elpris.models.taxes import TaxAndFees


def round_down_to_hour(dt: datetime) -> datetime:
    return dt.replace(minute=0, second=0, microsecond=0)


def beregn_totalpris(spot_price_dkk_per_mwh: float, hour_dk: datetime) -> dict:
    """Beregner totalpris for en enkelt timepost inkl. alle afgifter.

    Args:
        spot_price_dkk_per_mwh: Spotpris i kr/MWh (som API'et returnerer).
        hour_dk: Tidspunkt i dansk tid (bruges til tidsafhængig nettarif).

    Returns:
        dict med spotpris, afgifter og totalpris inkl. moms.
    """
    tariffs = TaxAndFees()

    spotpris_kwh = spot_price_dkk_per_mwh / 1000
    elafgift = tariffs.get_elafgift()
    systemtarif = tariffs.get_systemtarif()
    nettarif = tariffs.get_nettarif(hour_dk)
    transmissionstarif = tariffs.get_transmis_tarif()

    total_ex_moms = spotpris_kwh + elafgift + systemtarif + nettarif + transmissionstarif
    total_med_moms = tariffs.add_taxes(total_ex_moms)
    moms = total_med_moms - total_ex_moms

    return {
        "hour_dk": hour_dk,
        "spotpris_kwh": spotpris_kwh,
        "elafgift": elafgift,
        "systemtarif": systemtarif,
        "nettarif": nettarif,
        "transmissionstarif": transmissionstarif,
        "total_ex_moms": total_ex_moms,
        "moms": moms,
        "total_med_moms": total_med_moms,
    }
