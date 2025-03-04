import streamlit as st
import sqlite3

DB_NAME = "job_portal.db"

def list_jobs():
    st.header("Available Jobs")

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jobs")
        jobs = cursor.fetchall()
        conn.close()

        if not jobs:
            st.write("No jobs available at the moment.")
            return

        for job in jobs:
            col1, col2 = st.columns([4, 1])
            with col1:
                with st.expander(f"{job[1]} - {job[2]}"):
                    st.write(f"**Company Name:** {job[1]}")
                    st.write(f"**Role:** {job[2]}")
                    st.write(f"**Location:** {job[4]}")
                    st.write(f"**Salary:** {job[5]}")
                    st.write(f"**Description:** {job[6]}")
                    st.write(f"**Openings:** {job[3]}")
                    st.write(f"**Applicants:** {job[7]}")  # Display applicant count
            with col2:
                # Show Apply button only for Applicants
                if st.session_state.get("is_logged_in", False) and st.session_state.get("user_type") == "Applicant":
                    if st.button(f"Apply for {job[2]}", key=f"apply_{job[0]}"):
                        st.session_state.selected_job = job
                        st.switch_page("pages/6_Apply_Job.py")

    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")

def main():
    st.title("ResumeInsight - A Resume-Analyzer")

    # Login button at the top right
    if not st.session_state.get("is_logged_in", False):
        if st.button("Login", key="login_button"):
            st.switch_page("pages/2_Login.py")
    else:
        st.write(f"Logged in as: {st.session_state.auth_user} ({st.session_state.user_type})")
        if st.button("Logout", key="logout_button"):
            st.session_state.auth_user = None
            st.session_state.is_logged_in = False
            st.session_state.user_type = None
            st.rerun()

    # Display jobs
    list_jobs()

    # Add Job button for Companies
    if st.session_state.get("is_logged_in", False) and st.session_state.get("user_type") == "Company":
        if st.button("Add Job", key="add_job_button"):
            st.switch_page("pages/4_Add_Job.py")

    # Your Jobs button for Companies
    if st.session_state.get("is_logged_in", False) and st.session_state.get("user_type") == "Company":
        if st.button("Your Jobs", key="your_jobs_button"):
            st.switch_page("pages/5_Your_Jobs.py")

if __name__ == "__main__":
    main()