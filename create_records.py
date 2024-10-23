from enums import EventStatus, PerformerType, SeatStatus, SubeventType, TicketType, VenueType
from tables import Ticket, Purchase, Customer, Event, Organizer, Subevent, Performer, Venue, Address, Stage, Seat
from datetime import datetime, date
import random
import numpy as np
from faker import Faker


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
        email = name + surname + random.choice([str(random.randint(1, 10000)), ""]) + "@" + faker.sentence(nb_words=1) + random.choice(["net", "com", "us"])
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


def create_venues():
    pass

def create_organizers():
    pass

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





if __name__ == '__main__':
    
    N_ORGANIZERS = 8000
    N_PERFORMERS = 15000
    N_VENUES = 25000
    N_CUSTOMERS = 800000
    N_EVENTS = 250000

    fake = Faker('en_US')
    Faker.seed(2137)
    
  
    print("\n________________________/n")
    pp = create_performers(10, fake)
    for p in pp:
        print(f"id: {p.performer_id}, Name: {p.performer_name}, Type: {p.performer_type}, Popularity: {p.popularity}")
        
    
    print("\n________________________/n")
    cc = create_customers(10, fake)
    for c in cc:
        print(f"id: {c.customer_id}, Name: {c.customer_name}, surname: {c.customer_surname}, email: {c.customer_email}, phone number: {c.customer_phone_number}, birth date: {c.customer_birth_date}")
        
        
  