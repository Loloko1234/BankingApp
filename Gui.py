import tkinter as tk
from tkinter import ttk, messagebox
from account import Account
from loan import Loan
from decimal import Decimal, InvalidOperation
import logging

class BankingGUI:
    def __init__(self, master, db_manager):
        self.master = master
        self.db_manager = db_manager
        self.account = None
        self.loan = None
        self.create_login_page()

    def create_login_page(self):
        self.clear_window()
        self.login_frame = ttk.Frame(self.master)
        self.login_frame.pack(padx=10, pady=10)

        ttk.Label(self.login_frame, text="Username:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.username_entry = ttk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.login_frame, text="Password:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.password_entry = ttk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(self.login_frame, text="Login", command=self.login).grid(row=2, column=0, columnspan=2, pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        user_id = self.db_manager.execute_query("SELECT id FROM users WHERE login = %s AND password = %s", (username, password))
        if user_id:
            self.account = Account(user_id[0][0], self.db_manager)
            self.loan = Loan(user_id[0][0], self.db_manager)
            self.open_main_page()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def open_main_page(self):
        self.clear_window()
        main_frame = ttk.Frame(self.master)
        main_frame.pack(padx=10, pady=10)

        self.balance_label = ttk.Label(main_frame, text=f"Balance: ${self.account.check_balance():.2f}", font=("Arial", 24))
        self.balance_label.pack(pady=20)

        ttk.Button(main_frame, text="Transactions", command=self.open_transaction_page).pack(pady=10)
        ttk.Button(main_frame, text="Loans", command=self.open_loan_page).pack(pady=10)
        ttk.Button(main_frame, text="Logout", command=self.create_login_page).pack(pady=10)

    def open_transaction_page(self):
        self.clear_window()
        transaction_frame = ttk.Frame(self.master)
        transaction_frame.pack(padx=10, pady=10)

        self.balance_label = ttk.Label(transaction_frame, text=f"Balance: ${self.account.check_balance():.2f}", font=("Arial", 18))
        self.balance_label.pack(pady=10)

        self.create_transaction_frame(transaction_frame, "deposit")
        self.create_transaction_frame(transaction_frame, "withdraw")

        ttk.Button(transaction_frame, text="Back to Main", command=self.open_main_page).pack(pady=10)

    def create_transaction_frame(self, parent, operation):
        frame = ttk.Frame(parent)
        frame.pack(pady=5)

        ttk.Label(frame, text=f"{operation.capitalize()} amount:").pack(side=tk.LEFT)
        amount_entry = ttk.Entry(frame, width=10)
        amount_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text=operation.capitalize(), 
                   command=lambda: self.transaction(amount_entry, operation)).pack(side=tk.LEFT)

    def transaction(self, amount_entry, operation):
        try:
            amount = Decimal(amount_entry.get())
            if amount <= 0:
                raise ValueError("Amount must be positive")
            new_balance = self.account.update_balance(amount, operation)
            self.balance_label.config(text=f"Balance: ${new_balance:.2f}")
            messagebox.showinfo("Success", f"{operation.capitalize()} successful")
            amount_entry.delete(0, tk.END)
        except (InvalidOperation, ValueError) as e:
            messagebox.showerror("Error", str(e))

    def open_loan_page(self):
        self.clear_window()
        loan_frame = ttk.Frame(self.master)
        loan_frame.pack(padx=10, pady=10)

        self.balance_label = ttk.Label(loan_frame, text=f"Balance: ${self.account.check_balance():.2f}", font=("Arial", 18))
        self.balance_label.pack(pady=10)

        self.create_loan_request_frame(loan_frame)
        self.create_loan_payment_frame(loan_frame)
        self.create_loan_history_frame(loan_frame)

        ttk.Button(loan_frame, text="Back to Main", command=self.open_main_page).pack(pady=10)

    def create_loan_request_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="Request Loan")
        frame.pack(pady=5, fill="x")

        ttk.Label(frame, text="Loan amount:").pack(side=tk.LEFT)
        self.loan_amount_entry = ttk.Entry(frame, width=10)
        self.loan_amount_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(frame, text="Interest rate:").pack(side=tk.LEFT)
        self.interest_rate_entry = ttk.Entry(frame, width=5)
        self.interest_rate_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="Request Loan", command=self.request_loan).pack(side=tk.LEFT)

    def create_loan_payment_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="Pay Loan")
        frame.pack(pady=5, fill="x")

        ttk.Label(frame, text="Loan ID:").pack(side=tk.LEFT)
        self.loan_id_entry = ttk.Entry(frame, width=5)
        self.loan_id_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(frame, text="Payment amount:").pack(side=tk.LEFT)
        self.payment_amount_entry = ttk.Entry(frame, width=10)
        self.payment_amount_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="Pay Loan", command=self.pay_loan).pack(side=tk.LEFT)

    def create_loan_history_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="Loan History")
        frame.pack(pady=5, fill="both", expand=True)

        self.loan_history_tree = ttk.Treeview(frame, columns=("ID", "Amount", "Interest", "Remaining", "Status", "Date"), show="headings", height=5)
        for col in self.loan_history_tree["columns"]:
            self.loan_history_tree.heading(col, text=col)
            self.loan_history_tree.column(col, width=100)
        self.loan_history_tree.pack(pady=5, fill="both", expand=True)

        self.view_loan_history()

    def request_loan(self):
        try:
            amount = Decimal(self.loan_amount_entry.get())
            interest_rate = Decimal(self.interest_rate_entry.get())
            if amount <= 0 or interest_rate < 0:
                raise ValueError("Invalid amount or interest rate")
            self.loan.request_loan(amount, interest_rate)
            new_balance = self.account.update_balance(amount, "deposit")
            self.balance_label.config(text=f"Balance: ${new_balance:.2f}")
            messagebox.showinfo("Success", "Loan request successful")
            self.loan_amount_entry.delete(0, tk.END)
            self.interest_rate_entry.delete(0, tk.END)
            self.view_loan_history()
        except (InvalidOperation, ValueError) as e:
            messagebox.showerror("Error", str(e))

    def pay_loan(self):
        try:
            loan_id = int(self.loan_id_entry.get())
            payment_amount = Decimal(self.payment_amount_entry.get())
            if payment_amount <= 0:
                raise ValueError("Payment amount must be positive")
            success, message = self.loan.pay_loan(loan_id, payment_amount)
            if success:
                new_balance = self.account.update_balance(payment_amount, "withdraw")
                self.balance_label.config(text=f"Balance: ${new_balance:.2f}")
                messagebox.showinfo("Success", message)
                self.loan_id_entry.delete(0, tk.END)
                self.payment_amount_entry.delete(0, tk.END)
                self.view_loan_history()
            else:
                messagebox.showerror("Error", message)
        except (ValueError, InvalidOperation) as e:
            messagebox.showerror("Error", str(e))

    def view_loan_history(self):
        for i in self.loan_history_tree.get_children():
            self.loan_history_tree.delete(i)
        loans = self.loan.get_loan_history()
        for loan in loans:
            self.loan_history_tree.insert("", "end", values=loan)

    def clear_window(self):
        for widget in self.master.winfo_children():
            widget.destroy()