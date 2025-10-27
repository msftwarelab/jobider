"""
Base adapter class for job platforms
"""

from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
from src.utils.logger import setup_logger


class BasePlatformAdapter(ABC):
    """Abstract base class for all platform adapters"""
    
    def __init__(self, config, db):
        self.config = config
        self.db = db
        self.logger = setup_logger(f'adapter.{self.platform_name}')
        self.driver = None
        self.is_logged_in = False
    
    @property
    @abstractmethod
    def platform_name(self):
        """Return the name of the platform (e.g., 'dice', 'indeed')"""
        pass
    
    @abstractmethod
    def login(self):
        """Login to the platform"""
        pass
    
    @abstractmethod
    def search_jobs(self, keywords, location):
        """Search for jobs on the platform"""
        pass
    
    @abstractmethod
    def extract_job_details(self, job_element):
        """Extract job details from a job listing element"""
        pass
    
    @abstractmethod
    def apply_to_job(self, job_url, job_data):
        """Apply to a specific job"""
        pass
    
    def init_driver(self):
        """Initialize Selenium WebDriver"""
        if self.driver:
            return
        
        self.logger.info("Initializing Chrome WebDriver...")
        
        chrome_options = Options()
        
        # Headless mode
        headless = os.getenv('HEADLESS_MODE', 'true').lower() == 'true'
        if headless:
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--disable-gpu')
        
        # Performance optimizations
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Disable images and CSS for faster loading (optional)
        # prefs = {"profile.managed_default_content_settings.images": 2}
        # chrome_options.add_experimental_option("prefs", prefs)
        
        # User agent to avoid detection
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Set page load timeout
        self.driver.set_page_load_timeout(30)
        
        # Set timeouts
        self.driver.implicitly_wait(10)
        
        self.logger.info("WebDriver initialized successfully")
    
    def close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            self.logger.info("Closing WebDriver...")
            self.driver.quit()
            self.driver = None
    
    def wait_for_element(self, by, value, timeout=10, silent=False):
        """Wait for an element to be present"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except Exception as e:
            if not silent:
                self.logger.error(f"Element not found: {value} - {str(e)}")
            return None
    
    def wait_and_click(self, by, value, timeout=10):
        """Wait for an element and click it"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            element.click()
            return True
        except Exception as e:
            self.logger.error(f"Could not click element: {value} - {str(e)}")
            return False
    
    def safe_find_element(self, by, value):
        """Safely find an element, return None if not found"""
        try:
            return self.driver.find_element(by, value)
        except:
            return None
    
    def safe_find_elements(self, by, value):
        """Safely find elements, return empty list if not found"""
        try:
            return self.driver.find_elements(by, value)
        except:
            return []
    
    def save_screenshot(self, name):
        """Save a screenshot for debugging"""
        if self.driver:
            screenshot_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'screenshots')
            os.makedirs(screenshot_dir, exist_ok=True)
            filepath = os.path.join(screenshot_dir, f"{name}.png")
            self.driver.save_screenshot(filepath)
            self.logger.debug(f"Screenshot saved: {filepath}")
    
    def check_duplicate(self, job_id):
        """Check if job or application already exists"""
        if self.db.job_exists(job_id, self.platform_name):
            self.logger.debug(f"Job {job_id} already in database")
            
        if self.db.application_exists(job_id, self.platform_name):
            self.logger.debug(f"Already applied to job {job_id}")
            return True
        
        return False
    
    def save_job(self, job_data):
        """Save job to database"""
        try:
            if not self.db.job_exists(job_data['job_id'], self.platform_name):
                job_data['platform'] = self.platform_name
                self.db.save_job(job_data)
                self.logger.info(f"Saved job: {job_data['title']} at {job_data['company']}")
        except Exception as e:
            self.logger.error(f"Error saving job: {str(e)}")
    
    def save_application(self, job_id, success=True, error_message=None, match_score=None):
        """Save application record to database"""
        try:
            app_data = {
                'job_id': job_id,
                'platform': self.platform_name,
                'success': success,
                'error_message': error_message,
                'match_score': match_score,
                'application_method': 'automated'
            }
            self.db.save_application(app_data)
            
            if success:
                self.logger.info(f"Application recorded: {job_id}")
            else:
                self.logger.error(f"Failed application recorded: {job_id} - {error_message}")
        except Exception as e:
            self.logger.error(f"Error saving application: {str(e)}")
    
    def run(self, search_only=False):
        """Main execution flow"""
        try:
            self.init_driver()
            self.login()
            
            # Get search criteria from config
            criteria = self.config['search_criteria']
            keywords_list = criteria.get('keywords', [])
            locations = criteria.get('locations', [])
            
            total_jobs_found = 0
            total_applications = 0
            
            # Search for each keyword-location combination
            for keywords in keywords_list:
                for location in locations:
                    self.logger.info(f"Searching: '{keywords}' in '{location}'")
                    
                    jobs = self.search_jobs(keywords, location)
                    total_jobs_found += len(jobs)
                    
                    self.logger.info(f"Found {len(jobs)} jobs")
                    
                    if not search_only:
                        # Apply to jobs
                        for job in jobs:
                            # Check if already applied
                            if self.check_duplicate(job['job_id']):
                                continue
                            
                            # Apply to job
                            try:
                                success = self.apply_to_job(job['url'], job)
                                if success:
                                    total_applications += 1
                            except Exception as e:
                                self.logger.error(f"Error applying to job: {str(e)}")
                                self.save_application(job['job_id'], success=False, error_message=str(e))
            
            self.logger.info(f"Session complete: Found {total_jobs_found} jobs, Applied to {total_applications}")
            
            return {
                'jobs_found': total_jobs_found,
                'applications_submitted': total_applications
            }
            
        except Exception as e:
            self.logger.error(f"Error in run: {str(e)}")
            raise
        finally:
            self.close_driver()
