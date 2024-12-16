"""Resume analysis utilities using spaCy."""
import spacy
from typing import Dict, List, Any
import re

class ResumeAnalyzer:
    def __init__(self):
        """Initialize spaCy model."""
        self.nlp = spacy.load("en_core_web_lg")
        
    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information using regex patterns."""
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email = re.findall(email_pattern, text)
        
        # Phone pattern (handles multiple formats)
        phone_pattern = r'(\+\d{1,3}[-.]?)?\s*\(?([0-9]{3})\)?[-.]?\s*([0-9]{3})[-.]?\s*([0-9]{4})'
        phone = re.findall(phone_pattern, text)
        
        # LinkedIn pattern
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin = re.findall(linkedin_pattern, text)
        
        return {
            "email": email[0] if email else "",
            "phone": ''.join(phone[0]) if phone else "",
            "linkedin": linkedin[0] if linkedin else ""
        }

    def extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extract education information."""
        education = []
        doc = self.nlp(text)
        
        # Common education keywords
        edu_keywords = r'(bachelor|master|phd|b\.?s\.?|m\.?s\.?|b\.?a\.?|m\.?a\.?|doctorate|degree)'
        edu_sections = re.split(r'\n{2,}', text)
        
        for section in edu_sections:
            if re.search(edu_keywords, section.lower()):
                # Extract degree
                degree_match = re.search(edu_keywords, section.lower())
                degree = degree_match.group(0) if degree_match else ""
                
                # Extract year
                year_pattern = r'20\d{2}|19\d{2}'
                year = re.search(year_pattern, section)
                
                if degree:
                    education.append({
                        "degree": degree.upper(),
                        "year": year.group(0) if year else "",
                        "details": section.strip()
                    })
        
        return education

    def extract_work_experience(self, text: str) -> List[Dict[str, str]]:
        """Extract work experience information."""
        experience = []
        doc = self.nlp(text)
        
        # Look for company names and positions
        for ent in doc.ents:
            if ent.label_ == "ORG":
                # Look for date patterns near the organization
                context = text[max(0, ent.start_char-50):min(len(text), ent.end_char+50)]
                dates = re.findall(r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4})', context)
                
                if dates:
                    experience.append({
                        "company": ent.text,
                        "dates": dates,
                        "context": context.strip()
                    })
        
        return experience

    def extract_information(self, text: str) -> Dict[str, Any]:
        """Extract key information from resume text."""
        doc = self.nlp(text)
        
        # Extract contact information
        contact_info = self.extract_contact_info(text)
        
        # Extract education
        education = self.extract_education(text)
        
        # Extract work experience
        work_experience = self.extract_work_experience(text)
        
        # Extract skills (using custom patterns)
        skills = self.extract_skills(text)
        
        return {
            "contact_info": contact_info,
            "education": education,
            "work_experience": work_experience,
            "skills": skills,
            "text": text
        }

    def extract_skills(self, text: str) -> List[str]:
        """Extract technical skills from text."""
        # Common technical skills patterns
        skill_patterns = [
            r'python|java|javascript|c\+\+|ruby|php|swift|kotlin|rust|golang',
            r'react|angular|vue|node\.js|express|django|flask|spring|laravel',
            r'aws|azure|gcp|docker|kubernetes|jenkins|git|ci/cd',
            r'sql|mysql|postgresql|mongodb|redis|elasticsearch',
            r'machine learning|deep learning|nlp|computer vision|data science',
            r'html|css|sass|less|bootstrap|tailwind',
            r'agile|scrum|kanban|jira|confluence'
        ]
        
        skills = set()
        text_lower = text.lower()
        
        for pattern in skill_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                skills.add(match.group(0))
        
        return list(skills)

    def calculate_similarity(self, resume_text: str, job_description: str) -> float:
        """Calculate similarity between resume and job description."""
        resume_doc = self.nlp(resume_text)
        job_doc = self.nlp(job_description)
        
        return resume_doc.similarity(job_doc)