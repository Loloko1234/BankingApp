import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from psycopg2 import pool
import logging
from decimal import Decimal, InvalidOperation

# Create a connection pool
connection_pool = psycopg2.pool.SimpleConnectionPool(
    1, 20,
    dbname='banking_db',
    user='postgres',
    password='Loloko1234',
    host='localhost',
    port='5432'
)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def execute_query(query, params=None):
    logging.debug(f"Executing query: {query}")
    logging.debug(f"Query parameters: {params}")
    conn = connection_pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            if query.strip().upper().startswith("SELECT"):
                result = cursor.fetchall()
                logging.debug(f"Query result: {result}")
            else:
                result = None
                conn.commit()
                logging.debug("Query executed successfully (non-SELECT)")
            return result
    except Exception as e:
        logging.exception(f"Database error: {e}")
        messagebox.showerror("Error", f"Database error: {e}")
        return None
    finally:
        connection_pool.putconn(conn)

def check_balance(user_id):
    result = execute_query("SELECT balance FROM accounts WHERE user_id = %s;", (user_id,))
    return result[0][0] if result else Decimal('0')

def login():
    username = entry_username.get()
    password = entry_password.get()
    
    result = execute_query("SELECT id FROM users WHERE login = %s AND password = %s;", (username, password))
    if result:
        user_id = result[0][0]
        open_banking_page(user_id)
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

def request_loan(user_id, loan_amount_entry, interest_rate_entry, balance_label):
    amount = loan_amount_entry.get()
    interest_rate = interest_rate_entry.get()
    if amount.isdigit() and interest_rate.replace('.', '').isdigit():
        amount = int(amount)
        interest_rate = float(interest_rate)
        if amount > 0 and 0 <= interest_rate <= 100:
            current_balance = check_balance(user_id)
            if amount <= current_balance * 2:
                execute_query("UPDATE accounts SET balance = balance + %s WHERE user_id = %s;", (amount, user_id))
                execute_query("INSERT INTO loans (user_id, amount, interest_rate, remaining_balance, status) VALUES (%s, %s, %s, %s, 'active');", 
                              (user_id, amount, interest_rate, amount))
                new_balance = check_balance(user_id)
                balance_label.config(text=f"Your balance is: ${new_balance:.2f}")
                messagebox.showinfo("Loan Approved", f"Your loan of ${amount} at {interest_rate}% interest has been approved and added to your account.")
                loan_amount_entry.delete(0, tk.END)
                interest_rate_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Loan Denied", "Loan amount exceeds your eligible limit.")
        else:
            messagebox.showerror("Invalid Input", "Please enter a positive amount and a valid interest rate (0-100).")
    else:
        messagebox.showerror("Invalid Input", "Please enter valid numbers.")

def pay_loan(user_id, loan_id, payment_amount, balance_label, loan_history_tree):
    logging.debug("pay_loan function called")
    logging.debug(f"Loan ID: {loan_id}, Payment Amount: {payment_amount}")
    
    payment_amount = Decimal(str(payment_amount))  # Convert to Decimal
    
    if payment_amount <= Decimal('0'):
        logging.debug("Invalid payment amount")
        messagebox.showerror("Invalid Input", "Please enter a positive payment amount.")
        return
    
    loan = execute_query("SELECT remaining_balance FROM loans WHERE id = %s AND user_id = %s;", (loan_id, user_id))
    if loan:
        remaining_balance = loan[0][0]
        if payment_amount <= remaining_balance:
            current_balance = check_balance(user_id)
            if payment_amount <= current_balance:
                new_remaining = remaining_balance - payment_amount
                execute_query("UPDATE loans SET remaining_balance = %s WHERE id = %s;", (new_remaining, loan_id))
                execute_query("UPDATE accounts SET balance = balance - %s WHERE user_id = %s;", (payment_amount, user_id))
                if new_remaining == Decimal('0'):
                    execute_query("UPDATE loans SET status = 'paid' WHERE id = %s;", (loan_id,))
                new_balance = check_balance(user_id)
                balance_label.config(text=f"Your balance is: ${new_balance:.2f}")
                messagebox.showinfo("Payment Successful", f"You've paid ${payment_amount:.2f} towards your loan.")
                view_loan_history(loan_history_tree, user_id)  # Refresh loan history
            else:
                messagebox.showerror("Insufficient Funds", "You don't have enough balance to make this payment.")
        else:
            messagebox.showerror("Invalid Payment", "Payment amount exceeds the remaining balance.")
    else:
        messagebox.showerror("Loan Not Found", "The specified loan was not found or doesn't belong to you.")

def view_loan_history(tree, user_id):
    for item in tree.get_children():
        tree.delete(item)
    
    loans = execute_query("SELECT id, amount, interest_rate, remaining_balance, status, created_at FROM loans WHERE user_id = %s ORDER BY created_at DESC;", (user_id,))
    if loans:
        for loan in loans:
            tree.insert('', 'end', values=(loan[0], f"${loan[1]:.2f}", f"{loan[2]}%", f"${loan[3]:.2f}", loan[4], loan[5].strftime("%Y-%m-%d %H:%M:%S")))
    else:
        tree.insert('', 'end', values=('No loan history', '', '', '', '', ''))

def open_banking_page(user_id):
    logging.debug(f"user_id in open_banking_page: {user_id}")
    app.withdraw()
    balance = check_balance(user_id)
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
        
        balance_label = ttk.Label(banking_page, text=f"Your balance is: ${balance:.2f}", style="TLabel")
        balance_label.pack(pady=20)
        
        notebook = ttk.Notebook(banking_page)
        notebook.pack(expand=True, fill="both", padx=10, pady=10)
        
        transactions_frame = ttk.Frame(notebook)
        notebook.add(transactions_frame, text="Transactions")
        
        withdraw_frame = ttk.Frame(transactions_frame)
        withdraw_frame.pack(pady=10)
        
        withdraw_label = ttk.Label(withdraw_frame, text="Withdraw amount: $", style="TLabel")
        withdraw_label.pack(side=tk.LEFT)
        
        withdraw_entry = ttk.Entry(withdraw_frame, width=10)
        withdraw_entry.pack(side=tk.LEFT, padx=5)
        
        withdraw_button = ttk.Button(withdraw_frame, text="Withdraw", 
                                     command=lambda: withdraw(user_id, withdraw_entry, balance_label))
        withdraw_button.pack(side=tk.LEFT)
        
        deposit_frame = ttk.Frame(transactions_frame)
        deposit_frame.pack(pady=10)
        
        deposit_label = ttk.Label(deposit_frame, text="Deposit amount: $", style="TLabel")
        deposit_label.pack(side=tk.LEFT)
        
        deposit_entry = ttk.Entry(deposit_frame, width=10)
        deposit_entry.pack(side=tk.LEFT, padx=5)
        
        deposit_button = ttk.Button(deposit_frame, text="Deposit", 
                                    command=lambda: deposit(user_id, deposit_entry, balance_label))
        deposit_button.pack(side=tk.LEFT)
        
        loan_frame = ttk.Frame(notebook)
        notebook.add(loan_frame, text="Loans")
        
        loan_request_frame = ttk.Frame(loan_frame)
        loan_request_frame.pack(pady=10)
        
        loan_amount_label = ttk.Label(loan_request_frame, text="Loan amount: $", style="TLabel")
        loan_amount_label.pack(side=tk.LEFT)
        
        loan_amount_entry = ttk.Entry(loan_request_frame, width=10)
        loan_amount_entry.pack(side=tk.LEFT, padx=5)
        
        interest_rate_label = ttk.Label(loan_request_frame, text="Interest rate: %", style="TLabel")
        interest_rate_label.pack(side=tk.LEFT)
        
        interest_rate_entry = ttk.Entry(loan_request_frame, width=5)
        interest_rate_entry.pack(side=tk.LEFT, padx=5)
        
        loan_button = ttk.Button(loan_request_frame, text="Request Loan", 
                                 command=lambda: request_loan(user_id, loan_amount_entry, interest_rate_entry, balance_label))
        loan_button.pack(side=tk.LEFT)
        
        loan_history_frame = ttk.Frame(loan_frame)
        loan_history_frame.pack(pady=10, expand=True, fill="both")
        
        loan_history_tree = ttk.Treeview(loan_history_frame, columns=('ID', 'Amount', 'Interest', 'Remaining', 'Status', 'Date'), show='headings')
        loan_history_tree.heading('ID', text='ID')
        loan_history_tree.heading('Amount', text='Amount')
        loan_history_tree.heading('Interest', text='Interest')
        loan_history_tree.heading('Remaining', text='Remaining')
        loan_history_tree.heading('Status', text='Status')
        loan_history_tree.heading('Date', text='Date')
        loan_history_tree.pack(expand=True, fill="both")
        
        loan_payment_frame = ttk.Frame(loan_frame)
        loan_payment_frame.pack(pady=10)
        
        loan_id_label = ttk.Label(loan_payment_frame, text="Loan ID:", style="TLabel")
        loan_id_label.pack(side=tk.LEFT)
        
        loan_id_entry = ttk.Entry(loan_payment_frame, width=5)
        loan_id_entry.pack(side=tk.LEFT, padx=5)
        
        payment_amount_label = ttk.Label(loan_payment_frame, text="Payment amount: $", style="TLabel")
        payment_amount_label.pack(side=tk.LEFT)
        
        payment_amount_entry = ttk.Entry(loan_payment_frame, width=10)
        payment_amount_entry.pack(side=tk.LEFT, padx=5)
        
        def pay_loan_wrapper():
            try:
                loan_id = int(loan_id_entry.get())
                payment_amount = Decimal(payment_amount_entry.get())
                pay_loan(user_id, loan_id, payment_amount, balance_label, loan_history_tree)
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid numbers for loan ID and payment amount.")
            except InvalidOperation:
                messagebox.showerror("Invalid Input", "Please enter a valid number for payment amount.")
            except Exception as e:
                logging.exception("An error occurred in pay_loan_wrapper")
                messagebox.showerror("Error", f"An error occurred: {str(e)}")

        pay_loan_button = ttk.Button(loan_payment_frame, text="Pay Loan", command=pay_loan_wrapper)
        pay_loan_button.pack(side=tk.LEFT)
        
        view_loan_history(loan_history_tree, user_id)
        
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
                    withdraw_entry.delete(0, tk.END)
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
                deposit_entry.delete(0, tk.END)
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