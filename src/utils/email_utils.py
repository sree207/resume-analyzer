# utils/email_utils.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st

def send_emails(job, applicants, email_type):
    """
    Send acceptance or rejection emails to applicants.
    
    Args:
        job (tuple): Job details from the database.
        applicants (list): List of applicants (name, email, score).
        email_type (str): "acceptance" or "rejection".
    """
    # Email credentials 
    sender_email = "Your_Email"  
    sender_password = "Your_App_Password"  
    smtp_server = "smtp.gmail.com"
    smtp_port = 587  

    # Job details
    company_name = job[1]
    role = job[2]

    # Determine recipients and email content based on email type
    if email_type == "acceptance":
        recipients = [(name, email) for name, email, _ in applicants]
        subject = f"Congratulations! You've been selected for next round for the {role} role at {company_name}"
        body_template = """
        Dear {name},

        We are pleased to inform you that you have been selected for  next round for the {role} position at {company_name}.
        Your application stood out among many, and we are excited to move forward with your application.

        

        Best regards,
        {company_name}
        """
    else:
        recipients = [(name, email) for name, email, _ in applicants]
        subject = f"Application Update for the {role} role at {company_name}"
        body_template = """
        Dear {name},

        Thank you for applying for the {role} position at {company_name}.
        After careful consideration, we regret to inform you that we have decided to move forward with other candidates.

        We appreciate your interest in joining our team and encourage you to apply for future openings.

        Best regards,
        {company_name}
        """

    # Send emails
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)

            for name, email in recipients:
                # Create the email
                msg = MIMEMultipart()
                msg["From"] = sender_email
                msg["To"] = email
                msg["Subject"] = subject

                # Add the body
                body = body_template.format(name=name, role=role, company_name=company_name)
                msg.attach(MIMEText(body, "plain"))

                # Send the email
                server.sendmail(sender_email, email, msg.as_string())

        st.success(f"{email_type.capitalize()} emails sent successfully!")
    except Exception as e:
        st.error(f"Failed to send {email_type} emails: {str(e)}")
