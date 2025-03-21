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

def reset_password_page():
    st.header("Reset Password")

    # Choose user type
    user_type = st.radio("Reset Password for:", ("Company", "Applicant"))

    # Reset Password form
    username = st.text_input("Enter your username")
    new_password = st.text_input("Enter new password", type="password")
    confirm_new_password = st.text_input("Re-enter new password", type="password")

    # Display password creation criteria
    st.info("""
        **Password must meet the following criteria:**
        - Minimum length of 8 characters.
        - At least one alphabet (uppercase or lowercase).
        - At least one number.
        - At least one special symbol (e.g., !@#$%^&*(),.?":{}|<>).
    """)

    if st.button("Reset Password", key="reset_password_button"):
        # Check if passwords match
        if new_password != confirm_new_password:
            st.error("Passwords do not match.")
            return

        # Validate password
        is_valid, message = is_password_valid(new_password)
        if not is_valid:
            st.error(f"Password does not meet the requirements: {message}")
            return

        # Hash the new password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(new_password.encode(), salt).decode()

        # Update the password in the database
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            if user_type == "Company":
                cursor.execute("UPDATE companies SET password = ? WHERE company_name = ?", (hashed_password, username))
            else:
                cursor.execute("UPDATE applicants SET password = ? WHERE username = ?", (hashed_password, username))
            conn.commit()
            if cursor.rowcount > 0:
                st.success("Password reset successfully!")
                time.sleep(3)
                st.switch_page("pages/2_Login.py")
            else:
                st.error("Username not found.")
        except sqlite3.Error as e:
            st.error(f"Database error: {e}")
        conn.close()

def main():
    reset_password_page()

if __name__ == "__main__":
    main()