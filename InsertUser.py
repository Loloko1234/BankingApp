import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import random
import string

# Database connection parameters
dbname = "banking_db"
user = "postgres"
password = "Loloko1234"
host = "localhost"
port = "5432"

# Connect to PostgreSQL
conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()

# Create users table if it doesn't exist
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    login VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(50) NOT NULL
)
""")

# Create accounts table if it doesn't exist
cur.execute("""
CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    account_number VARCHAR(20) UNIQUE NOT NULL,
    balance DECIMAL(10, 2) DEFAULT 0
)
""")

# Create loans table if it doesn't exist
cur.execute("""
CREATE TABLE IF NOT EXISTS loans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    amount DECIMAL(10, 2),
    interest_rate DECIMAL(5, 2),
    remaining_balance DECIMAL(10, 2),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Function to generate a random account number
def generate_account_number():
    return ''.join(random.choices(string.digits, k=10))

# Sample user data
users = [
    ("john4", "password123"),
]

# Insert users and create accounts
for login, password in users:
    cur.execute("INSERT INTO users (login, password) VALUES (%s, %s) ON CONFLICT (login) DO NOTHING RETURNING id", (login, password))
    user_id = cur.fetchone()
    if user_id:
        user_id = user_id[0]
        account_number = generate_account_number()
        cur.execute("INSERT INTO accounts (user_id, account_number, balance) VALUES (%s, %s, %s)", (user_id, account_number, 1000))
        print(f"User {login} inserted with account number {account_number} and initial balance of $1000")
    else:
        print(f"User {login} already exists")

# Sample loan data
loans = [
    ("john4", 500, "approved"),
]

# Insert sample loans
for login, amount, status in loans:
    cur.execute("SELECT id FROM users WHERE login = %s", (login,))
    user_id = cur.fetchone()
    if user_id:
        user_id = user_id[0]
        cur.execute("INSERT INTO loans (user_id, amount, status) VALUES (%s, %s, %s)", (user_id, amount, status))
        print(f"Loan of ${amount} for user {login} inserted with status: {status}")
    else:
        print(f"User {login} not found, loan not inserted")

# Dodaj na końcu skryptu InsertUser.py

# Sprawdź, czy kolumna interest_rate istnieje
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='loans' AND column_name='interest_rate'")
if not cur.fetchone():
    # Jeśli kolumna nie istnieje, dodaj ją
    cur.execute("ALTER TABLE loans ADD COLUMN interest_rate DECIMAL(5, 2) DEFAULT 5.0")
    print("Dodano kolumnę interest_rate do tabeli loans")

# Sprawdź, czy kolumna remaining_balance istnieje
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='loans' AND column_name='remaining_balance'")
if not cur.fetchone():
    # Jeśli kolumna nie istnieje, dodaj ją
    cur.execute("ALTER TABLE loans ADD COLUMN remaining_balance DECIMAL(10, 2)")
    print("Dodano kolumnę remaining_balance do tabeli loans")

# Zaktualizuj istniejące wiersze, ustawiając wartości domyślne
cur.execute("UPDATE loans SET interest_rate = 5.0, remaining_balance = amount WHERE interest_rate IS NULL OR remaining_balance IS NULL")
print("Zaktualizowano istniejące wiersze w tabeli loans")

conn.commit()

# Commit changes and close connection
conn.commit()
cur.close()
conn.close()

print("Sample data insertion completed.")