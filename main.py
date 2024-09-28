import tkinter as tk
from psycopg2 import pool
from database_manager import DatabaseManager
from Gui import BankingGUI

def main():
    connection_pool = pool.SimpleConnectionPool(1, 10,
    database='banking_db',
    user='postgres',
    password='Loloko1234',
    host='localhost',
    port='5432'
)

    db_manager = DatabaseManager(connection_pool)

    root = tk.Tk()
    root.title("BANK")
    root.geometry("600x400")
    app = BankingGUI(root, db_manager)
    root.mainloop()

if __name__ == "__main__":
    main()