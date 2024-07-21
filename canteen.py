import streamlit as st
import sqlite3

# Initialize database connection
def init_db():
    conn = sqlite3.connect('canteen.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            card_id TEXT UNIQUE NOT NULL,
            balance REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Add new user to the database
def add_user(name, card_id):
    conn = sqlite3.connect('canteen.db')
    c = conn.cursor()
    c.execute('INSERT INTO users (name, card_id, balance) VALUES (?, ?, ?)', (name, card_id, 0.00))
    conn.commit()
    conn.close()

# Get user details by card ID
def get_user_by_card_id(card_id):
    conn = sqlite3.connect('canteen.db')
    c = conn.cursor()
    c.execute('SELECT name, balance FROM users WHERE card_id = ?', (card_id,))
    user = c.fetchone()
    conn.close()
    return user

# Update user balance
def update_balance(card_id, amount):
    conn = sqlite3.connect('canteen.db')
    c = conn.cursor()
    c.execute('UPDATE users SET balance = balance + ? WHERE card_id = ?', (amount, card_id))
    conn.commit()
    conn.close()

# Main page
def main_page():
    st.title("XYZ Company's Canteen Management System")
    st.subheader("Main Page")
    
    if st.button("New User"):
        st.session_state.page = "New User"
    if st.button("Existing User"):
        st.session_state.page = "Existing User"

# New User page
def new_user_page():
    st.title("XYZ Company's Canteen Management System")
    st.subheader("Register New User")

    name = st.text_input("Name", key="new_user_name")
    card_id = st.text_input("Card ID", key="new_user_card_id")

    status_message = st.empty()

    if st.button("Confirm"):
        if name and card_id:
            try:
                add_user(name, card_id)
                status_message.success("User added successfully!")
            except sqlite3.IntegrityError:
                status_message.error("Card ID already exists.")
        else:
            status_message.error("Please fill in all fields.")

    if st.button("Back to Main Page"):
        st.session_state.page = "Main Page"
        st.experimental_rerun()

# Existing User page
def existing_user_page():
    st.title("XYZ Company's Canteen Management System")
    st.subheader("Top Up Card")

    if "card_id" not in st.session_state:
        st.session_state.card_id = ""
    if "user" not in st.session_state:
        st.session_state.user = None
    if "amount" not in st.session_state:
        st.session_state.amount = 0.00

    card_id = st.text_input("Card ID", value=st.session_state.card_id, key="existing_user_card_id")
    
    status_message = st.empty()

    if st.button("Confirm Card ID"):
        if card_id:
            user = get_user_by_card_id(card_id)
            if user:
                st.session_state.user = user
                st.session_state.card_id = card_id
                st.session_state.amount = 0.00
            else:
                status_message.error("Card does not exist. Please enter a valid Card ID.")
        else:
            status_message.error("Please enter a Card ID.")
    
    if st.session_state.user:
        user = st.session_state.user
        st.text_input("Name", value=user[0], disabled=True, key="user_name")
        current_balance = st.number_input("Current Balance", value=user[1], format="%.2f", disabled=True)
        amount = st.number_input("Amount to Top Up", min_value=0.00, format="%.2f", key="top_up_amount", value=st.session_state.amount)
        
        if st.button("Confirm Top Up"):
            if amount > 0:
                update_balance(st.session_state.card_id, amount)
                user = get_user_by_card_id(st.session_state.card_id)
                if user:
                    st.session_state.user = user
                    st.session_state.amount = amount
                    st.write(f"Updated Balance: ${user[1]:.2f}")
                    status_message.success("Card topped up successfully!")
                else:
                    status_message.error("Failed to update balance.")
            else:
                status_message.error("Amount must be greater than zero.")
    
    if st.button("Back to Main Page"):
        st.session_state.page = "Main Page"
        st.session_state.card_id = ""
        st.session_state.user = None
        st.session_state.amount = 0.00
        st.experimental_rerun()

# Manage navigation
def main():
    if 'page' not in st.session_state:
        st.session_state.page = "Main Page"
    
    if st.session_state.page == "Main Page":
        main_page()
    elif st.session_state.page == "New User":
        new_user_page()
    elif st.session_state.page == "Existing User":
        existing_user_page()

if __name__ == '__main__':
    init_db()
    main()
