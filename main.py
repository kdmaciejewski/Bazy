import pandas as pd
import random
from datetime import datetime, timedelta
import numpy as np

# Example holiday dates
holidays = [
    datetime(2024, 12, 25),  # Christmas
    datetime(2024, 12, 31),  # New Year's Eve
    datetime(2024, 11, 28),  # Thanksgiving (US)
    datetime(2024, 7, 4)  # Independence Day (US)
]


# Function to generate random dates with more weight towards holidays
def generate_purchase_date():
    holiday_prob = 0.3  # 30% chance of a purchase being on a holiday
    normal_prob = 0.7  # 70% chance of a purchase being on a normal day

    if random.random() < holiday_prob:
        return random.choice(holidays) + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
    else:
        return datetime(2024, random.randint(1, 12), random.randint(1, 28)) + timedelta(hours=random.randint(0, 23),
                                                                                        minutes=random.randint(0, 59))

def generate_customers(num_customers):
    customers = []
    for customer_id in range(1, num_customers + 1):
        customer = {
            "customer_id": customer_id,
            "customer_name": f"Name{customer_id}",
            "customer_surname": f"Surname{customer_id}",
            "customer_email": f"customer{customer_id}@example.com",
            "customer_phone_number": f"{random.randint(100000000, 999999999)}",
            "customer_birth_date": datetime(1980 + random.randint(0, 40), random.randint(1, 12), random.randint(1, 28)).strftime('%Y-%m-%d')
        }
        customers.append(customer)
    return customers


def generate_purchases(num_purchases, num_customers):
    purchases = []
    for purchase_id in range(1, num_purchases + 1):
        customer_id = random.randint(1, num_customers)
        purchase_date = generate_purchase_date()
        total_price = round(random.uniform(20.0, 500.0), 2)

        purchase = {
            "purchase_id": purchase_id,
            "customer_id": customer_id,
            "purchase_date": purchase_date.strftime('%Y-%m-%d %H:%M:%S'),
            "purchase_total_price": total_price
        }
        purchases.append(purchase)
    return purchases


def generate_events(num_events, organizer_ids):
    events = []
    for event_id in range(1, num_events + 1):
        organizer_id = random.choice(organizer_ids)
        event_name = f"Event{event_id}"
        start_date = datetime(2024, random.randint(1, 12), random.randint(1, 28), random.randint(0, 23), random.randint(0, 59))
        end_date = start_date + timedelta(days=random.randint(1, 5))
        event_description = f"This is a description for {event_name}."
        event_status = random.choice(["planned", "active", "rescheduled", "finished"])

        event = {
            "event_id": event_id,
            "organizer_id": organizer_id,
            "event_name": event_name,
            "event_start_date": start_date.strftime('%Y-%m-%d %H:%M:%S'),
            "event_end_date": end_date.strftime('%Y-%m-%d %H:%M:%S'),
            "event_description": event_description,
            "event_status": event_status
        }
        events.append(event)
    return events

def generate_tickets(num_tickets, event_ids, purchase_ids):
    tickets = []
    for ticket_id in range(1, num_tickets + 1):
        purchase_id = random.choice(purchase_ids)
        event_id = random.choice(event_ids)
        ticket_type = random.choice(["normal", "meet_and_greet", "vip"])
        ticket_price = round(random.uniform(50.0, 200.0), 2)

        ticket = {
            "ticket_id": ticket_id,
            "purchase_id": purchase_id,
            "event_id": event_id,
            "ticket_type": ticket_type,
            "ticket_price": ticket_price
        }
        tickets.append(ticket)
    return tickets


if __name__ == '__main__':
    customers = generate_customers(100)
    purchases = generate_purchases(200, len(customers))

    # Save to CSV
    pd.DataFrame(customers).to_csv('customers.csv', index=False)
    pd.DataFrame(purchases).to_csv('purchases.csv', index=False)