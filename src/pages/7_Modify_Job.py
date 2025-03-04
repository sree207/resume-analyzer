import streamlit as st
import sqlite3
import time  # Import the time module for delay

DB_NAME = "job_portal.db"

def modify_job_page(job):
    st.header(f"Modify {job[2]} at {job[1]}")

    with st.form("modify_job_form"):
        role = st.text_input("Job Role", value=job[2])
        openings = st.number_input("Number of Openings", min_value=1, step=1, value=job[3])
        location = st.text_input("Location", value=job[4])
        salary = st.text_input("Salary", value=job[5])
        description = st.text_area("Job Description", value=job[6])

        submit = st.form_submit_button("Submit Changes")
            
        if submit:
            if role and location and salary and description:
                try:
                    conn = sqlite3.connect(DB_NAME)
                    cursor = conn.cursor()

                    # Update the job
                    cursor.execute("""
                        UPDATE jobs
                        SET role = ?, openings = ?, location = ?, salary = ?, description = ?
                        WHERE id = ?
                    """, (role, openings, location, salary, description, job[0]))
                    conn.commit()
                    conn.close()
                    st.success("Job updated successfully!")
                    time.sleep(3)
                    st.switch_page("pages/5_Your_Jobs.py")
                except sqlite3.Error as e:
                    st.error(f"Database error: {e}")
                except Exception as e:
                    st.error(f"Unexpected error: {e}")
            else:
                st.error("Please fill in all fields.")

def main():
    # Restrict access to Companies only
    if not st.session_state.get("is_logged_in", False) or st.session_state.get("user_type") != "Company":
        st.error("You do not have access to this page. Redirecting to the home page...")
        time.sleep(3)
        st.switch_page("pages/1_Home.py")

    if "selected_job" in st.session_state and st.session_state.selected_job is not None:
        modify_job_page(st.session_state.selected_job)
    else:
        st.error("No job selected. Redirecting to the home page...")
        time.sleep(3)
        st.switch_page("pages/1_Home.py")

if __name__ == "__main__":
    main()