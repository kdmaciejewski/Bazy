from torch import native_batch_norm
from enums import EventStatus, PerformerType, SeatStatus, SubeventType, TicketType, VenueType
from tables import Ticket, Purchase, Customer, Event, Organizer, Subevent, Performer, Venue, Address, Stage, Seat
from datetime import datetime, date
import random
import numpy as np
from faker import Faker
from faker.providers import DynamicProvider

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
    return datetime(birth_year, random.randint(1, 12), random.randint(1, 28)).strftime('%Y-%m-%d')


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



'''
from faker.providers import DynamicProvider

medical_professions_provider = DynamicProvider(
     provider_name="medical_profession",
     elements=["dr.", "doctor", "nurse", "surgeon", "clerk"],
)

fake = Faker()

# then add new provider to faker instance
fake.add_provider(medical_professions_provider)

# now you can use:
fake.medical_profession()
# 'dr.'
'''


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
        address_number = faker.building_number()
        
        return Address(adr_country=country, adr_city=address_city, adr_street=address_street, adr_pcode=address_postal_code, adr_nr=address_number)
    
    
    def create_venue_and_address(faker):
        venue_type = random.choices(venue_types, weights=venues_weights, k=1)[0]
        match venue_type:
            case VenueType.PARK:
                venue_size = random.choices(sizes, weights=[0.1, 0.2, 0.55, 0.15], k=1)[0]
                venue_capacity = random.randint(venues_sizes[venue_size][0], venues_sizes[venue_size][1])
                venue_name = faker.sentence(nb_words=3, variable_nb_words=True)[:-1] + "Park"
            case VenueType.STADIUM:
                venue_size = random.choices(sizes, weights=[0.01, 0.1, 0.65, 0.24], k=1)[0]
                venue_capacity = random.randint(venues_sizes[venue_size][0], venues_sizes[venue_size][1])
                venue_name = random.choice(["The", ""]) + faker.sentence(nb_words=3, variable_nb_words=True)[:-1] + random.choices(["Stadium", ""], weights=[0.7, 0.3], k=1)[0]
            case VenueType.ARENA:
                venue_size = random.choices(sizes, weights=[0.1, 0.7, 0.15, 0.05], k=1)[0]
                venue_capacity = random.randint(venues_sizes[venue_size][0], venues_sizes[venue_size][1])
                venue_name = random.choice(["The", ""]) + faker.sentence(nb_words=3, variable_nb_words=True)[:-1] + random.choices(["Arena", ""], weights=[0.7, 0.3], k=1)[0]
            case VenueType.HALL:
                venue_size = random.choices(sizes, weights=[0.4, 0.4, 0.1, 0.1], k=1)[0]
                venue_capacity = random.randint(venues_sizes[venue_size][0], venues_sizes[venue_size][1])
                venue_name = random.choice(["The", ""]) + faker.sentence(nb_words=3, variable_nb_words=True)[:-1] + random.choices(["Stadium", ""], weights=[0.7, 0.3], k=1)[0]
            case _:
                venue_name = "The" + faker.sentence(nb_words=2, variable_nb_words=True)
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


def create_tickets():
    pass

def create_purchases():
    pass

def create_seats():
    pass

def create_stages():
    pass

def create_subevents():
    pass

def create_address():
    pass



def sanity_check(n):
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
        
        
    #venue_types = [item for item in VenueType]
    #print(venue_types)
    print("\n________________________\n")
    print("VENUES AND ADDRESSES")
    
    
    vv, aa = create_venues_and_addresses(n, fake)
    for v,a in zip(vv, aa):
        print(f"Venue: {v.venue_id}, name: {v.venue_name}, type: {v.venue_type}, addres_id: {v.venue_address_id}, capacity: {v.venue_capacity}, size: {v.venue_size}")
        print(f"Adres: {a.address_id}, country: {a.address_country}, city: {a.address_city}, street: {a.address_street}, pcode: {a.address_postal_code}, nr: {a.address_number}\n")
  
    
    

if __name__ == '__main__':
    
    N_ORGANIZERS = 8000
    N_PERFORMERS = 15000
    N_CUSTOMERS = 800000
    
    N_VENUES = 21000
    
    N_EVENTS = 250000

    n = 10
    sanity_check(n)
    
    
    fake = Faker('en_US')
    Faker.seed(2137)
    
    '''
    print("/////////////////////////////////////")
    get_n_fake_cities(5, fake)
    for i in range(0, 20):
        print(fake.fake_adr())
    '''
    