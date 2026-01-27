import pytest
from elpris.models.taxes import TaxAndFees

def test_tax_and_fees_default_values():
    tariffs = TaxAndFees()
    assert tariffs.get_moms_rate() == 0.25
    assert tariffs.get_elafgift() == 0.699 * 2
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
