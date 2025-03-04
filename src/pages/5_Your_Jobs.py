import streamlit as st
import sqlite3
from utils.email_utils import send_emails
import pandas as pd
import time  # Import the time module for delay

DB_NAME = "job_portal.db"

def display_applications(job_id):
    st.subheader("Applications")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Fetch the number of openings for the job
    cursor.execute("SELECT openings FROM jobs WHERE id = ?", (job_id,))
    job_openings = cursor.fetchone()[0]

    # Fetch applications for the job, ordered by score in descending order
    cursor.execute("""
        SELECT id, applicant_name, applicant_email, score, status
        FROM applications
        WHERE job_id = ?
        ORDER BY score DESC
    """, (job_id,))
    applications = cursor.fetchall()

    if not applications:
        st.write("No applications yet.")
        return

    # Display applications in a table
    df = pd.DataFrame(applications, columns=["ID", "Applicant Name", "Email", "Score", "Status"])
    st.dataframe(df)

    # Button to send acceptance and rejection emails
    if st.button("Send Acceptance/Rejection Emails", key=f"send_emails_{job_id}"):
        # Get the top applicants based on the number of openings
        top_applicants = applications[:job_openings]
        other_applicants = applications[job_openings:]

        # Update status and send emails for top applicants (Accepted)
        for app in top_applicants:
            cursor.execute("""
                UPDATE applications
                SET status = 'Accepted'
                WHERE id = ?
            """, (app[0],))
            conn.commit()  # Commit the transaction

            # Send acceptance email
            job = cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
            send_emails(job, [(app[1], app[2], app[3])], "acceptance")

        # Update status and send emails for other applicants (Rejected)
        for app in other_applicants:
            cursor.execute("""
                UPDATE applications
                SET status = 'Rejected'
                WHERE id = ?
            """, (app[0],))
            conn.commit()  # Commit the transaction

            # Send rejection email
            job = cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
            send_emails(job, [(app[1], app[2], app[3])], "rejection")

        st.success("Emails sent successfully! Status updated.")

    conn.close()

def delete_job(job_id):
    """
    Delete a job from the database.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    conn.commit()
    conn.close()
    st.success("Job deleted successfully!")
    time.sleep(3)
    st.rerun()

def display_user_jobs():
    st.header("Your Posted Jobs")

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Fetch jobs posted by the logged-in company
        company_name = st.session_state.get("auth_user")
        cursor.execute("SELECT * FROM jobs WHERE company_name = ?", (company_name,))
        jobs = cursor.fetchall()

        if not jobs:
            st.write("You have not posted any jobs yet.")
            return

        for job in jobs:
            with st.expander(f"{job[1]} - {job[2]}"):
                st.write(f"**Company Name:** {job[1]}")
                st.write(f"**Role:** {job[2]}")
                st.write(f"**Openings:** {job[3]}")
                st.write(f"**Location:** {job[4]}")
                st.write(f"**Salary:** {job[5]}")
                st.write(f"**Description:** {job[6]}")
                st.write(f"**Applicants:** {job[7]}")  # Display applicant count

                # Buttons to modify or delete the job
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Modify {job[2]}", key=f"modify_{job[0]}"):
                        st.session_state.selected_job = job
                        st.switch_page("pages/7_Modify_Job.py")
                with col2:
                    if st.button(f"Delete {job[2]}", key=f"delete_{job[0]}"):
                        delete_job(job[0])

                # Show applications for this job
                display_applications(job[0])

        conn.close()
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")

def main():
    if st.session_state.get("is_logged_in", False) and st.session_state.get("user_type") == "Company":
        display_user_jobs()
    else:
        st.error("Please login as a Company to view your posted jobs.")

if __name__ == "__main__":
    main()