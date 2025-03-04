import streamlit as st
import sqlite3
import bcrypt
import time  # Import the time module for delay

DB_NAME = "job_portal.db"

def login_page():
    st.header("Login")

    # Choose user type
    user_type = st.radio("Login as:", ("Company", "Applicant"))

    # Login form
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", key="login_button"):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        if user_type == "Company":
            cursor.execute("SELECT password FROM companies WHERE company_name = ?", (username,))
        else:
            cursor.execute("SELECT password FROM applicants WHERE username = ?", (username,))

        user = cursor.fetchone()
        conn.close()

        if user:
            stored_hashed_password = user[0]

            # Verify the entered password against the stored hash
            if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
                st.session_state.auth_user = username
                st.session_state.is_logged_in = True
                st.session_state.user_type = user_type
                st.success("Login successful!")
                time.sleep(3)
                st.switch_page("pages/1_Home.py")
            else:
                st.error("Invalid username or password.")
        else:
            st.error("Invalid username or password.")

    # Sign Up button
    if st.button("Sign Up", key="signup_button"):
        st.switch_page("pages/3_Sign_Up.py")

def main():
    login_page()

if __name__ == "__main__":
    main()