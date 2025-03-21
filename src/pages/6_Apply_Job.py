import streamlit as st
import sqlite3
import time  # Import the time module for delay
from utils.pdf_parser import extract_text_from_pdf
from utils.resume_analyzer import ResumeAnalyzer
from utils.text_processor import extract_skills, get_common_skills_db
from utils.field_analyzer import FieldAnalyzer
from utils.display_utils import (
    display_contact_info,
    display_education,
    display_work_experience,
    display_skills_comparison,
    display_field_recommendations,
    display_course_recommendation,
)

DB_NAME = "job_portal.db"

def apply_job_page(job):
    st.header(f"Apply for {job[2]} at {job[1]}")
    
    # Name input (pre-filled with the logged-in applicant's username)
    name = st.session_state.get("auth_user")
    st.write(f"**Applicant Name:** {name}")
    
    # Email input
    email = st.text_input("Your Email")
    
    # Resume upload section
    st.header("📄 Upload Resume")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    
    # Job description (pre-filled from the selected job)
    job_description = job[6]  # Job description is stored in the 7th column of the jobs table
    
    if uploaded_file and email:  # Ensure email is provided
        try:
            # Check if the applicant has already applied for this job
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id FROM applications
                WHERE job_id = ? AND applicant_name = ?
            """, (job[0], name))
            existing_application = cursor.fetchone()

            if existing_application:
                st.error("You have already applied for this job.")
                conn.close()
                return

            # Extract text from PDF
            resume_text = extract_text_from_pdf(uploaded_file)
            
            # Initialize ResumeAnalyzer
            analyzer = ResumeAnalyzer()
            
            # Analyze resume
            resume_info = analyzer.extract_information(resume_text)
            
            # Calculate similarity score
            similarity_score = analyzer.calculate_similarity(resume_text, job_description)
            
            # Extract skills
            skills_db = get_common_skills_db()
            resume_skills = resume_info['skills']
            job_skills = extract_skills(job_description, skills_db)
            
            # Display results
            st.header("📊 Analysis Results")
            
            # Display similarity score
            st.subheader("🎯 Match Score")
            st.progress(similarity_score)
            st.write(f"Similarity Score: {similarity_score:.2%}")
            
            # Display contact information
            display_contact_info(resume_info['contact_info'])
            
            # Display education
            display_education(resume_info['education'])
            
            # Display work experience
            display_work_experience(resume_info['work_experience'])
            
            # Display skills comparison
            display_skills_comparison(resume_skills, job_skills)
            
            # Display field recommendations
            display_field_recommendations(resume_skills)
            
            # Improvement suggestions
            st.subheader("💡 Suggestions for Improvement")
            missing_skills = [skill for skill in job_skills if skill.lower() not in [s.lower() for s in resume_skills]]
            if missing_skills:
                st.write("Consider adding these skills to your resume:")
                for skill in missing_skills:
                    st.write(f"- {skill}")
            else:
                st.write("Great job! Your resume contains all the required skills.")
            
            # Course recommendation
            display_course_recommendation()  # Pass the job role for course recommendations

            # Submit application button
            if st.button("Submit Application"):
                # Insert the application
                cursor.execute("""
                    INSERT INTO applications (job_id, applicant_name, applicant_email, score, status)
                    VALUES (?, ?, ?, ?, ?)
                """, (job[0], name, email, similarity_score, "Pending"))  # Default status is "Pending"
                
                # Increment the applicant count for the job
                cursor.execute("""
                    UPDATE jobs
                    SET applicants_count = applicants_count + 1
                    WHERE id = ?
                """, (job[0],))
                
                conn.commit()
                conn.close()
                
                st.success(f"Application submitted with a score of {similarity_score:.2f}!")
                time.sleep(3)
                st.switch_page("pages/1_Home.py")
        
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please upload your resume and provide your email to proceed.")

def main():
    # Restrict access to Applicants only
    if not st.session_state.get("is_logged_in", False) or st.session_state.get("user_type") != "Applicant":
        st.error("You do not have access to this page. Redirecting to the home page...")
        time.sleep(3)
        st.switch_page("pages/1_Home.py")

    if "selected_job" in st.session_state and st.session_state.selected_job is not None:
        apply_job_page(st.session_state.selected_job)
    else:
        st.error("No job selected. Redirecting to the home page...")
        st.switch_page("pages/1_Home.py")

if __name__ == "__main__":
    main()