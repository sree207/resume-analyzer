import streamlit as st
import sqlite3
import bcrypt
import re  # Import the re module for regular expressions
import time  # Import the time module for delay

DB_NAME = "job_portal.db"

def is_password_valid(password):
    """
    Check if the password meets the following requirements:
    - Minimum length of 8
    - At least one alphabet
    - At least one special symbol
    - At least one number
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Za-z]", password):  # Check for at least one alphabet
        return False, "Password must contain at least one alphabet."
    if not re.search(r"[0-9]", password):  # Check for at least one number
        return False, "Password must contain at least one number."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):  # Check for at least one special symbol
        return False, "Password must contain at least one special symbol."
    return True, "Password is valid."

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

    # Display password creation criteria
    st.info("""
        **Password must meet the following criteria:**
        - Minimum length of 8 characters.
        - At least one alphabet (uppercase or lowercase).
        - At least one number.
        - At least one special symbol (e.g., !@#$%^&*(),.?":{}|<>).
    """)

    if st.button("Sign Up", key="signup_button"):
        # Check if passwords match
        if password != confirm_password:
            st.error("Passwords do not match.")
            return

        # Validate password
        is_valid, message = is_password_valid(password)
        if not is_valid:
            st.error(f"Password does not meet the requirements: {message}")
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