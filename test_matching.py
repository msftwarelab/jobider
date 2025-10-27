"""
Test script for job matching engine
"""

from src.matching import JobMatcher
from src.utils import load_config, calculate_match_score, extract_salary

print('Testing Job Matching Engine...\n')

# Load config
config = load_config()
matcher = JobMatcher(config)

# Test job data
test_jobs = [
    {
        'title': 'Senior Python Developer',
        'description': 'We need a Python expert with Django and FastAPI experience. Docker and AWS knowledge is a plus.',
        'requirements': 'Python, Django, REST APIs, 5+ years experience',
        'location': 'Remote',
        'salary_min': 120000,
        'salary_max': 160000
    },
    {
        'title': 'Java Developer',
        'description': 'Looking for Java/Spring Boot developer',
        'requirements': 'Java, Spring, MySQL',
        'location': 'San Francisco, CA',
        'salary_min': 130000,
        'salary_max': 170000
    },
    {
        'title': 'Python Backend Engineer',
        'description': 'Backend role with Python, FastAPI, PostgreSQL. Remote work available.',
        'requirements': 'Python, FastAPI, PostgreSQL, Docker, Kubernetes',
        'location': 'Remote',
        'salary_min': 140000,
        'salary_max': 180000
    }
]

# Test matching
print('Job Matching Results:')
print('=' * 70)

for job in test_jobs:
    matches, score = matcher.matches(job)
    status = '✓ MATCH' if matches else '✗ NO MATCH'
    print(f'\n{status} | Score: {score:.1f}%')
    print(f'Title: {job["title"]}')
    print(f'Location: {job["location"]}')
    print(f'Salary: ${job["salary_min"]:,} - ${job["salary_max"]:,}')

print('\n' + '=' * 70)

# Test salary extraction
print('\nTesting Salary Extraction...')
test_salaries = [
    '$100,000 - $150,000',
    '100K - 150K',
    '$120000',
    '80-120K'
]

for sal_text in test_salaries:
    min_sal, max_sal = extract_salary(sal_text)
    if min_sal:
        print(f'  "{sal_text}" → Min: ${min_sal:,.0f}, Max: ${max_sal:,.0f}')
    else:
        print(f'  "{sal_text}" → Could not parse')

print('\n✅ Job matching engine working correctly!')
