"""
Dice.com platform adapter
"""

import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from .base_adapter import BasePlatformAdapter
from src.utils.helpers import extract_salary, calculate_match_score


class DiceAdapter(BasePlatformAdapter):
    """Adapter for Dice.com job platform"""
    
    DICE_URL = "https://www.dice.com"
    LOGIN_URL = "https://www.dice.com/dashboard/login"
    SEARCH_URL = "https://www.dice.com/jobs"
    
    @property
    def platform_name(self):
        return "dice"
    
    def login(self):
        """Login to Dice.com - Two-step process: email first, then password"""
        if self.is_logged_in:
            return True
        
        email = os.getenv('DICE_EMAIL')
        password = os.getenv('DICE_PASSWORD')
        
        if not email or not password:
            self.logger.error("Dice credentials not found in environment variables")
            return False
        
        try:
            self.logger.info("Logging into Dice.com...")
            self.driver.get(self.LOGIN_URL)
            time.sleep(3)
            self.save_screenshot("dice_login_page")
            
            # STEP 1: Enter email
            self.logger.info("Step 1: Entering email...")
            email_input = self.wait_for_element(By.CSS_SELECTOR, "input[name='email']", timeout=10)
            
            if not email_input:
                email_input = self.wait_for_element(By.CSS_SELECTOR, "input[type='email']", timeout=5)
            
            if email_input:
                email_input.clear()
                time.sleep(0.5)
                email_input.send_keys(email)
                time.sleep(1)
                self.logger.info("Email entered successfully")
                self.save_screenshot("dice_email_entered")
            else:
                self.logger.error("Email input not found")
                self.save_screenshot("dice_no_email_input")
                return False
            
            # Click Continue button
            self.logger.info("Clicking Continue button...")
            continue_button = self.wait_for_element(By.CSS_SELECTOR, "button[data-testid='sign-in-button']", timeout=5)
            
            if not continue_button:
                continue_button = self.safe_find_element(By.XPATH, "//button[contains(text(), 'Continue')]")
            
            if not continue_button:
                continue_button = self.safe_find_element(By.CSS_SELECTOR, "button[type='submit']")
            
            if continue_button:
                continue_button.click()
                time.sleep(3)
                self.logger.info("Continue button clicked")
                self.save_screenshot("dice_after_continue")
            else:
                self.logger.warning("Continue button not found, trying Enter key")
                email_input.send_keys(Keys.RETURN)
                time.sleep(3)
            
            # STEP 2: Enter password
            self.logger.info("Step 2: Entering password...")
            password_input = self.wait_for_element(By.CSS_SELECTOR, "input[name='password']", timeout=10)
            
            if not password_input:
                password_input = self.wait_for_element(By.CSS_SELECTOR, "input[type='password']", timeout=5)
            
            if password_input:
                password_input.clear()
                time.sleep(0.5)
                password_input.send_keys(password)
                time.sleep(1)
                self.logger.info("Password entered successfully")
                self.save_screenshot("dice_password_entered")
            else:
                self.logger.error("Password input not found")
                self.save_screenshot("dice_no_password_input")
                return False
            
            # Click Sign In button
            self.logger.info("Clicking Sign In button...")
            signin_button = self.wait_for_element(By.CSS_SELECTOR, "button[data-testid='submit-password']", timeout=5)
            
            if not signin_button:
                signin_button = self.safe_find_element(By.XPATH, "//button[contains(text(), 'Sign In')]")
            
            if not signin_button:
                signin_button = self.safe_find_element(By.CSS_SELECTOR, "button[type='submit']")
            
            if signin_button:
                signin_button.click()
                time.sleep(5)
                self.logger.info("Sign In button clicked")
                self.save_screenshot("dice_after_signin")
            else:
                self.logger.error("Sign In button not found")
                self.save_screenshot("dice_no_signin_button")
                return False
            
            # Verify login success
            self.logger.info("Verifying login...")
            time.sleep(3)
            
            current_url = self.driver.current_url.lower()
            if "home-feed" in current_url or "dashboard" in current_url:
                self.logger.info("✓ Successfully logged into Dice.com!")
                self.is_logged_in = True
                return True
            else:
                # Wait a bit more and check again
                time.sleep(3)
                current_url = self.driver.current_url.lower()
                if "login" not in current_url:
                    self.logger.info("✓ Login appears successful (not on login page)")
                    self.is_logged_in = True
                    return True
                else:
                    self.logger.error("✗ Login verification failed")
                    return False
                
        except Exception as e:
            self.logger.error(f"Login error: {str(e)}")
            self.save_screenshot("dice_login_exception")
            return False
    
    def search_jobs(self, keywords, location="Remote", max_results=50):
        """Search for jobs on Dice.com - go directly to filtered URL (single page)"""
        # This method is kept for compatibility but not used directly
        # Use search_jobs_on_page instead for page-by-page processing
        return self.search_jobs_on_page(1)
    
    def search_jobs_on_page(self, page_num):
        """Search for jobs on a specific page"""
        try:
            # Get search query from environment variable
            search_query = os.getenv('DICE_SEARCH_QUERY', 'python')
            
            # URL encode the search query (replace spaces with +)
            encoded_query = search_query.replace(' ', '+')
            
            # Build URL with page number
            if page_num == 1:
                filtered_url = f"https://www.dice.com/jobs?filters.workplaceTypes=Remote&q={encoded_query}"
            else:
                filtered_url = f"https://www.dice.com/jobs?filters.workplaceTypes=Remote&q={encoded_query}&page={page_num}"
            
            self.logger.info(f"Navigating to page {page_num}: {filtered_url}")
            self.driver.get(filtered_url)
            time.sleep(4)
            
            # Check if we got redirected (means no more pages)
            current_url = self.driver.current_url
            if page_num > 1 and f"page={page_num}" not in current_url:
                self.logger.info(f"Redirected from page {page_num}, no more pages available.")
                return None  # Signal that pagination should stop
            
            self.save_screenshot(f"search_results_page_{page_num}")
            
            # Extract job listings from current page
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, "div[data-testid='job-card']")
            
            if not job_cards:
                self.logger.info(f"No job cards found on page {page_num}.")
                return None  # Signal that pagination should stop
            
            self.logger.info(f"Found {len(job_cards)} job cards on page {page_num}")
            
            page_jobs = []
            for idx, card in enumerate(job_cards):
                try:
                    job_data = self.extract_job_details(card)
                    if job_data:
                        page_jobs.append(job_data)
                        self.logger.info(f"Extracted job {idx + 1}: {job_data.get('title', 'Unknown')}")
                except Exception as e:
                    self.logger.error(f"Error extracting job: {str(e)}")
                    continue
            
            self.logger.info(f"✓ Page {page_num} complete. Found {len(page_jobs)} jobs on this page")
            return page_jobs
            
        except Exception as e:
            self.logger.error(f"Error searching jobs on page {page_num}: {str(e)}")
            self.save_screenshot("search_error")
            return None
    
    def extract_job_details(self, card_element):
        """Extract job details from a job card element"""
        try:
            job_data = {}
            
            # Job title
            try:
                title_elem = card_element.find_element(By.CSS_SELECTOR, "a[data-testid='job-search-job-detail-link']")
                job_data['title'] = title_elem.text.strip()
                job_data['url'] = title_elem.get_attribute('href')
            except:
                return None
            
            # Company name
            try:
                company_elem = card_element.find_element(By.CSS_SELECTOR, "a[href*='company-profile']")
                job_data['company'] = company_elem.text.strip()
            except:
                job_data['company'] = "Unknown"
            
            # Location
            try:
                location_elem = card_element.find_element(By.XPATH, ".//p[contains(text(), 'Remote') or contains(text(), 'Hybrid')]")
                job_data['location'] = location_elem.text.strip()
            except:
                job_data['location'] = "Not specified"
            
            # Salary
            try:
                salary_elem = card_element.find_element(By.CSS_SELECTOR, "p[id='salary-label']")
                job_data['salary'] = salary_elem.text.strip()
            except:
                job_data['salary'] = None
            
            # Description (summary from card)
            try:
                desc_elem = card_element.find_element(By.CSS_SELECTOR, "p.line-clamp-2")
                job_data['description'] = desc_elem.text.strip()
            except:
                job_data['description'] = ""
            
            # Job ID
            try:
                job_data['job_id'] = card_element.get_attribute('data-id')
            except:
                job_data['job_id'] = None
            
            # Store the card element reference for later clicking
            job_data['_card_element'] = card_element
            
            return job_data
            
        except Exception as e:
            self.logger.error(f"Error extracting job details: {str(e)}")
            return None
    
    def apply_to_job(self, job_url, job_data):
        """Apply to a job on Dice.com"""
        original_window = self.driver.current_window_handle
        
        try:
            self.logger.info(f"Applying to job: {job_url}")
            
            # Get resume filename from environment variable
            resume_filename = os.getenv('RESUME_FILENAME', 'Julian_Thomas.docx')
            resume_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'resumes', resume_filename)
            
            if not os.path.exists(resume_path):
                self.logger.error(f"Resume file not found: {resume_path}")
                self.logger.error(f"Please ensure '{resume_filename}' exists in the resumes/ folder")
                return False
            
            self.logger.info(f"Using resume: {resume_filename}")
            
            # Navigate to job page
            self.driver.get(job_url)
            time.sleep(3)
            self.save_screenshot("job_detail_page")
            
            # Look for Easy Apply button (custom web component)
            easy_apply_button = None
            try:
                # Try the custom web component selector first
                easy_apply_button = self.wait_for_element(By.CSS_SELECTOR, "apply-button-wc", timeout=5)
                if not easy_apply_button:
                    # Try traditional button selectors
                    easy_apply_button = self.wait_for_element(By.CSS_SELECTOR, "button.btn-primary", timeout=5)
                    if not easy_apply_button or "Easy apply" not in easy_apply_button.text:
                        # Try alternative selectors
                        easy_apply_button = self.wait_for_element(By.XPATH, "//button[contains(., 'Easy Apply') or contains(., 'Easy apply')]", timeout=5)
            except:
                self.logger.warning("Easy Apply button not found - skipping to next job")
                return False
            
            if not easy_apply_button:
                self.logger.warning("Easy Apply button not found - skipping to next job")
                return False
            
            easy_apply_button.click()
            self.logger.info("Clicked Easy Apply button")
            time.sleep(3)
            self.save_screenshot("apply_form_opened")
            
            # Check if Replace button exists - if not, job may already be applied
            replace_clicked = False
            file_input_found = False
            
            try:
                # Try to find Replace button/link
                replace_selectors = [
                    "button.file-remove",
                    "//button[contains(@class, 'file-remove')]",
                    "//span[contains(@class, 'file-remove-subtext')]",
                    "//span[contains(., 'Replace')]",
                    "//button[contains(., 'Replace')]",
                    ".file-remove-subtext"
                ]
                
                for selector in replace_selectors:
                    try:
                        if selector.startswith("//"):
                            replace_button = self.wait_for_element(By.XPATH, selector, timeout=2, silent=True)
                        else:
                            replace_button = self.wait_for_element(By.CSS_SELECTOR, selector, timeout=2, silent=True)
                        
                        if replace_button:
                            replace_button.click()
                            self.logger.info("Clicked Replace button")
                            replace_clicked = True
                            time.sleep(2)
                            break
                    except:
                        continue
                
                if not replace_clicked:
                    self.logger.info("Replace button not found, checking if resume already uploaded...")
                    # Check if we can find upload button without Replace (resume not uploaded yet)
                    upload_check = self.driver.find_elements(By.XPATH, "//span[contains(., 'Upload')]")
                    if not upload_check:
                        self.logger.warning("No Replace or Upload button found - job may already be applied. Skipping to next job.")
                        return False
            except:
                self.logger.info("Replace button not found, will check file input")
            
            # Wait for file picker dialog and upload
            try:
                # Look for file input - try specific ID first
                file_input = None
                file_input_found = False
                try:
                    file_input = self.driver.find_element(By.CSS_SELECTOR, "input#fsp-fileUpload")
                except:
                    # Fallback to generic file inputs
                    file_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
                    if file_inputs:
                        file_input = file_inputs[-1]
                
                if file_input:
                    file_input_found = True
                    
                    # Convert resume path to absolute path
                    abs_resume_path = os.path.abspath(resume_path)
                    file_input.send_keys(abs_resume_path)
                    self.logger.info(f"Resume selected: {abs_resume_path}")
                    time.sleep(2)
                    
                    # Click Upload button
                    upload_button = None
                    try:
                        # Try specific selectors for the upload button
                        upload_button = self.driver.find_element(By.CSS_SELECTOR, "span.fsp-button-upload")
                    except:
                        try:
                            upload_button = self.driver.find_element(By.CSS_SELECTOR, "span[data-e2e='upload']")
                        except:
                            # Fallback to text-based search
                            upload_button = self.wait_for_element(By.XPATH, "//span[contains(., 'Upload')]", timeout=5)
                    
                    if upload_button:
                        upload_button.click()
                        self.logger.info("Clicked Upload button")
                        time.sleep(3)
                        self.save_screenshot("resume_uploaded")
                    else:
                        self.logger.warning("Upload button not found - skipping to next job")
                        return False
                else:
                    self.logger.warning("No file input found - skipping to next job")
                    return False
            except Exception as e:
                self.logger.warning(f"Error uploading resume: {str(e)} - skipping to next job")
                self.save_screenshot("upload_error")
                return False
            
            # Click Next button
            try:
                next_button = self.wait_for_element(By.CSS_SELECTOR, "button.btn-next", timeout=5)
                if not next_button:
                    next_button = self.wait_for_element(By.XPATH, "//button[contains(., 'Next')]", timeout=5)
                
                if next_button:
                    next_button.click()
                    self.logger.info("Clicked Next button")
                    time.sleep(3)
                    self.save_screenshot("after_next")
            except Exception as e:
                self.logger.warning(f"Could not find/click Next button: {str(e)} - will try to submit anyway")
            
            # Click Submit button
            try:
                submit_button = None
                try:
                    # Try specific selector for Submit button with seds-button-primary class
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, "button.seds-button-primary")
                except:
                    try:
                        # Try button containing Submit text
                        submit_button = self.driver.find_element(By.XPATH, "//button[contains(., 'Submit')]")
                    except:
                        # Fallback to generic submit button
                        submit_button = self.wait_for_element(By.CSS_SELECTOR, "button[type='submit']", timeout=5)
                
                if submit_button:
                    submit_button.click()
                    self.logger.info("Clicked Submit button")
                    time.sleep(3)
                    self.save_screenshot("application_submitted")
                    self.logger.info("✓ Application submitted successfully")
                    
                    # Close the application tab/window if opened in new tab
                    try:
                        if len(self.driver.window_handles) > 1:
                            self.driver.close()
                            self.driver.switch_to.window(original_window)
                            self.logger.info("Closed application window and returned to main window")
                    except:
                        pass
                    
                    return True
                else:
                    self.logger.warning("Submit button not found - skipping to next job")
                    return False
            except Exception as e:
                self.logger.warning(f"Error clicking Submit button: {str(e)} - skipping to next job")
                self.save_screenshot("submit_error")
                return False
            
        except Exception as e:
            self.logger.warning(f"Error applying to job: {str(e)} - skipping to next job")
            self.save_screenshot("apply_error")
            
            # Try to return to original window
            try:
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                self.driver.switch_to.window(original_window)
            except:
                pass
            
            return False
    
    def run(self, search_only=False):
        """Override run method to process jobs page by page"""
        try:
            self.init_driver()
            self.login()
            
            total_jobs_found = 0
            total_applications = 0
            max_pages = 30
            
            self.logger.info(f"Starting page-by-page job application process...")
            
            # Process pages 1 through 30
            for page_num in range(1, max_pages + 1):
                self.logger.info(f"\n{'='*60}")
                self.logger.info(f"PROCESSING PAGE {page_num}")
                self.logger.info(f"{'='*60}")
                
                # Search jobs on this page
                jobs = self.search_jobs_on_page(page_num)
                
                # Check if pagination should stop
                if jobs is None:
                    self.logger.info(f"No more pages available. Stopping at page {page_num - 1}.")
                    break
                
                if len(jobs) == 0:
                    self.logger.info(f"No jobs found on page {page_num}. Stopping pagination.")
                    break
                
                total_jobs_found += len(jobs)
                self.logger.info(f"Found {len(jobs)} jobs on page {page_num}")
                
                if not search_only:
                    # Apply to each job on this page
                    page_applications = 0
                    for idx, job in enumerate(jobs, 1):
                        self.logger.info(f"\n--- Job {idx}/{len(jobs)} on page {page_num} ---")
                        
                        # Check if already applied
                        if self.check_duplicate(job['job_id']):
                            self.logger.info(f"Already applied to this job. Skipping.")
                            continue
                        
                        # Save job to database
                        self.save_job(job)
                        
                        # Apply to job
                        try:
                            success = self.apply_to_job(job['url'], job)
                            if success:
                                page_applications += 1
                                total_applications += 1
                                self.save_application(job['job_id'], success=True)
                            else:
                                self.save_application(job['job_id'], success=False, error_message="Application failed")
                        except Exception as e:
                            self.logger.error(f"Error applying to job: {str(e)}")
                            self.save_application(job['job_id'], success=False, error_message=str(e))
                    
                    self.logger.info(f"\n✓ Page {page_num} complete: Applied to {page_applications}/{len(jobs)} jobs")
                    self.logger.info(f"Session totals so far: {total_jobs_found} jobs found, {total_applications} applications submitted")
            
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"SESSION COMPLETE")
            self.logger.info(f"{'='*60}")
            self.logger.info(f"Total pages processed: {page_num if jobs is None else page_num}")
            self.logger.info(f"Total jobs found: {total_jobs_found}")
            self.logger.info(f"Total applications submitted: {total_applications}")
            
            return {
                'jobs_found': total_jobs_found,
                'applications_submitted': total_applications
            }
            
        except Exception as e:
            self.logger.error(f"Error in run: {str(e)}")
            raise
        finally:
            self.close_driver()
