from datetime import date, datetime
from enum import StrEnum
from pydantic import BaseModel
from tzlocal import get_localzone

class PriceArea(StrEnum):
    DK1 = "DK1"
    DK2 = "DK2"
  
    
    """
    
    
        params = {
            'start': datetime.now(pytz.timezone('Europe/Copenhagen')).strftime('%Y-%m-%d'),
            'end': (datetime.now(pytz.timezone('Europe/Copenhagen')) + timedelta(days=1)).strftime('%Y-%m-%d'),
            'filter': f'{{"PriceArea":"{price_area}"}}',
            'sort': 'HourDK'
        }
    
    """


class Energinet(BaseModel):
    str : url = "https://api.energidataservice.dk/dataset/Elspotprices"
    datetime : start
    datetime : end
    PriceArea : price_area
    str : sort

    @field_serializer('start')
    def serialize_from_date_time(self, from_dt : datetime) -> str:
        return from_dt.strftime('%Y-%m-%d')
    
    # Vi skal også have lavet en serializer for to_date_time
    # .model_dump() vil lave vores model om til et dictionary

    @classmethod
    def create_now(cls) -> Energinet:
        """Creates an instance for the user at the users local timezone

        Returns:
            Energinet: A Instance of a Energinet model
        """

        #Den aktuelle tidszone for brugeren
        tz = get_localzone()

        #Opret en datetime med aktuel tidszone
        current_time = datetime.now(tz)

        #Vi skal have udfyldt vores instans. 
        return cls(
            start=current_time,
            end=current_time + timedelta(days=1),
            price_area=PriceArea.DK1,
            sort='HourDK'
        )
        
