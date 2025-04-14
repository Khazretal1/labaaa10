import psycopg2
import csv


def connect_db():
    return psycopg2.connect(dbname="phonebook", user="postgres", password="newpassword", host="localhost", port="5433")

def create_phonebook_table():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS phonebook (
                    id SERIAL PRIMARY KEY,
                    first_name VARCHAR(50),
                    phone VARCHAR(15) UNIQUE
                );
            """)
            conn.commit()

def insert_from_csv(filepath):
    with connect_db() as conn:
        cur = conn.cursor()
        with open(filepath, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file, delimiter=';')
            next(reader, None)
            for row in reader:
                cur.execute(
                    "INSERT INTO phonebook (first_name, phone) VALUES (%s, %s) ON CONFLICT (phone) DO NOTHING;",
                    row
                )
        conn.commit()

def insert_from_console():
    first_name = input("First name: ")
    phone = input("Phone: ")
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO phonebook (first_name, phone) VALUES (%s, %s) ON CONFLICT (phone) DO NOTHING;", (first_name, phone))
            conn.commit()

def update_phonebook_entry(identifier, new_first_name=None, new_phone=None):
    with connect_db() as conn:
        with conn.cursor() as cur:
            if new_first_name:
                cur.execute("UPDATE phonebook SET first_name = %s WHERE phone = %s;", (new_first_name, identifier))
            if new_phone:
                cur.execute("UPDATE phonebook SET phone = %s WHERE phone = %s;", (new_phone, identifier))
            conn.commit()

def query_phonebook(filter_by=None, value=None):
    with connect_db() as conn:
        with conn.cursor() as cur:
            if filter_by == 'first_name':
                cur.execute("SELECT * FROM phonebook WHERE first_name = %s;", (value,))
            elif filter_by == 'phone':
                cur.execute("SELECT * FROM phonebook WHERE phone = %s;", (value,))
            else:
                cur.execute("SELECT * FROM phonebook;")
            rows = cur.fetchall()
            for row in rows:
                print(row)

def delete_from_phonebook(identifier):
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM phonebook WHERE first_name = %s OR phone = %s;", (identifier, identifier))
            conn.commit()

if __name__ == "__main__":
    create_phonebook_table()
    while True:
        print("\nPhoneBook Menu")
        print("1. Insert from CSV")
        print("2. Insert from Console")
        print("3. Update Entry")
        print("4. Query PhoneBook")
        print("5. Delete Entry")
        print("6. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            insert_from_csv("./data.csv")
        elif choice == '2':
            insert_from_console()
        elif choice == '3':
            identifier = input("Enter the phone of the user to update: ")
            new_first_name = input("Enter new first name (or press Enter to skip): ")
            new_phone = input("Enter new phone (or press Enter to skip): ")
            update_phonebook_entry(identifier, new_first_name or None, new_phone or None)
        elif choice == '4':
            filter_by = input("Filter by (first_name/phone/none): ")
            value = None if filter_by == 'none' else input(f"Enter value for {filter_by}: ")
            query_phonebook(filter_by if filter_by != 'none' else None, value)
        elif choice == '5':
            identifier = input("Enter first name or phone to delete: ")
            delete_from_phonebook(identifier)
        elif choice == '6':
            break
        else:
            print("Invalid choice")