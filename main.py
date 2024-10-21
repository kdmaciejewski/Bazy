import pandas as pd
import random
from datetime import datetime, timedelta
import numpy as np

# Constants for US states and more populated states
more_populated_states = ["California", "Texas", "Florida", "New York", "Illinois"]
less_populated_states = ["Wyoming", "Vermont", "Alaska", "North Dakota", "South Dakota"]
all_states = more_populated_states * 4 + less_populated_states  # Skew towards more populated states

# Key dates for events
holidays = [
    datetime(2024, 1, 1),  # New Year's Day
    datetime(2024, 7, 4),  # Independence Day
    datetime(2024, 11, 28),  # Thanksgiving
    datetime(2024, 12, 25),  # Christmas
    datetime(2024, 2, 14),  # Valentine's Day
    datetime(2024, 10, 31),  # Halloween
    datetime(2024, 8, 1),  # Summer
    datetime(2024, 5, 20)  # May
]

# Helper function to generate customer birth dates
def generate_birth_date():
    current_year = datetime.now().year


    age = np.random.choice(
        range(18, 81),
        p=[
            0.2/3 if 18 <= x < 21 else  # Distribute 0.2 across ages 18, 19, 20
            0.5/14 if 21 <= x < 35 else  # Distribute 0.5 across ages 21-35
            0.2/25 if 35 <= x < 60 else  # Distribute 0.3 across ages 36-59
            0.1/21 if 60 <= x <= 80 else  # Distribute 0.1 across ages 60-79
            0
            for x in range(18, 81)
        ]
    )
    birth_year = current_year - age
    return datetime(birth_year, random.randint(1, 12), random.randint(1, 28)).strftime('%Y-%m-%d')

# Helper function to generate purchase dates with weighted times
def generate_purchase_date():
    if random.random() < 0.3:
        date = random.choice(holidays)
    else:
        date = datetime(2024, random.randint(1, 12), random.randint(1, 28))

    if date.weekday() < 5:  # Weekday
        hour = np.random.choice(range(18, 21), p=[0.5, 0.3, 0.2])
    else:  # Weekend
        hour = np.random.choice(range(10, 18))

    minute = random.randint(0, 59)
    return date + timedelta(hours=int(hour), minutes=int(minute))

# Generate more venues in more populated states
def generate_venues(num_venues):
    venues = []
    addresses = []
    for venue_id in range(1, num_venues + 1):
        state = random.choice(all_states)
        address_id = venue_id
        venue = {
            "venue_id": venue_id,
            "venue_name": f"Venue{venue_id}",
            "venue_address_id": address_id,
            "venue_capacity": random.randint(500, 5000),
            "venue_state": state
        }
        address = {
            "address_id": address_id,
            "address_country": "USA",
            "address_city": f"City{venue_id}",
            "address_street": f"Street{venue_id}",
            "address_postal_code": f"{random.randint(10000, 99999)}",
            "address_number": f"{random.randint(1, 999)}"
        }
        venues.append(venue)
        addresses.append(address)
    return venues, addresses

# Generate organizers
def generate_organizers(num_organizers):
    organizers = []
    for organizer_id in range(1, num_organizers + 1):
        organizers.append({
            "organizer_id": organizer_id,
            "organizer_name": f"Organizer{organizer_id}",
            "organizer_email": f"organizer{organizer_id}@example.com"
        })
    return organizers

# Generate customers with skewed age distribution
def generate_customers(num_customers):
    customers = []
    for customer_id in range(1, num_customers + 1):
        customers.append({
            "customer_id": customer_id,
            "customer_name": f"Name{customer_id}",
            "customer_surname": f"Surname{customer_id}",
            "customer_email": f"customer{customer_id}@example.com",
            "customer_phone_number": f"{random.randint(100000000, 999999999)}",
            "customer_birth_date": generate_birth_date()
        })
    return customers

# Generate subevents with weighted performers
def generate_subevents(events, performers, venue_ids):
    subevents = []
    subevent_types = ['concert', 'conference', 'seminar', 'workshop', 'tradeshow', 'fundraiser', 'expo']
    subevent_id = 1

    # Create weighted probabilities for performers (some will perform more)
    performer_ids = [performer['performer_id'] for performer in performers]
    performer_weights = np.random.dirichlet(np.ones(len(performers)), size=1)[0]  # Dirichlet distribution

    for event in events:
        num_subevents = random.randint(1, 5)
        for _ in range(num_subevents):
            performer_id = np.random.choice(performer_ids, p=performer_weights)  # Weighted performer selection
            venue_id = random.choice(venue_ids)
            subevent_start = datetime.strptime(event['event_start_date'], '%Y-%m-%d %H:%M:%S') + timedelta(hours=random.randint(0, 3))
            subevent_end = subevent_start + timedelta(hours=2)
            subevents.append({
                "subevent_id": subevent_id,
                "event_id": event['event_id'],
                "subevent_type": random.choice(subevent_types),
                "venue_id": venue_id,
                "performer_id": performer_id,
                "subevent_start_date": subevent_start.strftime('%Y-%m-%d %H:%M:%S'),
                "subevent_end_date": subevent_end.strftime('%Y-%m-%d %H:%M:%S')
            })
            subevent_id += 1
    return subevents

# Generate events with weighted organizers and venues
def generate_events(num_events, organizer_ids, venue_ids):
    events = []
    organizer_weights = np.random.dirichlet(np.ones(len(organizer_ids)), size=1)[0]  # Weighted organizer distribution
    venue_weights = np.random.dirichlet(np.ones(len(venue_ids)), size=1)[0]  # Weighted venue distribution

    for event_id in range(1, num_events + 1):
        organizer_id = np.random.choice(organizer_ids, p=organizer_weights)  # Weighted organizer selection
        venue_id = np.random.choice(venue_ids, p=venue_weights)  # Weighted venue selection
        event_name = f"Event{event_id}"
        start_date = generate_purchase_date()
        end_date = start_date + timedelta(days=random.randint(1, 2))
        event_description = f"Description for {event_name}."
        event_status = random.choice(["planned", "active", "rescheduled", "canceled"])

        events.append({
            "event_id": event_id,
            "organizer_id": organizer_id,
            "event_name": event_name,
            "event_start_date": start_date.strftime('%Y-%m-%d %H:%M:%S'),
            "event_end_date": end_date.strftime('%Y-%m-%d %H:%M:%S'),
            "event_description": event_description,
            "event_status": event_status
        })
    return events


# Generate performers
def generate_performers(num_performers):
    performers = []
    for performer_id in range(1, num_performers + 1):
        performer_type = random.choice(["Singer", "Musician", "Comedian", "Dancer", "Actor", "Magician"])
        is_a_band = random.random() < 0.2
        performers.append({
            "performer_id": performer_id,
            "performer_name": f"Performer{performer_id}",
            "performer_type": performer_type,
            "is_a_band": is_a_band
        })
    return performers

# Generate stages and seats
def generate_stages_and_seats(venues):
    stages = []
    seats = []
    seat_id = 1
    for venue in venues:
        stage_id = venue["venue_id"]
        stages.append({
            "stage_id": stage_id,
            "stage_name": f"Stage{stage_id}",
            "vanue_id": venue["venue_id"]
        })
        # Generate seats for the stage
        for seat_num in range(1, random.randint(50, 150)):
            seats.append({
                "seat_id": seat_id,
                "stage_id": stage_id,
                "seat_name": f"Seat{seat_num}",
                "seat_status": "available",
                "sector": f"Sector{random.choice(['A', 'B', 'C', 'D'])}"
            })
            seat_id += 1
    return stages, seats

# Generate purchases and tickets
def generate_purchases_and_tickets(customers, events):
    purchases = []
    tickets = []
    purchase_id = 1
    ticket_id = 1
    for customer in customers:
        num_purchases = random.randint(1, 3)
        for _ in range(num_purchases):
            purchase_date = generate_purchase_date()
            total_price = round(random.uniform(20, 200), 2)
            purchases.append({
                "purchase_id": purchase_id,
                "customer_id": customer["customer_id"],
                "purchase_date": purchase_date.strftime('%Y-%m-%d %H:%M:%S'),
                "purchase_total_price": total_price
            })

            # Generate tickets for each purchase
            num_tickets = random.randint(1, 5)
            for _ in range(num_tickets):
                event = random.choice(events)
                seat = random.randint(1, 100)  # Assumes seats are numbered from 1 to 100 for simplicity
                tickets.append({
                    "ticket_id": ticket_id,
                    "purchase_id": purchase_id,
                    "event_id": event["event_id"],
                    "seat_id": seat,
                    "ticket_price": round(random.uniform(10, 100), 2),
                    "ticket_status": random.choice(["valid", "used", "expired"])
                })
                ticket_id += 1

            purchase_id += 1
    return purchases, tickets


if __name__ == '__main__':
    # Number of data entries to generate
    NUM_VENUES = 100000
    NUM_ORGANIZERS = 10000
    NUM_CUSTOMERS = 500000
    NUM_EVENTS = 200000
    NUM_PERFORMERS = 50000

    # Generate data
    venues, addresses = generate_venues(NUM_VENUES)
    organizers = generate_organizers(NUM_ORGANIZERS)
    customers = generate_customers(NUM_CUSTOMERS)
    events = generate_events(NUM_EVENTS, [org["organizer_id"] for org in organizers], [venue["venue_id"] for venue in venues])
    performers = generate_performers(NUM_PERFORMERS)
    stages, seats = generate_stages_and_seats(venues)
    subevents = generate_subevents(events, performers, [venue["venue_id"] for venue in venues])
    purchases, tickets = generate_purchases_and_tickets(customers, events)

    # Convert data to DataFrames for export to CSV
    df_addresses = pd.DataFrame(addresses)
    df_venues = pd.DataFrame(venues)
    df_organizers = pd.DataFrame(organizers)
    df_customers = pd.DataFrame(customers)
    df_events = pd.DataFrame(events)
    df_performers = pd.DataFrame(performers)
    df_stages = pd.DataFrame(stages)
    df_seats = pd.DataFrame(seats)
    df_subevents = pd.DataFrame(subevents)
    df_purchases = pd.DataFrame(purchases)
    df_tickets = pd.DataFrame(tickets)

    # Export to CSV
    df_addresses.to_csv('data/addresses.csv', index=False)
    df_venues.to_csv('data/venues.csv', index=False)
    df_organizers.to_csv('data/organizers.csv', index=False)
    df_customers.to_csv('data/customers.csv', index=False)
    df_events.to_csv('data/events.csv', index=False)
    df_performers.to_csv('data/performers.csv', index=False)
    df_stages.to_csv('data/stages.csv', index=False)
    df_seats.to_csv('data/seats.csv', index=False)
    df_subevents.to_csv('data/subevents.csv', index=False)
    df_purchases.to_csv('data/purchases.csv', index=False)
    df_tickets.to_csv('data/tickets.csv', index=False)

    print("Data generation completed and saved to CSV files.")
