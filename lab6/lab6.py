import pg8000
import csv
import time

DB_SETTINGS = {
    "database": "bazy",
    "user": "postgres",
    "password": "Maciejewski12",
    "host": "localhost",
    "port": 5432
}

PROCEDURES = []
OUTPUT_FILE = "results.txt"
OUTPUT_PLANS_FILE = "plans.txt"
NUM_RUNS = 2

def check_record_counts(cursor):
    # Wymagane liczby rekordów
    required_counts = {
        "Ticket": 1000000,
        "Purchase": 950000,
        "Event": 85000,
        "Organizer": 800,
        "Customer": 800000,
        "Venue": 2100,
        "Performer": 17000,
        "Subevent": 111563,
        "Address": 2100,
        "Stage": 2588,
        "Seat": 132123
    }

    # Wynik
    insufficient_data = []

    # Zapytania SQL dla każdej tabeli
    for table, required_count in required_counts.items():
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        actual_count = cursor.fetchone()[0]

        if actual_count < required_count:
            insufficient_data.append((table, actual_count, required_count))

    if insufficient_data:
        print("Niektóre tabele mają niewystarczającą liczbę rekordów:")
        for table, actual, required in insufficient_data:
            print(f"Tabela: {table}, Liczba rekordów: {actual}, Wymagana: {required}")
    else:
        print("Wszystkie tabele mają wystarczającą liczbę rekordów.")

    return insufficient_data

def load_queries_from_file(file_path):
    queries = []

    with open(file_path, 'r') as file:
        query = ""
        for line in file:
            line = line.strip()

            if line:
                query += line + " "

            if line.endswith(";"):
                queries.append(query.strip())
                query = ""
    return queries

def execute_procedure(cursor, procedure_name):
    start_time = time.time()
    cursor.execute(f"{procedure_name};")
    execution_time = time.time() - start_time

    return execution_time


def get_query_plan(cursor, procedure_name):
    cursor.execute(f"EXPLAIN ANALYZE {procedure_name};")

    return "\n".join(row[0] for row in cursor.fetchall())


def save_to_txt(filename, data):
    with open(filename, mode='w') as file:
        file.write("Liczba uruchomień transkacji: " + str(NUM_RUNS) + "\n")
        file.write("{:<15} {:<15} {:<15} {:<15}\n".format("Procedure", "Min Time (s)", "Max Time (s)", "Avg Time (s)"))
        for row in data:
            file.write("".join(map(str, row)) + "\n")


def save_plans(filename, data):
    with open(filename, mode='w') as file:
        file.write("Zebrane plany zapytań:")
        file.write("-" * 80 + "\n")
        for row in data:
            file.write("-" * 80 + "\n")
            file.write("Transakcja:\n")
            file.write("".join(str(row) + "\n"))

def main():
    results = []
    plans = []      # Zapisuje plany wykonania do oddzielnego pliku
    PROCEDURES = load_queries_from_file("transakcje.txt")

    try:
        conn = pg8000.connect(**DB_SETTINGS)
        conn.autocommit = True
        cursor = conn.cursor()

        # Sprawdzanie liczby rekordów
        insufficient_data = check_record_counts(cursor)
        if insufficient_data:
            print("Zatrzymano wykonanie testów obciążenia z powodu niewystarczającej liczby danych.")
            return

        times = {procedure: [] for procedure in PROCEDURES}

        for run in range(1, NUM_RUNS + 1):
            print(f"Running round {run}...")

            for procedure in PROCEDURES:
                query_plan = None
                exec_time = execute_procedure(cursor, procedure)
                times[procedure].append(exec_time)
                query_plan = get_query_plan(cursor, procedure)
                plans.append(query_plan)  # Dodajemy plan dla każdego uruchomienia transakcji

        count = 1
        for procedure in PROCEDURES:
            min_time = round(min(times[procedure]), 3)
            max_time = round(max(times[procedure]), 3)
            avg_time = round(sum(times[procedure]) / len(times[procedure]), 3)
            results.append("-" * 80)
            results.append(f"Transakcja {count:}:   {min_time:<15} {max_time:<15} {avg_time:<15}")
            count += 1

        save_to_txt(OUTPUT_FILE, results)
        print(f"Benchmark results saved to {OUTPUT_FILE}")
        save_plans(OUTPUT_PLANS_FILE, plans)
        print(f"Plans saved to {OUTPUT_PLANS_FILE}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    main()
