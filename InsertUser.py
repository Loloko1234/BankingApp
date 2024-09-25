import psycopg2
from datetime import datetime
import random
import string

db_params = {
    'dbname': 'banking_db',
    'user': 'postgres',
    'password': 'Loloko1234',
    'host': 'localhost',
    'port': '5432'
}

def generate_account_number(length=10):
    return ''.join(random.choices(string.digits, k=length))

def create_user(login, password):
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (login, password, created_at, updated_at) VALUES (%s, %s, %s, %s) RETURNING id;",
            (login, password, datetime.now(), datetime.now())
        )
        user_id = cursor.fetchone()[0]
        conn.commit()
        print(f"User created with ID: {user_id}")
        return user_id
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def create_account(user_id, balance):
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        account_number = generate_account_number()
        cursor.execute(
            "INSERT INTO accounts (user_id, account_number, balance, created_at, updated_at) VALUES (%s, %s, %s, %s, %s) RETURNING id;",
            (user_id, account_number, balance, datetime.now(), datetime.now())
        )
        account_id = cursor.fetchone()[0]
        conn.commit()
        print(f"Account created with ID: {account_id} and Account Number: {account_number}")
        return account_id
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def create_transaction(account_id, amount, description):
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO transactions (account_id, amount, transaction_date, description) VALUES (%s, %s, %s, %s) RETURNING id;",
            (account_id, amount, datetime.now(), description)
        )
        transaction_id = cursor.fetchone()[0]
        conn.commit()
        print(f"Transaction created with ID: {transaction_id}")
        return transaction_id
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    user_id = create_user('1234', '1234')
    if user_id:
        account_id = create_account(user_id, 1300)
        if account_id:
            create_transaction(account_id, 100, 'Initial deposit')