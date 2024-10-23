import itertools
from enums import EventStatus, PerformerType, SeatStatus, SubeventType, TicketType, VenueType
from datetime import datetime, date



###############################
# TABLES


class Ticket:
    
    id_iter = itertools.count()
    
    def __init__(self, purchase_id: int, event_id: int, ticket_type: TicketType, ticket_seat_id: int):
        self.ticket_id = next(self.id_iter)
        self.purchase_id = purchase_id
        self.event_id = event_id
        self.ticket_type = ticket_type
        self.ticket_seat_id = ticket_seat_id


class Purchase:
    
    id_iter = itertools.count()
    
    def __init__(self, purchase_id: int, customer_id: int, purchase_date: datetime, purchase_total_price: float):
        self.purchase_id = next(self.id_iter)
        self.customer_id = customer_id
        self.purchase_date = purchase_date
        self.purchase_total_price = purchase_total_price
        
        
class Customer:
    id_iter = itertools.count()
    
    def __init__(self, customer_name: str, custormer_surname: str, customer_email: str, customer_phone_number: str, customer_birth_date: date):
        self.customer_id = next(self.id_iter)
        self.customer_name = customer_name
        self.customer_surname = custormer_surname
        self.customer_email = customer_email
        self.customer_phone_number = customer_phone_number
        self.customer_birth_date = customer_birth_date


class Event:
    id_iter = itertools.count()
    
    def __init__(self, organizer_id: int, event_name: str, event_start_date: datetime, event_end_date: datetime, event_description: str, event_status: EventStatus):
        self.event_id = next(self.id_iter)
        self.organizer_id = organizer_id
        self.event_name = event_name
        self.event_start_date = event_start_date
        self.event_end_date = event_end_date
        self.event_description = self.validate_atr_length(event_description, 2000)
        self.event_status = event_status
           
    def validate_atr_length(self, atr: str, max_length: int) -> str:
        if len(atr) > max_length:
            raise ValueError(f"Atr cant be that long")
 
        
class Organizer:
    id_iter = itertools.count()
    
    def __init__(self, organizer_name: str, organizer_email: str):
        self.organizer_id = next(self.id_iter)
        self.organizer_name = organizer_name
        self.organizer_email = organizer_email
       
        
class Subevent:
    id_iter = itertools.count()
    
    def __init__(self, event_id: int, subevent_type: SubeventType, venue_id: int, performer_id: int, subevent_start_date: datetime, subevent_end_date: datetime):
        self.subevent_id = next(self.id_iter)
        self.event_id = event_id
        self.subevent_type = subevent_type
        self.venue_id = venue_id
        self.performer_id = performer_id
        self.subevent_start_date = subevent_start_date
        self.subevent_end_date = subevent_end_date
   
      
# POPULARITY ADDED AS A SUBSIDIARY ATR - DO NOT INCLUDE IN DB     
class Performer:
    id_iter = itertools.count()
    
    def __init__(self, performer_name: str, performer_type: PerformerType, is_a_band: bool, popularity: int):
        self.performer_id = next(self.id_iter)
        self.performer_name = performer_name
        self.performer_type = performer_type
        self.is_a_band = is_a_band
        self.popularity = popularity


# SIZE ADDED AS A SUBSIDIARY ATR - DO NOT INCLUDE IN DB  
class Venue:
    id_iter = itertools.count()
    
    def __init__(self, venue_name: str, venue_type: VenueType ,venue_address_id: int, venue_capacity: int, venue_size: str):
        self.venue_id = next(self.id_iter)
        self.venue_name = venue_name
        self.venue_type = venue_type
        self.venue_address_id = venue_address_id
        self.venue_capacity = venue_capacity
        self.venue_size = venue_size
        
        
# te rozmiary to tak średnio        
class Address:
    id_iter = itertools.count()
    
    def __init__(self, adr_country: str, adr_city: str, adr_street: str, adr_pcode: str, adr_nr: str):
        self.address_id = next(self.id_iter)
        self.address_country = self.validate_atr_length(adr_country, 50)
        self.address_city = self.validate_atr_length(adr_city, 58)
        self.address_street = self.validate_atr_length(adr_street, 100)
        self.address_postal_code = self.validate_atr_length(adr_pcode, 12)
        self.address_number = self.validate_atr_length(adr_nr, 10)
        
    def validate_atr_length(self, atr: str, max_length: int) -> str:
        if len(atr) > max_length:
            raise ValueError(f"Atr cant be that long")
        else:
            return atr
  
        
class Stage:
    id_iter = itertools.count()
    
    def __init__(self, stage_name: str, venue_id: int):
        self.stage_id = next(self.id_iter)
        self.stage_name = self.validate_atr_length(stage_name, 50)
        self.venue_id = venue_id
    
    def validate_atr_length(self, atr: str, max_length: int) -> str:
        if len(atr) > max_length:
            raise ValueError(f"Atr cant be that long")
        

class Seat:
    id_iter = itertools.count()
    
    def __init__(self, stage_id: int, seat_name: str, seat_status: SeatStatus, seat_sector: str):
        self.seat_id = next(self.id_iter)
        self.stage_id = stage_id
        self.seat_name = seat_name
        self.seat_status = seat_status
        self.seat_sector = seat_sector