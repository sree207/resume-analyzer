"""Main Streamlit application."""
import streamlit as st
import os
import sys
import google.generativeai as genai
genai.configure(api_key="GEMINI API")

project_root = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(project_root)  # Move up one level to include project root
if project_root not in sys.path:
    sys.path.append(project_root)


from utils.pdf_parser import extract_text_from_pdf
from utils.resume_analyzer import ResumeAnalyzer
from utils.text_processor import extract_skills, get_common_skills_db
from utils.field_analyzer import FieldAnalyzer

def display_contact_info(contact_info):
    """Display contact information in a formatted way."""
    st.subheader("📞 Contact Information")
    if contact_info.get("email"):
        st.write(f"📧 Email: {contact_info['email']}")
    if contact_info.get("phone"):
        st.write(f"📱 Phone: {contact_info['phone']}")
    if contact_info.get("linkedin"):
        st.write(f"💼 LinkedIn: {contact_info['linkedin']}")

def display_education(education):
    """Display education information in a formatted way."""
    st.subheader("🎓 Education")
    for edu in education:
        with st.expander(f"{edu['degree']} ({edu['year']})"):
            st.write(f"Degree: {edu['degree']}")
            st.write(f"Year: {edu['year']}")





def display_work_experience(experience):
    """Display work experience in a formatted way."""
    st.subheader("💼 Work Experience")
    for exp in experience:
        with st.expander(f"{exp['company']} ({' - '.join(exp['dates'])})"):
            st.write(f"Company: {exp['company']}")
            st.write(f"Dates: {' - '.join(exp['dates'])}")

            
            
            




def display_skills_comparison(resume_skills, job_skills):
    """Display skills comparison in a formatted way."""
    st.subheader("🔍 Skills Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("📋 Skills Found in Resume:")
        for skill in resume_skills:
            st.write(f"✓ {skill}")
            
    with col2:
        st.write("🎯 Required Skills in Job Description:")
        for skill in job_skills:
            if skill.lower() in [s.lower() for s in resume_skills]:
                st.write(f"✓ {skill}")
            else:
                st.write(f"❌ {skill}")

def display_field_recommendations(skills):
    """Display field recommendations pie chart."""
    st.subheader("🎯 Field Recommendations")
    
    field_analyzer = FieldAnalyzer()
    field_scores = field_analyzer.analyze_fields(skills)
    
    if field_scores:
        fig = field_analyzer.create_pie_chart(field_scores)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            
            # Display detailed breakdown
            st.write("Detailed Field Analysis:")
            for field, score in field_scores:
                st.write(f"- {field}: {score:.1f}%")
    else:
        st.write("Not enough skills detected to make field recommendations.")

def display_course_recommendation():
    
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 300,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
    system_instruction=(
        "Recommend courses and resources based on the job role. "
        "Please format the output as follows: "
        "- Make course names **bold**. "
        "- Use proper Markdown for links. "
        "Do not include greetings, symbols, or unnecessary text."
        "Make sure that course links and videos are valid and available."
    ),
    )

            # Streamlit Interface
    st.subheader("📒Course Recommendation")
    job_role = st.text_input("Enter the job role (e.g., Web Developer, Data Scientist, etc.):")

    if st.button("Get Recommendations"):
        if job_role.strip():
            # Start a chat session and fetch recommendations
            chat_session = model.start_chat(
                history=[
                    {
                        "role": "user",
                        "parts": [job_role],
                     },
                ]
            )
            response = chat_session.send_message(job_role)

            # Display the response as Markdown
            st.markdown("### Recommendations:")
            st.markdown(response.text, unsafe_allow_html=True)
        else:
            st.error("Please enter a valid job role.")

def main():
    st.title("ResumeInsight - A Resume-Analyzer")
    
    # Initialize ResumeAnalyzer
    analyzer = ResumeAnalyzer()
    
    # File upload section
    st.header("📄 Upload Resume")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    # Job description input
    st.header("📝 Job Description")
    job_description = st.text_area(
        "Enter the job description",
        height=200,
        max_chars=5000,
        placeholder="Paste the job description here..."
    )
    
    if uploaded_file and job_description:
        try:
            # Extract text from PDF
            resume_text = extract_text_from_pdf(uploaded_file)
            
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

            #Course recommendation
            display_course_recommendation()
            
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()