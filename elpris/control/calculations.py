import pandas as pd
from datetime import datetime
from elpris.models.taxes import TaxAndFees

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
    df['TotalPris'] = tariffs.add_tarrifs(df['SpotPriceDKK_kWh'], df['HourDK']) # Note: add_tarrifs signature in models/taxes.py only uses charge for now in body, but I kept args
    # But wait, in taxes.py I kept: def add_tarrifs(self, charge : float, charge_time : pd.Timestamp) -> float:
    # And implementation: return charge + self._elafgift + self._systemtarif + self._nettarif + self._trans_tarif
    
    # Use tariffs.add_tarrifs correctly. It expects float and Timestamp.
    # But here we are operating on Series. 
    # The original correct code was: df['TotalPris'] = tariffs.add_tarrifs(df['SpotPriceDKK_kWh']) 
    # WAIT. The original code in elpris.py had:
    # df['TotalPris'] = tariffs.add_tarrifs(df['SpotPriceDKK_kWh'])
    # BUT the definition of add_tarrifs in elpris.py was:
    # def add_tarrifs(self, charge : float, charge_time : pd.Timestamp) -> float:
    # So the original code was confusing/maybe broken if run? 
    # Let's check elpris.py again. Step 13.
    # Line 113: def add_tarrifs(self, charge : float, charge_time : pd.Timestamp) -> float:
    # Line 176: df['TotalPris'] = tariffs.add_tarrifs(df['SpotPriceDKK_kWh'])
    # This implies that `add_tarrifs` was being called with only one argument!
    # And Python would error if `charge_time` is mandatory.
    # Ah, but line 113 has type hints but no defaults?
    # Wait, in Step 13: `def add_tarrifs(self, charge : float, charge_time : pd.Timestamp) -> float:`
    # It does NOT have a default value for charge_time.
    # So the original code `df['TotalPris'] = tariffs.add_tarrifs(df['SpotPriceDKK_kWh'])` would FAIL with mismatched arguments.
    # UNLESS... python allows missing args? No.
    # Maybe I should fix this bug? Or maybe I misread the file content?
    # Let's check if the method is used properly.
    # The user wants "best compliance". Breaking the code is bad. Fixing it is good.
    # I'll modify `add_tarrifs` in `taxes.py` locally to make sure it handles Series or scalar, or I adjust the call here.
    # Since this is a refactor, I should probably stick to what logic implies.
    # `add_tarrifs` seems to just add constants. 
    # `add_taxes` uses simple multiplication.
    # I will stick to what the original code likely intended but maybe `add_tarrifs` *should* have had a default or be robust?
    # Or maybe the original code was never run successfully? 
    # I will modify `calculations.py` to just call it as it was (with one arg) BUT I need to fix `taxes.py` to allow optional `charge_time` or fix the call.
    # In my `taxes.py` I wrote: `def add_tarrifs(self, charge : float, charge_time : pd.Timestamp) -> float:`
    # I should update `taxes.py` to make `charge_time` optional if I want to support the existing call, or update the call here.
    # Updating the call here is harder because we are passing a Series (`df[...]`). 
    # Passing a Series to a function expecting float might work if pandas broadcasting handles it, but the second arg `charge_time` is missing.
    # I will assume the intention was to support the call. 
    # I'll update `taxes.py` to make `charge_time` optional = None. 
    
    # df['TotalPrisMedMoms'] = tariffs.add_taxes(df['TotalPris'])
    df['TotalPrisMedMoms'] = tariffs.add_taxes(df['TotalPris'])

    return df
