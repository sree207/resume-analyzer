import streamlit as st
import sqlite3

DB_NAME = "job_portal.db"

def list_jobs():
    st.header("Available Jobs")

    # Add search bar for job role
    role_query = st.text_input("Search by job role", placeholder="Enter job role...")

    # Initialize company_query as None
    company_query = None

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Fetch jobs based on user type and search queries
        if st.session_state.get("is_logged_in", False):
            if st.session_state.get("user_type") == "Company":
                # Fetch jobs posted by the logged-in company
                company_name = st.session_state.get("auth_user")
                if role_query:
                    cursor.execute("""
                        SELECT * FROM jobs
                        WHERE company_name = ? AND role LIKE ?
                    """, (company_name, f"%{role_query}%"))
                else:
                    cursor.execute("SELECT * FROM jobs WHERE company_name = ?", (company_name,))
            elif st.session_state.get("user_type") == "Applicant":
                # Fetch unique company names for the searched role
                if role_query:
                    cursor.execute("""
                        SELECT DISTINCT company_name FROM jobs
                        WHERE role LIKE ?
                    """, (f"%{role_query}%",))
                    company_names = [row[0] for row in cursor.fetchall()]

                    # Add a dropdown for company names
                    if company_names:
                        company_query = st.selectbox("Filter by company name", options=["All"] + company_names)
                    else:
                        st.write("No companies found for this role.")
                        company_query = "All"

                # Fetch jobs based on role and company name
                if role_query and company_query and company_query != "All":
                    cursor.execute("""
                        SELECT * FROM jobs
                        WHERE role LIKE ? AND company_name = ?
                    """, (f"%{role_query}%", company_query))
                elif role_query:
                    cursor.execute("""
                        SELECT * FROM jobs
                        WHERE role LIKE ?
                    """, (f"%{role_query}%",))
                else:
                    cursor.execute("SELECT * FROM jobs")
        else:
            # Fetch unique company names for non-logged-in users
            if role_query:
                cursor.execute("""
                    SELECT DISTINCT company_name FROM jobs
                    WHERE role LIKE ?
                """, (f"%{role_query}%",))
                company_names = [row[0] for row in cursor.fetchall()]

                # Add a dropdown for company names
                if company_names:
                    company_query = st.selectbox("Filter by company name", options=["All"] + company_names)
                else:
                    st.write("No companies found for this role.")
                    company_query = "All"

            # Fetch jobs based on role and company name for non-logged-in users
            if role_query and company_query and company_query != "All":
                cursor.execute("""
                    SELECT * FROM jobs
                    WHERE role LIKE ? AND company_name = ?
                """, (f"%{role_query}%", company_query))
            elif role_query:
                cursor.execute("""
                    SELECT * FROM jobs
                    WHERE role LIKE ?
                """, (f"%{role_query}%",))
            else:
                cursor.execute("SELECT * FROM jobs")

        jobs = cursor.fetchall()
        conn.close()

        if not jobs:
            st.write("No jobs found matching your search criteria." if (role_query or company_query) else "No jobs available at the moment.")
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
    st.title("Welcome to ResumeInsight!")

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