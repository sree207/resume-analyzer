import streamlit as st
import joblib
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from utils.field_analyzer import FieldAnalyzer

# Load trained model and encoders
model = load_model(r'E:\resume-analyzer\models\course_recommendation_model.keras')
job_role_encoder = joblib.load(r'E:\resume-analyzer\models\job_role_encoder.pkl')  # Load encoders
course_name_encoder = joblib.load(r'E:\resume-analyzer\models\course_name_encoder.pkl')
category_encoder = joblib.load(r'E:\resume-analyzer\models\category_encoder.pkl')

# Load processed dataset
df_final = pd.read_csv(r'E:\resume-analyzer\models\df_final.csv')

# 📞 Display Contact Information
def display_contact_info(contact_info):
    """Display contact information in a formatted way."""
    st.subheader("📞 Contact Information")
    if contact_info.get("email"):
        st.write(f"📧 Email: {contact_info['email']}")
    if contact_info.get("phone"):
        st.write(f"📱 Phone: {contact_info['phone']}")
    if contact_info.get("linkedin"):
        st.write(f"💼 LinkedIn: {contact_info['linkedin']}")

# 🎓 Display Education
def display_education(education):
    """Display education information in a formatted way."""
    st.subheader("🎓 Education")
    for edu in education:
        with st.expander(f"{edu['degree']} ({edu['year']})"):
            st.write(f"Degree: {edu['degree']}")
            st.write(f"Year: {edu['year']}")

# 💼 Display Work Experience
def display_work_experience(experience):
    """Display work experience in a formatted way."""
    st.subheader("💼 Work Experience")
    for exp in experience:
        with st.expander(f"{exp['company']} ({' - '.join(exp['dates'])})"):
            st.write(f"Company: {exp['company']}")
            st.write(f"Dates: {' - '.join(exp['dates'])}")

# 🔍 Display Skills Comparison
def display_skills_comparison(resume_skills, job_skills):
    """Compare resume skills with job requirements."""
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

# 🎯 Display Field Recommendations
def display_field_recommendations(skills):
    """Analyze skills and recommend potential fields."""
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

"""
# 📒 Course Recommendation System
def recommend_courses_with_details(job_role):
    
    if job_role not in job_role_encoder.classes_.tolist():
        return []

    job_role_encoded = job_role_encoder.transform([job_role])
    categories_for_job = df_final[df_final['job_role'] == job_role]['category'].unique()
    recommended_courses = []

    for category in categories_for_job:
        category_encoded = category_encoder.transform([category])
        input_vector = np.array([[job_role_encoded[0], category_encoded[0]]])

        print("Input Vector:", input_vector)  # ✅ Debugging Input
        predictions = model.predict(input_vector)
        print("Predictions Shape:", predictions.shape)  # ✅ Debugging Output
        print(predictions)  # ✅ Check the actual predictions

        # Fix the sorting to extract correct courses
        #predicted_course_indices = np.argsort(predictions[0])[-3:][::-1]  # ✅ Corrected
        # Extract top 3 predicted course indices
        predicted_course_indices = np.argsort(predictions[0])[-3:][::-1]  # Get highest probabilities first
        predicted_course_names = course_name_encoder.inverse_transform(predicted_course_indices)  # Convert indices to names

        # Debugging output
        print("\nTop 3 Course Indices:", predicted_course_indices)
        print("Top 3 Course Names:", predicted_course_names)
        print("Top 3 Probabilities:", predictions[0][predicted_course_indices])


        #recommended_courses.extend(course_name_encoder.inverse_transform(predicted_course_indices))

    #return df_final[df_final['course_name'].isin(recommended_courses)][['course_name', 'course_link', 'difficulty_level']].drop_duplicates().values[:3]
"""


def recommend_courses_with_details(job_role, confidence_threshold=0.5):
    """Recommend top 3 highly specific courses based on job role using the trained model."""
    
    if job_role not in job_role_encoder.classes_.tolist():
        print(f"❌ Job role '{job_role}' not found in encoder classes.")
        return []

    job_role_encoded = job_role_encoder.transform([job_role])
    categories_for_job = df_final[df_final['job_role'] == job_role]['category'].unique()
    
    all_predictions = []

    for category in categories_for_job:
        try:
            category_encoded = category_encoder.transform([category])
            input_vector = np.array([[job_role_encoded[0], category_encoded[0]]])

            predictions = model.predict(input_vector)[0]

            # Get top course indices
            top_indices = np.argsort(predictions)[-5:][::-1]  # Top 5 (to allow filtering)
            top_courses = course_name_encoder.inverse_transform(top_indices)
            top_probs = predictions[top_indices]

            # Collect courses with sufficient confidence
            for course, prob in zip(top_courses, top_probs):
                if prob >= confidence_threshold:
                    all_predictions.append((course, prob))

        except Exception as e:
            print(f"⚠️ Error processing category '{category}': {e}")

    # Sort by confidence and take the top 3 unique courses
    all_predictions = sorted(set(all_predictions), key=lambda x: x[1], reverse=True)[:3]

    return all_predictions




# 🎒 Streamlit UI
def display_course_recommendation():
    """Display course recommendations based on the job role."""
    st.subheader("📒 Course Recommendation")
    job_role = st.text_input("Enter the job role (e.g., Web Developer, Data Scientist, etc.):")

    if st.button("Get Recommendations"):
        if job_role.strip():
            try:
                recommended_courses = recommend_courses_with_details(job_role)

                if recommended_courses:
                    st.markdown("### Recommendations:")
                    for course, confidence in recommended_courses:
                        course_row = df_final[df_final["course_name"] == course]
                        if not course_row.empty:
                            course_link = course_row["course_link"].values[0]
                            difficulty = course_row["difficulty_level"].values[0]

                            st.markdown(f"**Course Name:** {course}")
                            st.markdown(f"🔗 [Course Link]({course_link})")
                            st.markdown(f"📊 Difficulty: {difficulty}")
                            st.write("---")

                else:
                    st.error("No highly relevant courses found for the given job role. Try another role.")

            except Exception as e:
                st.error(f"An error occurred: {e}")

        else:
            st.error("Please enter a valid job role.")

