"""
Utility functions for JobBider
"""

import os
import yaml
import time
import random
from dotenv import load_dotenv


def load_config():
    """Load configuration from config.yaml"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.yaml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def load_env():
    """Load environment variables"""
    load_dotenv()


def sanitize_filename(filename):
    """Sanitize filename for safe file operations"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def extract_salary(salary_text):
    """Extract salary range from text"""
    import re
    
    if not salary_text:
        return None, None
    
    # Remove commas and dollar signs
    salary_text = salary_text.replace(',', '').replace('$', '')
    
    # Try to find salary range (e.g., "100000 - 150000" or "100K - 150K")
    range_pattern = r'(\d+)(?:K|k)?\s*[-to]+\s*(\d+)(?:K|k)?'
    match = re.search(range_pattern, salary_text)
    
    if match:
        min_sal = float(match.group(1))
        max_sal = float(match.group(2))
        
        # Convert K to thousands
        if 'k' in salary_text.lower():
            min_sal *= 1000
            max_sal *= 1000
        
        return min_sal, max_sal
    
    # Try to find single salary value
    single_pattern = r'(\d+)(?:K|k)?'
    match = re.search(single_pattern, salary_text)
    
    if match:
        salary = float(match.group(1))
        if 'k' in salary_text.lower():
            salary *= 1000
        return salary, salary
    
    return None, None


def match_keywords(text, keywords):
    """Check if any keywords are present in text (case-insensitive)"""
    if not text or not keywords:
        return False
    
    text = text.lower()
    for keyword in keywords:
        if keyword.lower() in text:
            return True
    return False


def calculate_match_score(job_data, criteria):
    """Calculate how well a job matches the search criteria (0-100)"""
    score = 0
    max_score = 0
    
    # Check required skills (40 points)
    max_score += 40
    required_skills = criteria.get('required_skills', [])
    if required_skills:
        job_text = f"{job_data.get('title', '')} {job_data.get('description', '')} {job_data.get('requirements', '')}".lower()
        matched_required = sum(1 for skill in required_skills if skill.lower() in job_text)
        score += (matched_required / len(required_skills)) * 40
    
    # Check optional skills (20 points)
    max_score += 20
    optional_skills = criteria.get('optional_skills', [])
    if optional_skills:
        job_text = f"{job_data.get('title', '')} {job_data.get('description', '')} {job_data.get('requirements', '')}".lower()
        matched_optional = sum(1 for skill in optional_skills if skill.lower() in job_text)
        score += (matched_optional / len(optional_skills)) * 20
    
    # Check location match (20 points)
    max_score += 20
    locations = criteria.get('locations', [])
    if locations and job_data.get('location'):
        if any(loc.lower() in job_data['location'].lower() for loc in locations):
            score += 20
    
    # Check salary range (20 points)
    max_score += 20
    salary_range = criteria.get('salary_range', {})
    if salary_range and job_data.get('salary_min'):
        min_salary = salary_range.get('min', 0)
        if job_data['salary_min'] >= min_salary:
            score += 20
    
    return (score / max_score * 100) if max_score > 0 else 0
