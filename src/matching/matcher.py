"""
Job matching engine
"""

from src.utils.helpers import calculate_match_score, match_keywords


class JobMatcher:
    """Match jobs against user criteria"""
    
    def __init__(self, config):
        self.config = config
        self.criteria = config['search_criteria']
    
    def matches(self, job_data):
        """Check if job matches criteria"""
        # Calculate overall match score
        score = calculate_match_score(job_data, self.criteria)
        
        # Minimum threshold
        if score < 60:
            return False, score
        
        return True, score
    
    def filter_jobs(self, jobs):
        """Filter a list of jobs by criteria"""
        matched_jobs = []
        
        for job in jobs:
            matches, score = self.matches(job)
            if matches:
                job['match_score'] = score
                matched_jobs.append(job)
        
        # Sort by match score (descending)
        matched_jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        return matched_jobs
