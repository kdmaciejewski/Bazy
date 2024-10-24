from enum import Enum



###############################
# ENUMS

class TicketType(Enum):
    NORMAL: int = 1
    MEET_AND_GREET: int = 2
    VIP: int = 3
    
class SubeventType(Enum):
    CONCERT: int = 1
    CONFERENCE: int = 2
    SEMINAR: int = 3
    WORKSHOP: int = 4
    TRADESHOW: int = 5
    FOUNDRISER: int = 6
    EXPO: int = 7
    
class VenueType(Enum):
    PARK: int = 1
    STADIUM: int = 2
    ARENA: int = 3
    HALL: int = 4
    
class EventStatus(Enum):
    PLANNED: int = 1
    ACTIVE: int = 2
    ANNULED: int = 3
    RESCHEDULED: int = 4
    FINISHED: int = 5

class PerformerType(Enum):
    SINGER: int = 1
    DANCER: int = 2
    ACTOR: int = 3
    COMEDIAN: int = 4
    MUSICIAN: int = 5
    MAGICIAN: int = 6
    POET: int = 7
    ACROBAT: int = 8
    OTHER: int = 9
    
class SeatStatus(Enum):
    TAKEN: int = 1
    AVAILABLE: int = 2
