import streamlit as st
import sqlite3
import pandas as pd
import time  # Import the time module for delay

DB_NAME = "job_portal.db"

def display_application_status():
    st.header("Your Application Status")

    # Restrict access to Applicants only
    if not st.session_state.get("is_logged_in", False) or st.session_state.get("user_type") != "Applicant":
        st.error("You do not have access to this page. Redirecting to the home page...")
        time.sleep(3)
        st.switch_page("pages/1_Home.py")

    # Get the logged-in applicant's username
    username = st.session_state.get("auth_user")

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Fetch applications for the logged-in applicant using their username
        cursor.execute("""
            SELECT j.company_name, j.role, a.score, a.status
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            WHERE a.applicant_name = ?
        """, (username,))
        applications = cursor.fetchall()

        if not applications:
            st.write("You have not applied to any jobs yet.")
            return

        # Display applications in a table
        df = pd.DataFrame(applications, columns=["Company", "Role", "Score", "Status"])
        st.dataframe(df)

        conn.close()
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")

def main():
    display_application_status()

if __name__ == "__main__":
    main()