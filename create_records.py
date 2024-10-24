from re import M
from torch import native_batch_norm
from enums import EventStatus, PerformerType, SeatStatus, SubeventType, TicketType, VenueType
from tables import Ticket, Purchase, Customer, Event, Organizer, Subevent, Performer, Venue, Address, Stage, Seat
from datetime import datetime, date, timedelta
import random
import numpy as np
from faker import Faker
from faker.providers import DynamicProvider
import pandas as pd

# Constants for US states and more populated states
more_populated_states = ["California", "Texas", "Florida", "New York", "Illinois"]
less_populated_states = ["Wyoming", "Vermont", "Alaska", "North Dakota", "South Dakota"]
all_states = more_populated_states * 4 + less_populated_states  # Skew towards more populated states

#(month, day)
holidays = [
    (1, 1),  # New Year's Day
    (7, 4),  # Independence Day
    (11, 28),  # Thanksgiving
    (12, 25),  # Christmas
    (2, 14),  # Valentine's Day
    (10, 31),  # Halloween
    (8, 1),  # Summer
    (5, 20)  # May
]


def get_season(date: date):
    dt_obj = date
    md = (dt_obj.month, dt_obj.day)
    if (3, 21) <= md < (6, 21):
        return "Spring"
    if (6, 21) <= md < (9, 21):
        return "Summer"
    if (9, 21) <= md < (12, 21):
        return "Autumn"
    return "Winter"


# generate customer birth date
def generate_birth_date():
    
    age = np.random.choice(
        range(18, 81),
        p = [
            0.2 / 3 if 18 <= x < 21 else   # Distribute 0.2 across ages 18, 19, 20
            0.5 / 14 if 21 <= x < 35 else  # Distribute 0.5 across ages 21-35
            0.2 / 25 if 35 <= x < 60 else  # Distribute 0.3 across ages 36-59
            0.1 / 21 if 60 <= x <= 80 else  # Distribute 0.1 across ages 60-79
            0
            for x in range(18, 81)
        ]
    )
    
    birth_year = datetime.now().year - age
    return datetime(birth_year, random.randint(1, 12), random.randint(1, 28))#.strftime('%Y-%m-%d')


def generate_purchase_date():
    if random.random() < 0.3:
        d = random.choice(holidays)
        date = datetime(2024, d[0], d[1])
    else:
        date = datetime(2024, random.randint(1, 12), random.randint(1, 28))

    if date.weekday() < 5:  # Weekday
        hour = np.random.choice(range(18, 21), p=[0.5, 0.3, 0.2])
    else:  # Weekend
        hour = np.random.choice(range(10, 18))

    minute = random.randint(0, 59)
    return date + timedelta(hours=int(hour), minutes=int(minute))

#####################################################################################################


def create_performers(n_of_performers: int, faker: Faker):
    
    # [SINGER, DANCER, ACTOR, COMEDIAN, MUSICIAN, MAGICIAN, POET, ACROBAT, OTHER]
    performer_types = [item for item in PerformerType]
    performer_weights = [0.2, 0.1, 0.1,  0.2, 0.2, 0.05, 0.05, 0.02, 0.08]
    
    popularities = [i for i in range(1, 11)]
    #                       1    2    3    4      5   6    7,     8      9,    10
    popularity_weights = [0.03, 0.1, 0.1, 0.185, 0.2, 0.2, 0.1, 0.05, 0.02, 0.015  ]
    
    def create_performer(faker):
        
        popularity = random.choices(popularities, weights=popularity_weights, k=1)[0]
        performer_type = random.choices(performer_types, weights=performer_weights, k=1)[0]
        
        is_a_band = random.choices([True, False], [0.3, 0.7], k=1)[0]
        if is_a_band:
            name = faker.sentence(nb_words=3, variable_nb_words=True)[:-1]
        else:
            name = faker.name()
        
        return Performer(name, performer_type, is_a_band, popularity)
    
    count = 0
    performers = []
    while(count != n_of_performers):
        p = create_performer(faker)
        performers.append(p)
        count += 1

    return performers


def create_customers(n_of_customers: int, faker: Faker):
    
    def create_customer(faker):
        name, surname = faker.first_name(), faker.last_name()
        #email = faker.email()
        email = name + surname + random.choice([str(random.randint(1, 10000)), ""]) + "@" + faker.sentence(nb_words=1).lower() + random.choice(["net", "com", "us"])
        phone_nr = faker.phone_number()
        birth_date = generate_birth_date()
        return Customer(name, surname, email, phone_nr, birth_date)
    
    count = 0
    customers = []
    
    while(count != n_of_customers):
        client = create_customer(faker)
        customers.append(client)
        count += 1
     
    return customers


def get_n_fake_cities(n, faker):
    adrs = set()
    for _ in range(0, n):
        fake_city = faker.city()
        pcode = faker.postcode()
        adrs.add((fake_city, pcode))
    
    adr_provider = DynamicProvider(
        provider_name="fake_adr",
        elements=list(adrs)
    )
    
    faker.add_provider(adr_provider)
    return 


def create_venues_and_addresses(n_of_venues: int, faker: Faker):
    
    venue_types = [item for item in VenueType]
    # types:         PARK, STADIUM, ARENA, HALL
    venues_weights = [0.2,   0.1,    0.3,    0.4]
    # (min, max) for every size
    venues_sizes = {"small": (200, 2000), "mid": (1000, 6000), "big": (8000, 30000), "huge": (30000, 100000) }
    sizes = ["small", "mid", "big", "huge"]
    
    def create_address(faker):
        country = "United States"
        adres = faker.fake_adr()
        address_city = adres[0]
        address_street = faker.street_name()
        address_postal_code = adres[1]
        address_number = str( int(faker.building_number()) % random.choice([10, 100, 1000]) )
        
        return Address(adr_country=country, adr_city=address_city, adr_street=address_street, adr_pcode=address_postal_code, adr_nr=address_number)
    
    
    def create_venue_and_address(faker):
        venue_type = random.choices(venue_types, weights=venues_weights, k=1)[0]
        match venue_type:
            case VenueType.PARK:
                venue_size = random.choices(sizes, weights=[0.1, 0.2, 0.55, 0.15], k=1)[0]
                venue_capacity = random.randint(venues_sizes[venue_size][0], venues_sizes[venue_size][1])
                venue_name = faker.sentence(nb_words=3, variable_nb_words=True)[:-1] + " Park"
            case VenueType.STADIUM:
                venue_size = random.choices(sizes, weights=[0.01, 0.1, 0.65, 0.24], k=1)[0]
                venue_capacity = random.randint(venues_sizes[venue_size][0], venues_sizes[venue_size][1])
                venue_name = random.choice(["The ", ""]) + faker.sentence(nb_words=3, variable_nb_words=True)[:-1] + random.choices([" Stadium", ""], weights=[0.7, 0.3], k=1)[0]
            case VenueType.ARENA:
                venue_size = random.choices(sizes, weights=[0.1, 0.7, 0.15, 0.05], k=1)[0]
                venue_capacity = random.randint(venues_sizes[venue_size][0], venues_sizes[venue_size][1])
                venue_name = random.choice(["The ", ""]) + faker.sentence(nb_words=3, variable_nb_words=True)[:-1] + random.choices([" Arena", ""], weights=[0.7, 0.3], k=1)[0]
            case VenueType.HALL:
                venue_size = random.choices(sizes, weights=[0.4, 0.4, 0.1, 0.1], k=1)[0]
                venue_capacity = random.randint(venues_sizes[venue_size][0], venues_sizes[venue_size][1])
                venue_name = random.choice(["The ", ""]) + faker.sentence(nb_words=3, variable_nb_words=True)[:-1] + random.choices([" Stadium", ""], weights=[0.7, 0.3], k=1)[0]
            case _:
                venue_name = "The " + faker.sentence(nb_words=2, variable_nb_words=True)
                venue_capacity = random.randint(100, 10000)
                venue_name = random.choice(sizes)
        
        venue_address = create_address(faker)
        return Venue(venue_name=venue_name, venue_type=venue_type, venue_address_id=venue_address.address_id, venue_capacity=venue_capacity, venue_size=venue_size), venue_address
        

    count = 0
    venues = []
    addresses = []
    
    while(count != n_of_venues):
        v, a = create_venue_and_address(faker)
        venues.append(v)
        addresses.append(a)
        count += 1
    
    return venues, addresses


def create_organizers(n_of_organizers: int, faker: Faker):
    
    def create_organizer(faker: Faker):
        name = faker.name()
        email = name.split(" ")[0] + name.split(" ")[1] + str(random.choice(["_biz", "_org", "_private", "_buisness"])) + "@" + random.choice(["contact.", ""]) + faker.sentence(nb_words=1).lower() + random.choice(["net", "com", "us"])    
        return Organizer(name, email)
    
    count = 0
    organizers = []
    
    while(count != n_of_organizers):
        o = create_organizer(faker)
        organizers.append(o)
        count += 1
    
    return organizers


def create_seats(stages):
    seats = []
    for stage in stages:
        for i in range(10, random.randint(20, 100)):
            name = f"s{i}"
            status = SeatStatus.AVAILABLE
            sector = random.choice([f"sector-{j}" for j in range(0, 10)])
            s = Seat(stage_id=stage.stage_id, seat_name=name, seat_status=status, seat_sector=sector)
            seats.append(s)
            
    return seats


def create_stages(venues):
    
    name_conv = {"text": ["A", "B", "C", "D", "E"], "numerical": ["1", "2", "3", "4", "5"], "other": ["main", "second", "third", "fourth", "fifth"]}
    convs = list(name_conv.keys())
    stages = []
    for v in venues:
        n_of_stages_in_venue = random.choices([i for i in range(1,6)], weights=[0.85, 0.11, 0.02, 0.01, 0.01], k=1)[0]
        #v_capacity = v.venue_capacity
        conv = random.choice(convs)
        
        for i in range(0, n_of_stages_in_venue):
            stage = Stage(name_conv[conv][i], v.venue_id)
            stages.append(stage)

    return stages


def create_events(n_of_events, faker, organizers):
    
    def create_event(organizer_weights, organizer_ids, faker):
        
        event_name = faker.sentence(nb_words=2, variable_nb_words=True)[:-1] + random.choice([" Event", " Performance", " Party", ""])
        organizer_id = np.random.choice(organizer_ids, p=organizer_weights) 
        
        start_date = generate_purchase_date()
        end_date = start_date + timedelta(hours=random.randint(1, 4), minutes=random.randint(0, 59))
        
        event_description = faker.sentence(nb_words=20, variable_nb_words=True)[:-1]
        event_status = random.choice([item for item in EventStatus])
        
        # DATA FOR SUBEVENTS        
        venue_artists = {'small': range(1, 6), 'mid': range(3, 7), 'big': range(6, 11), 'huge': range(7, 11)}
        event_size = list(venue_artists.keys())
        event_size =  random.choice(event_size)
        
        n_of_subevents = np.random.choice([i for i in range(1, 5)], p=[0.75, 0.2, 0.04, 0.01])
        
        event = Event(organizer_id=organizer_id, event_name=event_name, event_start_date=start_date, event_end_date=end_date, event_description=event_description, event_status=event_status, n_of_subevents=n_of_subevents, event_size=event_size)
              
        return event
    
    
    organizer_weights = np.random.dirichlet(np.ones(len(organizers)), size=1)[0] # Weighted organizer distribution
    organizer_ids = [o.organizer_id for o in organizers]
    
    count = 0
    events = []
    
    while(count != n_of_events):
        e = create_event(organizer_weights, organizer_ids, faker)
        events.append(e)
        count += 1
    
    return events
    

def create_subevents(events, venues, performers):
    venue_artists = {'small': range(1, 6), 'mid': range(3, 7), 'big': range(6, 11), 'huge': range(7, 11)}
        
    def create_subevent(venue, performer, subevent_start, subevent_end, event_id):
        subevent_type = random.choice([item for item in SubeventType])
        return Subevent(event_id=event_id, subevent_type=subevent_type, venue_id=venue.venue_id, performer_id=performer.performer_id, subevent_start_date=subevent_start, subevent_end_date=subevent_end)
    
    
    subevents = []
    
    for e in events:
        n_of_subevents = e.event_n_of_subevents
        event_size = e.event_size
        
        matching_venues_size = [venue for venue in venues if venue.venue_size]
        matching_performers_size = [p for p in performers if p.popularity in venue_artists[event_size]]
        
        if len(matching_performers_size) != 0:
            performer_1 = random.choice(matching_performers_size) 
            performer_1_proffession = performer_1.performer_type
        else:
            # screw it
            performer_1 = random.choice([p for p in performers]) 
            performer_1_proffession = performer_1.performer_type
        
        if n_of_subevents != 1:
            matching_performer_set = [performer_1]
            #im giving 20 shots for different performers
            for _ in range(20):
                performer_i = random.choice([p for p in matching_performers_size if p.performer_type==performer_1_proffession])
                if performer_i:
                    if performer_1 not in matching_performer_set and len(matching_performer_set) != n_of_subevents:
                        matching_performer_set.append(performer_i)
            
            n_set = len(matching_performer_set)
            if n_set != n_of_subevents:
                b_plan = random.choices(matching_performers_size, k=n_of_subevents-n_set)
                matching_performer_set.extend(b_plan)
        else:
            matching_performer_set = [performer_1]
        
        venue = random.choice(matching_venues_size)
        
 
        total_seconds = (e.event_end_date - e.event_start_date).total_seconds()
        interval_seconds = total_seconds / n_of_subevents
        stages = [e.event_start_date + timedelta(seconds=i * interval_seconds) for i in range(n_of_subevents + 1)]
        stage_tuples = [(stages[i], stages[i+1]) for i in range(len(stages) - 1)]
        
        for i in range(n_of_subevents):
            sub_event = create_subevent(venue, matching_performer_set[i], stage_tuples[i][0], stage_tuples[i][1], e.event_id)
            subevents.append(sub_event)
            
    return subevents
    

def create_tickets(n_of_tickets, purchases, events, seats):
    
    def create_ticket(purchase, event, seat):
        
        ticket_type = random.choices([item for item in TicketType], weights=[0.8, 0.17, 0.03], k=1)[0]
        ticket_price = random.choice([float(10)*0.5*p for p in range(1, 50) if float(10)*0.5*p < purchase.purchase_total_price])
    
        return Ticket(purchase_id=purchase.purchase_id, event_id=event.event_id, ticket_type=ticket_type, ticket_seat_id=seat.seat_id, ticket_price=ticket_price)
    
    count = 0
    tickets = []
    
    while(count != n_of_tickets):
        purchase = random.choice(purchases)
        seat = random.choice(seats)
        event = random.choice(events)
        
        t = create_ticket(purchase, event, seat)
        tickets.append(t)
        count += 1
    
    return tickets
       

def create_purchases(n_of_purchases, customers):
    
    def create_purchase(customer):
        price = random.randint(1, 5) * random.choice([float(10)*0.5*p for p in range(1, 50)])
        p_date = generate_purchase_date()
        return Purchase(customer_id=customer.customer_id, purchase_date=p_date, purchase_total_price=price)
    
    
    count = 0
    purchases = []
    
    while(count != n_of_purchases):
        customer = random.choice(customers)
        p = create_purchase(customer)
        purchases.append(p)
        count += 1
    
    return purchases
    


############################################


def sanity_check(n=15):
    fake = Faker('en_US')
    Faker.seed(2137)
    get_n_fake_cities(8, fake)
  
    print("\n________________________\n")
    print("PERFORMERS")
    pp = create_performers(n, fake)
    for p in pp:
        print(f"id: {p.performer_id}, Name: {p.performer_name}, Type: {p.performer_type}, Popularity: {p.popularity}")
        
    print("\n________________________\n")
    print("CUSTOMERS")
    cc = create_customers(n, fake)
    for c in cc:
        print(f"id: {c.customer_id}, Name: {c.customer_name}, surname: {c.customer_surname}, email: {c.customer_email}, phone number: {c.customer_phone_number}, birth date: {c.customer_birth_date}")
        
    print("\n________________________\n")
    print("ORGANIZERS")
    oo = create_organizers(n, fake)
    for o in oo:
        print(f"id: {o.organizer_id}, Name: {o.organizer_name}, email: {o.organizer_email}")
        
    print("\n________________________\n")
    print("VENUES AND ADDRESSES")
    
    
    vv, aa = create_venues_and_addresses(n, fake)
    for v,a in zip(vv, aa):
        print(f"Venue: {v.venue_id}, name: {v.venue_name}, type: {v.venue_type}, addres_id: {v.venue_address_id}, capacity: {v.venue_capacity}, size: {v.venue_size}")
        print(f"Adres: {a.address_id}, country: {a.address_country}, city: {a.address_city}, street: {a.address_street}, pcode: {a.address_postal_code}, nr: {a.address_number}\n")
        
    
    print("\n________________________\n")
    print("STAGES")
    ss = create_stages(vv)
    for s in ss:
        print(f"Stage: {s.stage_id}, name: {s.stage_name}, venue_id: {s.venue_id}")
        
    print("\n________________________\n")
    print("SEATS")
    sts = create_seats(ss)
    for st in sts[:10]:
        print(f"Seat: {st.seat_id}, stage: {st.stage_id}, name: {st.seat_name}, status: {st.seat_status}, sector: {st.seat_sector}")
          
    print("\n________________________\n")
    print("EVENTS")
    ee = create_events(n, fake, oo)
    for e in ee:
        print(f"EVENT id: {e.event_id}, Name: {e.event_name}, start: {e.event_start_date}, end: {e.event_end_date}, status: {e.event_status}, n of subevents: {e.event_n_of_subevents}, size: {e.event_size}")
    
    print("\n________________________\n")
    print("SUBEVENTS")
    ses = create_subevents(ee, vv, pp)
    for se in ses:
        print(f"SUBEVENT id: {se.subevent_id}, event_id: {se.event_id}, start: {se.subevent_start_date}, end: {se.subevent_end_date}, performer: {se.performer_id}, venue: {se.venue_id}, type: {se.subevent_type}")      
        
    print("\n________________________\n")
    print("PURCHASES")
    prs = create_purchases(n, cc)
    for pr in prs:
        print(f"Purchase: {pr.purchase_id}, customer: {pr.customer_id}, total: {pr.purchase_total_price}, date: {pr.purchase_date}")
        
        
    print("\n________________________\n")
    print("TICKETS")
    ts = create_tickets(n, prs, ee, sts)
    for t in ts:
        print(f"Ticket: {t.ticket_id}, purchase_id: {t.purchase_id}, price: {t.ticket_price}, event: {t.event_id}, type: {t.ticket_type}, seat_id: {t.ticket_seat_id}")
        
    PERFORMERS = [p.to_dict() for p in pp]
    CUSTOMERS = [c.to_dict() for c in cc]
    ORGANIZERS = [o.to_dict() for o in oo]
    VENUES = [v.to_dict() for v in vv]
    ADDRESSES = [a.to_dict() for a in aa]
    STAGES = [s.to_dict() for s in ss]
    SEATS = [st.to_dict() for st in sts]
    EVENTS = [e.to_dict() for e in ee]
    SUBEVENTS = [se.to_dict() for se in ses]
    PURCHASES = [pr.to_dict() for pr in prs]
    TICKETS = [t.to_dict() for t in ts]
    
    # Convert data to DataFrames for export to CSV
    df_addresses = pd.DataFrame(ADDRESSES)
    df_venues = pd.DataFrame(VENUES)
    df_organizers = pd.DataFrame(ORGANIZERS)
    df_customers = pd.DataFrame(CUSTOMERS)
    df_events = pd.DataFrame(EVENTS)
    df_performers = pd.DataFrame(PERFORMERS)
    df_stages = pd.DataFrame(STAGES)
    df_seats = pd.DataFrame(SEATS)
    df_subevents = pd.DataFrame(SUBEVENTS)
    df_purchases = pd.DataFrame(PURCHASES)
    df_tickets = pd.DataFrame(TICKETS)
    
    # Export to CSV
    df_addresses.to_csv('data_sample/addresses.csv', index=False)
    df_venues.to_csv('data_sample/venues.csv', index=False)
    df_organizers.to_csv('data_sample/organizers.csv', index=False)
    df_customers.to_csv('data_sample/customers.csv', index=False)
    df_events.to_csv('data_sample/events.csv', index=False)
    df_performers.to_csv('data_sample/performers.csv', index=False)
    df_stages.to_csv('data_sample/stages.csv', index=False)
    df_seats.to_csv('data_sample/seats.csv', index=False)
    df_subevents.to_csv('data_sample/subevents.csv', index=False)
    df_purchases.to_csv('data_sample/purchases.csv', index=False)
    df_tickets.to_csv('data_sample/tickets.csv', index=False)

    print("Data generation completed and saved to CSV files.")
    
  
def main():
    
    N_ORGANIZERS = 8000
    N_PERFORMERS = 15000
    N_CUSTOMERS = 800000
    
    N_VENUES = 21000
    
    N_EVENTS = 250000
    
    N_PURCHASES = 950000
    N_TICKETS = 1000000
    
    fake = Faker('en_US')
    Faker.seed(2137)
    get_n_fake_cities(4000, fake)
    

    pp = create_performers(N_PERFORMERS, fake)
    cc = create_customers(N_CUSTOMERS, fake)
    oo = create_organizers(N_ORGANIZERS, fake)  
    vv, aa = create_venues_and_addresses(N_VENUES, fake)
    ss = create_stages(vv)
    sts = create_seats(ss)
    ee = create_events(N_EVENTS, fake, oo)
    ses = create_subevents(ee, vv, pp)
    prs = create_purchases(N_PURCHASES, cc)
    ts = create_tickets(N_TICKETS, prs, ee, sts)

    PERFORMERS = [p.to_dict() for p in pp]
    CUSTOMERS = [c.to_dict() for c in cc]
    ORGANIZERS = [o.to_dict() for o in oo]
    VENUES = [v.to_dict() for v in vv]
    ADDRESSES = [a.to_dict() for a in aa]
    STAGES = [s.to_dict() for s in ss]
    SEATS = [st.to_dict() for st in sts]
    EVENTS = [e.to_dict() for e in ee]
    SUBEVENTS = [se.to_dict() for se in ses]
    PURCHASES = [pr.to_dict() for pr in prs]
    TICKETS = [t.to_dict() for t in ts]
    
        # Convert data to DataFrames for export to CSV
    df_addresses = pd.DataFrame(ADDRESSES)
    df_venues = pd.DataFrame(VENUES)
    df_organizers = pd.DataFrame(ORGANIZERS)
    df_customers = pd.DataFrame(CUSTOMERS)
    df_events = pd.DataFrame(EVENTS)
    df_performers = pd.DataFrame(PERFORMERS)
    df_stages = pd.DataFrame(STAGES)
    df_seats = pd.DataFrame(SEATS)
    df_subevents = pd.DataFrame(SUBEVENTS)
    df_purchases = pd.DataFrame(PURCHASES)
    df_tickets = pd.DataFrame(TICKETS)
    
    # Export to CSV
    df_addresses.to_csv('data_full/addresses.csv', index=False)
    df_venues.to_csv('data_full/venues.csv', index=False)
    df_organizers.to_csv('data_full/organizers.csv', index=False)
    df_customers.to_csv('data_full/customers.csv', index=False)
    df_events.to_csv('data_full/events.csv', index=False)
    df_performers.to_csv('data_full/performers.csv', index=False)
    df_stages.to_csv('data_full/stages.csv', index=False)
    df_seats.to_csv('data_full/seats.csv', index=False)
    df_subevents.to_csv('data_full/subevents.csv', index=False)
    df_purchases.to_csv('data_full/purchases.csv', index=False)
    df_tickets.to_csv('data_full/tickets.csv', index=False)

    print("Data generation completed and saved to CSV files.")
    
    


if __name__ == '__main__':
    
    main()
    #sanity_check(15)
    