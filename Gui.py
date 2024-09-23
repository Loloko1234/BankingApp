import customtkinter as ctk
from Login import CheckUser

# Initialize the main window
app = ctk.CTk()
app.geometry("400x300")
app.title("Login")

# Function to handle login button click
def login():
    username = entry_username.get()
    password = entry_password.get()
    if CheckUser(username, password):
        print("Login successful")
        open_banking_page()
    else:
        print("Login failed")

# Function to handle transition to the banking page
def open_banking_page():
    app.withdraw()  # Hide the login window
    app2 = ctk.CTk()  # Create a new window for the banking page
    app2.geometry("400x300")
    app2.title("Banking")
    
    # Add widgets to the banking page
    label = ctk.CTkLabel(app2, text="Welcome to the Banking Page!")
    label.pack(pady=20)
    
    # Run the banking page window
    app2.mainloop()

# Create and place the username label and entry
label_username = ctk.CTkLabel(app, text="Username:")
label_username.pack(pady=10)
entry_username = ctk.CTkEntry(app)
entry_username.pack(pady=10)

# Create and place the password label and entry
label_password = ctk.CTkLabel(app, text="Password:")
label_password.pack(pady=10)
entry_password = ctk.CTkEntry(app, show="*")
entry_password.pack(pady=10)

# Create and place the login button
button_login = ctk.CTkButton(app, text="Login", command=login)
button_login.pack(pady=20)

# Run the application
app.mainloop()