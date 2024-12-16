"""Field recommendation analysis utilities."""
from typing import Dict, List, Tuple
import plotly.graph_objects as go

class FieldAnalyzer:
    def __init__(self):
        """Initialize field categories and their associated skills."""
        self.field_skills = {
            "Web Development": [
                "html", "css", "javascript", "react", "angular", "vue", "node.js",
                "express", "django", "flask", "php", "laravel"
            ],
            "Data Science": [
                "python", "r", "machine learning", "deep learning", "nlp",
                "data analysis", "statistics", "pandas", "numpy", "scikit-learn"
            ],
            "DevOps": [
                "aws", "azure", "gcp", "docker", "kubernetes", "jenkins",
                "ci/cd", "terraform", "ansible", "linux"
            ],
            "Database": [
                "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
                "oracle", "database design", "nosql"
            ],
            "Mobile Development": [
                "android", "ios", "swift", "kotlin", "react native", "flutter",
                "mobile app development"
            ],
            "Software Engineering": [
                "java", "c++", "python", "golang", "rust", "software architecture",
                "design patterns", "algorithms"
            ]
        }

    def analyze_fields(self, skills: List[str]) -> List[Tuple[str, float]]:
        """Analyze skills and return field recommendations with scores."""
        field_scores = {}
        skills_lower = [skill.lower() for skill in skills]

        for field, field_skills in self.field_skills.items():
            matching_skills = sum(1 for skill in field_skills if any(s in skill for s in skills_lower))
            if matching_skills > 0:
                score = matching_skills / len(field_skills)
                field_scores[field] = score

        # Sort by score and normalize to percentages
        total_score = sum(field_scores.values())
        if total_score > 0:
            normalized_scores = [(field, (score / total_score) * 100) 
                               for field, score in field_scores.items()]
        else:
            normalized_scores = []

        return sorted(normalized_scores, key=lambda x: x[1], reverse=True)

    def create_pie_chart(self, field_scores: List[Tuple[str, float]]) -> go.Figure:
        """Create a pie chart visualization of field recommendations."""
        if not field_scores:
            return None

        fields, scores = zip(*field_scores)
        
        fig = go.Figure(data=[go.Pie(
            labels=fields,
            values=scores,
            hole=.3,
            textinfo='label+percent',
            textposition='inside',
            marker=dict(
                colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD', '#D4A5A5']
            )
        )])
        
        fig.update_layout(
            title={
                'text': 'Field Recommendations Based on Skills',
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            showlegend=False,
            height=500
        )
        
        return fig