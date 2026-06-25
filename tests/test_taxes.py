import pytest
from datetime import datetime
from elpris.models.taxes import TaxAndFees
from elpris.control.calculations import beregn_totalpris

def test_tax_and_fees_default_values():
    tariffs = TaxAndFees()
    assert tariffs.get_moms_rate() == 0.25
    assert tariffs.get_elafgift() == 0.699
    assert tariffs.get_systemtarif() == 0.054
    assert tariffs.get_transmis_tarif() == 0.07

def test_add_tarrifs():
    tariffs = TaxAndFees()
    charge = 1.0
    # Expected: 1.0 + 0.699 + 0.054 + 0.213 + 0.07 = 2.036
    # Note: elafgift in init is 0.699, but calculation uses _elafgift directly.
    # In __init__: self._elafgift = elafgift.
    # In add_tarrifs: return charge + self._elafgift + ...
    # Wait, in get_elafgift() it returns self._elafgift * 2. 
    # But add_tarrifs uses self._elafgift directly. 
    # This might be a logic "bug" or feature in original code, I preserved it.
    # Let's calculate what `add_tarrifs` does based on code:
    # 1.0 + 0.699 + 0.054 + 0.213 + 0.07 = 2.036
    expected = 1.0 + 0.699 + 0.054 + 0.213 + 0.07
    assert tariffs.add_tarrifs(charge) == pytest.approx(expected)

def test_add_taxes():
    tariffs = TaxAndFees()
    amount = 100.0
    # 100 * 1.25 = 125.0
    assert tariffs.add_taxes(amount) == 125.0


def test_get_nettarif_sommer_lav():
    tariffs = TaxAndFees()
    # Juli kl. 02:00 -> lav tarif (5.17 øre = 0.0517 kr)
    t = datetime(2025, 7, 15, 2, 0, 0)
    assert tariffs.get_nettarif(t) == pytest.approx(0.0517)


def test_get_nettarif_sommer_hoj():
    tariffs = TaxAndFees()
    # Juni kl. 10:00 -> høj tarif (7.74 øre = 0.0774 kr)
    t = datetime(2025, 6, 20, 10, 0, 0)
    assert tariffs.get_nettarif(t) == pytest.approx(0.0774)


def test_get_nettarif_sommer_peak():
    tariffs = TaxAndFees()
    # Juni kl. 18:00 -> peak tarif (20.14 øre = 0.2014 kr)
    t = datetime(2025, 6, 20, 18, 0, 0)
    assert tariffs.get_nettarif(t) == pytest.approx(0.2014)


def test_get_nettarif_vinter_peak():
    tariffs = TaxAndFees()
    # Oktober kl. 18:00 -> peak tarif (46.49 øre = 0.4649 kr)
    t = datetime(2025, 10, 15, 18, 0, 0)
    assert tariffs.get_nettarif(t) == pytest.approx(0.4649)


def test_get_nettarif_vinter_lav():
    tariffs = TaxAndFees()
    # Januar kl. 03:00 -> lav tarif (5.17 øre = 0.0517 kr)
    t = datetime(2025, 1, 10, 3, 0, 0)
    assert tariffs.get_nettarif(t) == pytest.approx(0.0517)


def test_get_nettarif_ingen_tid():
    tariffs = TaxAndFees()
    # Uden tid -> fallback (0.213)
    assert tariffs.get_nettarif(None) == pytest.approx(0.213)


def test_beregn_totalpris_sommer_lav():
    # Spotpris: 500 kr/MWh = 0.5 kr/kWh
    # Sommer, lav last (kl. 02:00): nettarif = 0.0517
    result = beregn_totalpris(500.0, datetime(2025, 7, 15, 2, 0, 0))
    assert result["spotpris_kwh"] == pytest.approx(0.5)
    assert result["elafgift"] == pytest.approx(0.699)
    assert result["systemtarif"] == pytest.approx(0.054)
    assert result["nettarif"] == pytest.approx(0.0517)
    assert result["transmissionstarif"] == pytest.approx(0.07)
    # 0.5 + 0.699 + 0.054 + 0.0517 + 0.07 = 1.3747
    assert result["total_ex_moms"] == pytest.approx(1.3747)
    # moms = 1.3747 * 0.25 = 0.343675
    assert result["moms"] == pytest.approx(0.343675)
    # total = 1.3747 + 0.343675 = 1.718375
    assert result["total_med_moms"] == pytest.approx(1.718375)


def test_beregn_totalpris_sommer_peak():
    # Spotpris: 1000 kr/MWh = 1.0 kr/kWh
    # Sommer, peak (kl. 18:00): nettarif = 0.2014
    result = beregn_totalpris(1000.0, datetime(2025, 6, 20, 18, 0, 0))
    assert result["spotpris_kwh"] == pytest.approx(1.0)
    assert result["nettarif"] == pytest.approx(0.2014)
    # 1.0 + 0.699 + 0.054 + 0.2014 + 0.07 = 2.0244
    assert result["total_ex_moms"] == pytest.approx(2.0244)
    assert result["total_med_moms"] == pytest.approx(2.0244 * 1.25)


def test_beregn_totalpris_negativ_spot():
    # Spotpris: -100 kr/MWh = -0.1 kr/kWh (negativ elpris forekommer)
    result = beregn_totalpris(-100.0, datetime(2025, 6, 20, 14, 0, 0))
    assert result["spotpris_kwh"] == pytest.approx(-0.1)
    # Total kan stadig være positiv pga. afgifter
    assert result["total_med_moms"] > 0
