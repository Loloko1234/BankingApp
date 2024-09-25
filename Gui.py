import tkinter as tk
import psycopg2

db_params = {
    'dbname': 'banking_db',
    'user': 'postgres',
    'password': 'Loloko1234',
    'host': 'localhost',
    'port': '5432'
}

def check_balance(user_id):
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM accounts WHERE user_id = %s;", (user_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def login():
    username = entry_username.get()
    password = entry_password.get()
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE login = %s AND password = %s;", (username, password))
        result = cursor.fetchone()
        if result:
            user_id = result[0]
            open_banking_page(user_id)
        else:
            print("Invalid username or password.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def open_banking_page(user_id):
    app.withdraw()  # Hide the login window
    balance = check_balance(user_id)
    if balance is not None:
        banking_page = tk.Toplevel(app)
        banking_page.title("Banking Page")
        balance_label = tk.Label(banking_page, text=f"Your balance is: {balance}")
        balance_label.pack(pady=20)
    else:
        print("Error: Could not retrieve balance.")

# Create the main application window
app = tk.Tk()
app.title("Login Page")

# Create and place the username label and entry
label_username = tk.Label(app, text="Username:")
label_username.pack(pady=10)
entry_username = tk.Entry(app)
entry_username.pack(pady=10)

# Create and place the password label and entry
label_password = tk.Label(app, text="Password:")
label_password.pack(pady=10)
entry_password = tk.Entry(app, show="*")
entry_password.pack(pady=10)

# Create and place the login button
button_login = tk.Button(app, text="Login", command=login)
button_login.pack(pady=20)

# Run the application
app.mainloop()