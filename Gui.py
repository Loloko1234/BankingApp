import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from psycopg2 import pool

# Create a connection pool
connection_pool = psycopg2.pool.SimpleConnectionPool(
    1, 20,
    dbname='banking_db',
    user='postgres',
    password='Loloko1234',
    host='localhost',
    port='5432'
)

def execute_query(query, params=None, fetch=True):
    conn = connection_pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            if fetch:
                result = cursor.fetchone()
            else:
                result = None
            conn.commit()  # Commit the transaction
            return result
    except Exception as e:
        conn.rollback()  # Rollback in case of error
        messagebox.showerror("Error", f"Database error: {e}")
        return None
    finally:
        connection_pool.putconn(conn)

def check_balance(user_id):
    result = execute_query("SELECT balance FROM accounts WHERE user_id = %s;", (user_id,))
    return result[0] if result else None

def login():
    username = entry_username.get()
    password = entry_password.get()
    
    result = execute_query("SELECT id FROM users WHERE login = %s AND password = %s;", (username, password))
    if result:
        user_id = result[0]
        open_banking_page(user_id)
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

def open_banking_page(user_id):
    app.withdraw()
    balance = check_balance(user_id)
    if balance is not None:
        banking_page = tk.Toplevel(app)
        banking_page.title("Banking Page")
        banking_page.geometry("400x400")
        banking_page.configure(bg="#f0f0f0")
        
        style = ttk.Style(banking_page)
        style.configure("TLabel", font=("Arial", 14), background="#f0f0f0")
        style.configure("TButton", font=("Arial", 12))
        style.configure("TEntry", font=("Arial", 12))
        
        balance_label = ttk.Label(banking_page, text=f"Your balance is: ${balance:.2f}", style="TLabel")
        balance_label.pack(pady=20)
        
        # Add withdraw input and button
        withdraw_frame = ttk.Frame(banking_page)
        withdraw_frame.pack(pady=10)
        
        withdraw_label = ttk.Label(withdraw_frame, text="Withdraw amount: $", style="TLabel")
        withdraw_label.pack(side=tk.LEFT)
        
        withdraw_entry = ttk.Entry(withdraw_frame, width=10)
        withdraw_entry.pack(side=tk.LEFT, padx=5)
        
        withdraw_button = ttk.Button(withdraw_frame, text="Withdraw", 
                                     command=lambda: withdraw(user_id, withdraw_entry, balance_label))
        withdraw_button.pack(side=tk.LEFT)
        
        logout_button = ttk.Button(banking_page, text="Logout", command=lambda: logout(banking_page))
        logout_button.pack(pady=20)
    else:
        messagebox.showerror("Error", "Could not retrieve balance.")

def logout(banking_page):
    banking_page.destroy()
    app.deiconify()

def withdraw(user_id, withdraw_entry, balance_label):
    amount = withdraw_entry.get()
    if amount.isdigit():
        amount = int(amount)
        if amount > 0:
            current_balance = check_balance(user_id)
            if amount <= current_balance:
                execute_query("UPDATE accounts SET balance = balance - %s WHERE user_id = %s;", (amount, user_id), fetch=False)
                new_balance = check_balance(user_id)
                if new_balance is not None:
                    balance_label.config(text=f"Your balance is: ${new_balance:.2f}")
                    messagebox.showinfo("Withdrawal Successful", f"${amount} has been withdrawn from your account.")
                    withdraw_entry.delete(0, tk.END)  # Clear the entry field
                else:
                    messagebox.showerror("Error", "Failed to update balance.")
            else:
                messagebox.showerror("Insufficient Funds", "You do not have enough funds in your account.")
        else:
            messagebox.showerror("Invalid Amount", "Please enter a positive amount.")
    else:
        messagebox.showerror("Invalid Input", "Please enter a valid number.")

# Create the main application window
app = tk.Tk()
app.title("Banking Login")
app.geometry("300x400")
app.configure(bg="#f0f0f0")

style = ttk.Style(app)
style.configure("TLabel", font=("Arial", 12), background="#f0f0f0")
style.configure("TEntry", font=("Arial", 12))
style.configure("TButton", font=("Arial", 12))

frame = ttk.Frame(app, padding="30 30 30 30", style="TFrame")
frame.pack(expand=True, fill="both")

# Create and place the username label and entry
label_username = ttk.Label(frame, text="Username:", style="TLabel")
label_username.grid(row=0, column=0, sticky="w", pady=(0, 5))
entry_username = ttk.Entry(frame, width=25)
entry_username.grid(row=1, column=0, pady=(0, 15))

# Create and place the password label and entry
label_password = ttk.Label(frame, text="Password:", style="TLabel")
label_password.grid(row=2, column=0, sticky="w", pady=(0, 5))
entry_password = ttk.Entry(frame, show="*", width=25)
entry_password.grid(row=3, column=0, pady=(0, 20))

# Create and place the login button
button_login = ttk.Button(frame, text="Login", command=login, width=20)
button_login.grid(row=4, column=0, pady=(10, 0))

# Run the application
app.mainloop()

# Close the connection pool when the application exits
connection_pool.closeall()