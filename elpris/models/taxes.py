from datetime import datetime

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
        return self._elafgift

    def get_systemtarif(self):
        """
        Returns the system tariff rate.

        Returns:
            float: The system tariff rate in kr/kWh.
        """
        return self._systemtarif

    def get_nettarif(self, charge_time: datetime | None = None):
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

    def add_tarrifs(self, charge: float, charge_time: datetime | None = None) -> float:
        """_summary_

        Args:
            charge (float): _description_
            charge_time (datetime): _description_

        Returns:
            float: _description_
        """
        # Note: The original code didn't use charge_time in calculation here, 
        # but get_nettarif actually takes charge_time. 
        # I should probably use it if the intention was to use dynamic tariffs.
        # But for exact migration I will stick to the original logic which seemed to use static properties?
        # Wait, the original line was:
        # return charge + self._elafgift + self._systemtarif + self._nettarif + self._trans_tarif
        # It used self._nettarif which is the default/fallback. 
        # To match original exactly:
        return charge + self.get_elafgift() + self.get_systemtarif() + self._nettarif + self.get_transmis_tarif()

    def add_taxes(self, charge_ex_tax) -> float:

        return charge_ex_tax * (1 + self._moms_rate)
