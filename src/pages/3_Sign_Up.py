import streamlit as st
import sqlite3
import bcrypt
import time  # Import the time module for delay

DB_NAME = "job_portal.db"

def signup_page():
    st.header("Sign Up")

    # Choose user type
    user_type = st.radio("Sign Up as:", ("Company", "Applicant"))

    # Sign Up form
    if user_type == "Company":
        company_name = st.text_input("Company Name")
    else:
        username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Re-enter Password", type="password")

    if st.button("Sign Up", key="signup_button"):
        if password != confirm_password:
            st.error("Passwords do not match.")
            return

        # Hash the password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode(), salt).decode()

        # Save to database
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            if user_type == "Company":
                cursor.execute("INSERT INTO companies (company_name, password) VALUES (?, ?)", (company_name, hashed_password))
            else:
                cursor.execute("INSERT INTO applicants (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            st.success("Account created successfully!")
            time.sleep(3)
            st.switch_page("pages/1_Home.py")
        except sqlite3.IntegrityError:
            st.error("Username or Company Name already exists.")
        conn.close()

def main():
    signup_page()

if __name__ == "__main__":
    main()