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
        
        # Common education keywords
        edu_keywords = r'(bachelor|master|phd|b\.?s\.?|m\.?s\.?|b\.?a\.?|m\.?a\.?|btech|mtech|doctorate|degree)'
        edu_sections = re.split(r'\n{2,}', text)
        print(edu_sections)
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
    
    def extract_sections(self, text: str) -> Dict[str, str]:
        """Split text into sections based on common resume headings."""
        sections = {
            "contact_info": "",
            "education": "",
            "work_experience": "",
            "skills": "",
            "other": ""
        }
        
        # Use a list of common resume section headers to split the resume
        section_keywords = {
            "education": r'(education|degree|university|school|qualification)',
            "work_experience": r'(work experience|experience|professional experience|employment)',
        }
        
        # Split the resume into sections based on keywords
        for section, keyword in section_keywords.items():
            match = re.search(keyword, text, re.IGNORECASE)
            if match:
                start = match.start()
                end = match.end()
                # Extract section text from the match to the next section or end of text
                next_section_start = len(text)
                for next_section, next_keyword in section_keywords.items():
                    if next_section != section:
                        next_match = re.search(next_keyword, text[end:], re.IGNORECASE)
                        if next_match:
                            next_section_start = min(next_section_start, next_match.start())
                section_text = text[end:end + next_section_start].strip()
                sections[section] = section_text
        
        # Capture the remaining text as 'other' (e.g., summary, references)
        remaining_text = text.strip()
        for section in sections:
            remaining_text = remaining_text.replace(sections[section], "")
        sections["other"] = remaining_text.strip()

        return sections

    def extract_information(self, text: str) -> Dict[str, Any]:
        """Extract key information from resume text."""
        sections = self.extract_sections(text)
        
        # Extract contact information
        contact_info = self.extract_contact_info(text)
        
        # Extract education
        education = self.extract_education(sections.get("education", ""))
        
        # Extract work experience
        work_experience = self.extract_work_experience(sections.get("work_experience", ""))
        
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
            r'python|java|javascript|c|c\+\+|ruby|php|swift|kotlin|rust|golang|sdlc|oop|dynamic programming|dp|matlab',
            r'react|frontend|backend|angular|vue|node\.js|express|django|flask|spring|laravel|asp.net|graphql',
            r'aws|azure|gcp|docker|kubernetes|jenkins|git|ci/cd',
            r'sql|mysql|postgresql|mongodb|cassandra|firebase|dynamodb|redis|elasticsearch|dsa',
            r'machine learning|deep learning|nlp|computer vision|excel|hadoop|spark|data science|data mining',
            r'html|css|sass|bootstrap|tailwind|tableau|powerbi',
            r'agile|scrum|kanban|jira|confluence|cloud|azure|google cloud|aws|cyber security|ethical hacking',
            r'Android Development|iOS Development|flutter|dart'
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
