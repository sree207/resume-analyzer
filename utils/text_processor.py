"""Text processing utilities."""
from typing import List, Set
import re

def extract_skills(text: str, skills_db: Set[str]) -> List[str]:
    """Extract skills from text using a predefined skills database."""
    text_lower = text.lower()
    skills_found = []

    for skill in skills_db:
        if skill.lower() in text_lower:
            skills_found.append(skill)
    
    return skills_found

def get_common_skills_db() -> List[str]:
    """Return a set of common technical skills."""
    return {
        "Python", "JavaScript", "Java", "C++", "SQL",
        "Machine Learning", "Data Analysis", "AWS",
        "Docker", "Kubernetes", "React", "Node.js",
        "Git", "REST API", "MongoDB", "PostgreSQL","Excel","R","Tableau","PowerBi",
    }
    
    
