import streamlit as st
import sqlite3

# Database name
DB_NAME = "job_portal.db"

def initialize_database():
    """
    Initialize the database and create tables if they don't exist.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create companies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Create applicants table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applicants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Create jobs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            role TEXT NOT NULL,
            openings INTEGER NOT NULL,
            location TEXT NOT NULL,
            salary TEXT NOT NULL,
            description TEXT NOT NULL,
            applicants_count INTEGER DEFAULT 0
        )
    """)

    # Create applications table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            applicant_name TEXT NOT NULL,
            applicant_email TEXT NOT NULL,
            score REAL NOT NULL,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (job_id) REFERENCES jobs(id)
        )
    """)

    conn.commit()
    conn.close()

def main():
    """
    Main function to initialize the app and manage session state.
    """
    # Initialize session state for authentication
    if "auth_user" not in st.session_state:
        st.session_state["auth_user"] = None
    if "is_logged_in" not in st.session_state:
        st.session_state["is_logged_in"] = False
    if "user_type" not in st.session_state:
        st.session_state["user_type"] = None
    if "selected_job" not in st.session_state:
        st.session_state["selected_job"] = None

    # Initialize the database
    initialize_database()

    # Redirect to the Home page
    st.switch_page("pages/1_Home.py")

if __name__ == "__main__":
    main()