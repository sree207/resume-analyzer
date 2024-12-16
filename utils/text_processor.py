"""Text processing utilities."""
from typing import List, Set
import re

def extract_skills(text: str, skills_db: Set[str]) -> List[str]:
    """Extract skills from text using a predefined skills database."""
    found_skills = []
    text_lower = text.lower()
    
    for skill in skills_db:
        if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text_lower):
            found_skills.append(skill)
    
    return found_skills

def get_common_skills_db() -> Set[str]:
    """Return a set of common technical skills."""
    return {
        "Python", "JavaScript", "Java", "C++", "SQL",
        "Machine Learning", "Data Analysis", "AWS",
        "Docker", "Kubernetes", "React", "Node.js",
        "Git", "REST API", "MongoDB", "PostgreSQL"
    }