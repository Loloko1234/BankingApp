import psycopg2

# Database connection parameters
db_params = {
    'dbname': 'banking_db',
    'user': 'postgres',
    'password': 'Loloko1234',
    'host': 'localhost',
    'port': '5432'
}

def CheckUser(login, password):
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE login = %s AND password = %s;", (login, password))
        rows = cursor.fetchall()
        if rows:
            return True
        else:
            return False
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        return False