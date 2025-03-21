import streamlit as st
import sqlite3
import time  # Import the time module for delay

DB_NAME = "job_portal.db"

def add_job_page():
    st.header("Add Job")

    with st.form("add_job_form"):
        role = st.text_input("Job Role", value="")
        openings = st.number_input("Number of Openings", min_value=1, step=1)
        location = st.text_input("Location", value="")
        salary = st.text_input("Salary", value="")
        description = st.text_area("Job Description", value="")

        submit = st.form_submit_button("Submit")
            
        if submit:
            if role and location and salary and description:
                try:
                    # Fetch the company name from session state
                    company_name = st.session_state.get("auth_user")

                    # Check if the job already exists
                    conn = sqlite3.connect(DB_NAME)
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT id FROM jobs
                        WHERE company_name = ? AND role = ? AND description = ?
                    """, (company_name, role, description))
                    existing_job = cursor.fetchone()

                    if existing_job:
                        st.error("Job description already exists.")
                    else:
                        # Insert into the main jobs table in job_portal.db
                        cursor.execute("""
                            INSERT INTO jobs (company_name, role, openings, location, salary, description)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (company_name, role, openings, location, salary, description))
                        conn.commit()
                        st.success("Job added successfully!")
                        time.sleep(3)
                        st.switch_page("pages/1_Home.py")
                    conn.close()
                except sqlite3.Error as e:
                    st.error(f"Database error: {e}")
                except Exception as e:
                    st.error(f"Unexpected error: {e}")
            else:
                st.error("Please fill in all fields.")

def main():
    if st.session_state.get("is_logged_in", False) and st.session_state.get("user_type") == "Company":
        add_job_page()
    else:
        st.error("Please login as a Company to add a job.")

if __name__ == "__main__":
    main()