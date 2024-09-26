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

def execute_query(query, params=None):
    conn = connection_pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            if query.strip().upper().startswith("SELECT"):
                result = cursor.fetchall()
            else:
                result = None
                conn.commit()
            print(f"Query result: {result}")  # Debug print
            return result
    except Exception as e:
        print(f"Database error: {e}")  # Debug print
        messagebox.showerror("Error", f"Database error: {e}")
        return None
    finally:
        connection_pool.putconn(conn)

def check_balance(user_id):
    result = execute_query("SELECT balance FROM accounts WHERE user_id = %s;", (user_id,))
    print(f"Check balance result: {result}")  # Debug print
    return result[0][0] if result and result[0] else None  # Return the first element of the first tuple

def login():
    username = entry_username.get()
    password = entry_password.get()
    
    result = execute_query("SELECT id FROM users WHERE login = %s AND password = %s;", (username, password))
    if result:
        user_id = result[0][0]  # Get the first element of the first tuple
        open_banking_page(user_id)
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

def request_loan(user_id, loan_amount_entry, balance_label):
    amount = loan_amount_entry.get()
    if amount.isdigit():
        amount = int(amount)
        if amount > 0:
            current_balance = check_balance(user_id)
            # Simple loan approval logic: loan amount should not exceed 2 times the current balance
            if amount <= current_balance * 2:
                execute_query("UPDATE accounts SET balance = balance + %s WHERE user_id = %s;", (amount, user_id))
                execute_query("INSERT INTO loans (user_id, amount, status) VALUES (%s, %s, 'approved');", (user_id, amount))
                new_balance = check_balance(user_id)
                balance_label.config(text=f"Your balance is: ${new_balance:.2f}")
                messagebox.showinfo("Loan Approved", f"Your loan of ${amount} has been approved and added to your account.")
                loan_amount_entry.delete(0, tk.END)  # Clear the entry field
            else:
                messagebox.showerror("Loan Denied", "Loan amount exceeds your eligible limit.")
        else:
            messagebox.showerror("Invalid Amount", "Please enter a positive amount.")
    else:
        messagebox.showerror("Invalid Input", "Please enter a valid number.")

def view_loan_history(tree, user_id):
    print(f"Fetching loan history for user_id: {user_id}")  # Debug print
    # Clear existing items
    for item in tree.get_children():
        tree.delete(item)
    
    loans = execute_query("SELECT amount, status, created_at FROM loans WHERE user_id = %s ORDER BY created_at DESC;", (user_id,))
    print(f"Loans fetched: {loans}")  # Debug print
    if loans:
        for loan in loans:
            tree.insert('', 'end', values=(f"${loan[0]:.2f}", loan[1], loan[2].strftime("%Y-%m-%d %H:%M:%S")))
        print(f"Inserted {len(loans)} loans into the tree")  # Debug print
    else:
        tree.insert('', 'end', values=('No loan history', '', ''))
        print("No loans found, inserted 'No loan history' message")  # Debug print

def open_banking_page(user_id):
    app.withdraw()
    balance = check_balance(user_id)
    print(f"Balance retrieved: {balance}")  # Debug print
    if balance is not None:
        banking_page = tk.Toplevel(app)
        banking_page.title("Banking Page")
        banking_page.geometry("500x600")
        banking_page.configure(bg="#f0f0f0")
        
        style = ttk.Style(banking_page)
        style.configure("TLabel", font=("Arial", 14), background="#f0f0f0")
        style.configure("TButton", font=("Arial", 12))
        style.configure("TEntry", font=("Arial", 12))
        style.configure("TNotebook", background="#f0f0f0")
        style.configure("TFrame", background="#f0f0f0")
        
        # Convert balance to float to ensure it's a number
        balance_float = float(balance)
        balance_label = ttk.Label(banking_page, text=f"Your balance is: ${balance_float:.2f}", style="TLabel")
        balance_label.pack(pady=20)
        
        # Create notebook (tabbed interface)
        notebook = ttk.Notebook(banking_page)
        notebook.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Transactions tab
        transactions_frame = ttk.Frame(notebook)
        notebook.add(transactions_frame, text="Transactions")
        
        # Withdraw frame
        withdraw_frame = ttk.Frame(transactions_frame)
        withdraw_frame.pack(pady=10)
        
        withdraw_label = ttk.Label(withdraw_frame, text="Withdraw amount: $", style="TLabel")
        withdraw_label.pack(side=tk.LEFT)
        
        withdraw_entry = ttk.Entry(withdraw_frame, width=10)
        withdraw_entry.pack(side=tk.LEFT, padx=5)
        
        withdraw_button = ttk.Button(withdraw_frame, text="Withdraw", 
                                     command=lambda: withdraw(user_id, withdraw_entry, balance_label))
        withdraw_button.pack(side=tk.LEFT)
        
        # Deposit frame
        deposit_frame = ttk.Frame(transactions_frame)
        deposit_frame.pack(pady=10)
        
        deposit_label = ttk.Label(deposit_frame, text="Deposit amount: $", style="TLabel")
        deposit_label.pack(side=tk.LEFT)
        
        deposit_entry = ttk.Entry(deposit_frame, width=10)
        deposit_entry.pack(side=tk.LEFT, padx=5)
        
        deposit_button = ttk.Button(deposit_frame, text="Deposit", 
                                    command=lambda: deposit(user_id, deposit_entry, balance_label))
        deposit_button.pack(side=tk.LEFT)
        
        # Loan tab
        loan_frame = ttk.Frame(notebook)
        notebook.add(loan_frame, text="Loans")
        
        # Loan request frame
        loan_request_frame = ttk.Frame(loan_frame)
        loan_request_frame.pack(pady=10)
        
        loan_label = ttk.Label(loan_request_frame, text="Loan amount: $", style="TLabel")
        loan_label.pack(side=tk.LEFT)
        
        loan_entry = ttk.Entry(loan_request_frame, width=10)
        loan_entry.pack(side=tk.LEFT, padx=5)
        
        loan_button = ttk.Button(loan_request_frame, text="Request Loan", 
                                 command=lambda: request_loan(user_id, loan_entry, balance_label))
        loan_button.pack(side=tk.LEFT)
        
        # Loan history frame
        loan_history_frame = ttk.Frame(loan_frame)
        loan_history_frame.pack(pady=10, expand=True, fill="both")
        
        loan_history_tree = ttk.Treeview(loan_history_frame, columns=('Amount', 'Status', 'Date'), show='headings')
        loan_history_tree.heading('Amount', text='Amount')
        loan_history_tree.heading('Status', text='Status')
        loan_history_tree.heading('Date', text='Date')
        loan_history_tree.pack(expand=True, fill="both")
        
        # Scrollbar for the treeview
        scrollbar = ttk.Scrollbar(loan_history_frame, orient="vertical", command=loan_history_tree.yview)
        scrollbar.pack(side="right", fill="y")
        loan_history_tree.configure(yscrollcommand=scrollbar.set)
        
        # Load loan history
        print(f"Calling view_loan_history with user_id: {user_id}")  # Debug print
        view_loan_history(loan_history_tree, user_id)
        
        # Refresh button for loan history
        refresh_button = ttk.Button(loan_frame, text="Refresh Loan History", 
                                    command=lambda: view_loan_history(loan_history_tree, user_id))
        refresh_button.pack(pady=10)
        
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
                execute_query("UPDATE accounts SET balance = balance - %s WHERE user_id = %s;", (amount, user_id))
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

def deposit(user_id, deposit_entry, balance_label):
    amount = deposit_entry.get()
    if amount.isdigit():
        amount = int(amount)
        if amount > 0:
            execute_query("UPDATE accounts SET balance = balance + %s WHERE user_id = %s;", (amount, user_id))
            new_balance = check_balance(user_id)
            if new_balance is not None:
                balance_label.config(text=f"Your balance is: ${new_balance:.2f}")
                messagebox.showinfo("Deposit Successful", f"${amount} has been deposited to your account.")
                deposit_entry.delete(0, tk.END)  # Clear the entry field
            else:
                messagebox.showerror("Error", "Failed to update balance.")
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