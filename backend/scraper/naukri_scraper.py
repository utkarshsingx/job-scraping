"""
Naukri.com job scraper using Selenium WebDriver
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import urllib.parse
import os
import shutil
import requests
import json
import random
import string


class NaukriScraper:
    """Scraper for naukri.com job listings"""
    
    def __init__(self, headless=True):
        """Initialize the scraper with Chrome WebDriver"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--remote-debugging-port=9222')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Initialize ChromeDriver with better error handling
        try:
            # Clear cache and get fresh driver
            driver_cache_path = os.path.expanduser('~/.wdm/drivers/chromedriver')
            if os.path.exists(driver_cache_path):
                try:
                    shutil.rmtree(driver_cache_path)
                    print("Cleared ChromeDriver cache")
                except Exception as e:
                    print(f"Note: Could not clear cache: {e}")
            
            # Install ChromeDriver
            initial_path = ChromeDriverManager().install()
            print(f"ChromeDriverManager returned path: {initial_path}")
            
            # ChromeDriverManager sometimes returns wrong file (like THIRD_PARTY_NOTICES.chromedriver)
            # Always search for the actual chromedriver executable
            driver_dir = os.path.dirname(initial_path)
            driver_path = None
            
            # Helper function to check if a path is the actual chromedriver executable
            def is_valid_chromedriver(path):
                if not os.path.exists(path):
                    return False
                # Check if it's a text file (wrong file)
                if 'THIRD_PARTY' in path or 'LICENSE' in path:
                    return False
                # Check file size (chromedriver is > 10MB, text files are < 1MB)
                try:
                    size = os.path.getsize(path)
                    if size < 1000000:  # Less than 1MB is likely not the executable
                        return False
                    # Check if executable or can be made executable
                    return os.path.isfile(path) and (os.access(path, os.X_OK) or True)
                except:
                    return False
            
            # First, check if the returned path is correct
            if is_valid_chromedriver(initial_path):
                driver_path = initial_path
            else:
                # Search in the same directory as the returned path
                same_dir_path = os.path.join(driver_dir, 'chromedriver')
                if is_valid_chromedriver(same_dir_path):
                    driver_path = same_dir_path
                else:
                    # Search in subdirectories
                    if os.path.exists(driver_dir):
                        for item in os.listdir(driver_dir):
                            item_path = os.path.join(driver_dir, item)
                            if os.path.isdir(item_path):
                                chromedriver_path = os.path.join(item_path, 'chromedriver')
                                if is_valid_chromedriver(chromedriver_path):
                                    driver_path = chromedriver_path
                                    break
                    
                    # If still not found, do recursive search
                    if not driver_path and os.path.exists(driver_cache_path):
                        def find_chromedriver_recursive(directory):
                            for root, dirs, files in os.walk(directory):
                                for file in files:
                                    if file == 'chromedriver':
                                        full_path = os.path.join(root, file)
                                        if is_valid_chromedriver(full_path):
                                            return full_path
                            return None
                        
                        driver_path = find_chromedriver_recursive(driver_cache_path)
            
            if not driver_path:
                raise Exception(f"Could not find valid chromedriver executable. Searched in: {driver_dir}")
            
            print(f"Using chromedriver at: {driver_path}")
            
            # Verify the driver path exists and make it executable if needed
            if not os.path.exists(driver_path):
                raise Exception(f"ChromeDriver not found at {driver_path}")
            
            # Ensure it's executable
            if not os.access(driver_path, os.X_OK):
                try:
                    os.chmod(driver_path, 0o755)
                    print(f"Made chromedriver executable: {driver_path}")
                except Exception as e:
                    print(f"Warning: Could not make chromedriver executable: {e}")
            
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(30)  # 30 second timeout
            self.wait = WebDriverWait(self.driver, 20)
            
        except Exception as e:
            print(f"Error initializing ChromeDriver: {e}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Failed to initialize ChromeDriver. Make sure Chrome browser is installed. Error: {str(e)}")
    
    def build_url(self, job_type, keyword, location, experience=None):
        """
        Build Naukri.com search URL from parameters
        
        Args:
            job_type: 'job' or 'internship'
            keyword: Job search keyword
            location: Job location
            experience: Years of experience (optional)
        
        Returns:
            Complete URL string
        """
        # Format keyword for URL (lowercase, replace spaces with hyphens)
        keyword_formatted = keyword.lower().replace(' ', '-')
        location_formatted = location.lower().replace(' ', '-')
        
        # Build base URL - correct format for internships
        if job_type.lower() == 'internship':
            base_url = f"https://www.naukri.com/{keyword_formatted}-internship-jobs-in-{location_formatted}"
        else:
            base_url = f"https://www.naukri.com/{keyword_formatted}-jobs-in-{location_formatted}"
        
        # Add query parameters
        params = {
            'k': keyword,
            'l': location
        }
        
        if experience is not None:
            params['experience'] = experience
        
        # Add internship-specific parameters
        if job_type.lower() == 'internship':
            params['qproductJobSource'] = '2'
            params['qinternshipFlag'] = 'true'
            params['naukriCampus'] = 'true'
        
        query_string = urllib.parse.urlencode(params)
        full_url = f"{base_url}?{query_string}"
        
        return full_url
    
    def scrape_jobs(self, job_type, keyword, location, experience=None, max_jobs=20, page=1):
        """
        Scrape jobs from Naukri.com
        
        Args:
            job_type: 'job' or 'internship'
            keyword: Job search keyword
            location: Job location
            experience: Years of experience (optional)
            max_jobs: Maximum number of jobs to scrape
            page: Page number for pagination (default: 1)
        
        Returns:
            Tuple of (list of job dictionaries, metadata dict with 'source' and 'debug_info')
        """
        # For web scraping, append page number to URL if page > 1
        if page > 1:
            url = self.build_url(job_type, keyword, location, experience) + f"&page={page}"
        else:
            url = self.build_url(job_type, keyword, location, experience)
        print(f"[SCRAPER] Starting web scraping for URL: {url}")
        
        metadata = {
            'source': 'scraping',
            'debug_info': {
                'scraping_attempted': True,
                'scraping_success': False,
                'api_fallback_used': False,
                'scraping_errors': [],
                'api_errors': []
            }
        }
        
        try:
            self.driver.get(url)
            # Reduced initial wait time - wait for specific element instead
            time.sleep(2)  # Reduced from 5 seconds
            
            # Handle popups or modals if they appear (non-blocking)
            try:
                popup_selectors = [
                    "//button[contains(text(), 'Close')]",
                    "//button[contains(text(), 'Skip')]",
                    "//span[contains(@class, 'close')]",
                    "//div[contains(@class, 'closeIcon')]"
                ]
                for selector in popup_selectors:
                    try:
                        popup = self.driver.find_element(By.XPATH, selector)
                        if popup and popup.is_displayed():
                            popup.click()
                            time.sleep(0.5)
                            break
                    except:
                        continue
            except:
                pass  # No popup found
            
            # Wait for job cards container to load with reduced timeout
            container_xpaths = [
                "/html/body/div[1]/div/main/div[1]/div[2]/div[2]/div/div[1]",
                "//div[contains(@class, 'srp-jobtuple-wrapper')]",
                "//div[contains(@class, 'jobTuple')]"
            ]
            
            container_found = False
            short_wait = WebDriverWait(self.driver, 5)  # Reduced from 20 seconds
            for xpath in container_xpaths:
                try:
                    short_wait.until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    container_found = True
                    break
                except:
                    continue
            
            if not container_found:
                error_msg = "Job cards container not found - scraping failed"
                print(f"[SCRAPER] {error_msg}")
                metadata['debug_info']['scraping_errors'].append(error_msg)
                # Try API fallback
                print("[SCRAPER] Attempting API fallback due to container not found...")
                api_jobs, api_metadata = self.scrape_jobs_via_api(job_type, keyword, location, experience, max_jobs)
                if api_jobs and len(api_jobs) > 0:
                    metadata['source'] = 'api_fallback'
                    metadata['debug_info']['api_fallback_used'] = True
                    metadata['debug_info'].update(api_metadata.get('debug_info', {}))
                    print(f"[SCRAPER] API fallback successful: returned {len(api_jobs)} jobs")
                    return api_jobs, metadata
                return [], metadata
            
            # Quick scroll to load content (no wait needed)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)  # Reduced from 3 seconds
            
            jobs = []
            card_index = 1
            
            # Extract job cards using the provided XPath structure
            while len(jobs) < max_jobs:
                card_xpath = f"/html/body/div[1]/div/main/div[1]/div[2]/div[2]/div/div[1]/div[{card_index}]"
                
                try:
                    card_element = self.driver.find_element(By.XPATH, card_xpath)
                    
                    job_data = self._extract_job_data(card_element, card_index)
                    
                    if job_data and job_data.get('job_title'):  # Only add if we got valid data
                        jobs.append(job_data)
                    
                    card_index += 1
                except Exception as e:
                    # Try alternative XPath or move to next
                    try:
                        alt_xpath = f"/html/body/div[1]/div/main/div[1]/div[2]/div[2]/div/div[{card_index}]/div"
                        card_element = self.driver.find_element(By.XPATH, alt_xpath)
                        job_data = self._extract_job_data(card_element, card_index)
                        if job_data and job_data.get('job_title'):
                            jobs.append(job_data)
                        card_index += 1
                    except:
                        # No more cards found
                        if card_index > 10:  # Safety check
                            break
                        card_index += 1
                        if card_index > 50:  # Safety limit
                            break
            
            # Mark scraping as successful if we got jobs
            if len(jobs) > 0:
                metadata['debug_info']['scraping_success'] = True
                print(f"[SCRAPER] Scraping successful: found {len(jobs)} jobs")
                return jobs, metadata
            
            # If scraping returned no jobs, try API fallback
            print("[SCRAPER] No jobs found via scraping, trying API fallback...")
            metadata['debug_info']['scraping_errors'].append("No jobs found in scraping results")
            api_jobs, api_metadata = self.scrape_jobs_via_api(job_type, keyword, location, experience, max_jobs, page)
            if api_jobs and len(api_jobs) > 0:
                metadata['source'] = 'api_fallback'
                metadata['debug_info']['api_fallback_used'] = True
                metadata['debug_info'].update(api_metadata.get('debug_info', {}))
                print(f"[SCRAPER] API fallback successful: returned {len(api_jobs)} jobs")
                return api_jobs, metadata
            
            print("[SCRAPER] Both scraping and API fallback returned no jobs")
            return jobs, metadata
            
        except Exception as e:
            error_msg = f"Error scraping jobs: {str(e)}"
            print(f"[SCRAPER] {error_msg}")
            import traceback
            traceback.print_exc()
            metadata['debug_info']['scraping_errors'].append(error_msg)
            
            # Try API as fallback even on error
            try:
                print("[SCRAPER] Attempting API fallback after scraping error...")
                api_jobs, api_metadata = self.scrape_jobs_via_api(job_type, keyword, location, experience, max_jobs, page)
                if api_jobs and len(api_jobs) > 0:
                    metadata['source'] = 'api_fallback'
                    metadata['debug_info']['api_fallback_used'] = True
                    metadata['debug_info'].update(api_metadata.get('debug_info', {}))
                    print(f"[SCRAPER] API fallback successful after error: returned {len(api_jobs)} jobs")
                    return api_jobs, metadata
            except Exception as api_error:
                api_error_msg = f"API fallback also failed: {str(api_error)}"
                print(f"[SCRAPER] {api_error_msg}")
                metadata['debug_info']['api_errors'].append(api_error_msg)
            
            return [], metadata
    
    def build_api_url(self, job_type, keyword, location, experience=None, page_no=1):
        """
        Build Naukri.com API URL from parameters
        
        Args:
            job_type: 'job' or 'internship'
            keyword: Job search keyword
            location: Job location
            experience: Years of experience (optional)
            page_no: Page number for pagination
        
        Returns:
            Complete API URL string
        """
        keyword_formatted = keyword.lower().replace(' ', '-')
        
        # Build seoKey for the URL
        if job_type.lower() == 'internship':
            seo_key = f"{keyword_formatted}-internship-jobs"
        else:
            seo_key = f"{keyword_formatted}-jobs"
        
        # Build API URL parameters
        params = {
            'noOfResults': 20,
            'urlType': 'search_by_keyword',
            'searchType': 'adv',
            'keyword': keyword,
            'sort': 'p',
            'pageNo': page_no,
            'k': keyword,
            'src': 'jobsearchDesk',
            'seoKey': seo_key
        }
        
        if experience is not None:
            params['experience'] = experience
        
        # Add internship-specific parameters
        if job_type.lower() == 'internship':
            params['qproductJobSource'] = '2'
            params['qinternshipFlag'] = 'true'
            params['naukriCampus'] = 'true'
        
        # Generate a session ID (random)
        params['sid'] = ''.join(random.choices(string.digits, k=16))
        
        query_string = urllib.parse.urlencode(params)
        api_url = f"https://www.naukri.com/jobapi/v3/search?{query_string}"
        
        return api_url
    
    def scrape_jobs_via_api(self, job_type, keyword, location, experience=None, max_jobs=20, page=1):
        """
        Scrape jobs using Naukri.com API endpoint (fallback method)
        Uses cookies from Selenium session if available
        
        Args:
            job_type: 'job' or 'internship'
            keyword: Job search keyword
            location: Job location
            experience: Years of experience (optional)
            max_jobs: Maximum number of jobs to scrape
            page: Page number for pagination (default: 1)
        
        Returns:
            Tuple of (list of job dictionaries, metadata dict with 'source' and 'debug_info')
        """
        metadata = {
            'source': 'api',
            'debug_info': {
                'api_attempted': True,
                'api_success': False,
                'api_url': '',
                'api_status_code': None,
                'api_response_jobs_count': 0,
                'current_page': page
            }
        }
        
        try:
            api_url = self.build_api_url(job_type, keyword, location, experience, page)
            metadata['debug_info']['api_url'] = api_url
            print(f"[API] Attempting API request to: {api_url}")
            
            # Prepare headers - minimal set that might work
            headers = {
                'accept': 'application/json',
                'accept-language': 'en-US,en;q=0.9',
                'appid': '109',
                'clientid': 'd3skt0p',
                'content-type': 'application/json',
                'systemid': 'Naukri',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
                'referer': self.build_url(job_type, keyword, location, experience),
            }
            
            # Try to get cookies from Selenium session if driver exists
            cookies = {}
            if hasattr(self, 'driver') and self.driver:
                try:
                    selenium_cookies = self.driver.get_cookies()
                    for cookie in selenium_cookies:
                        cookies[cookie['name']] = cookie['value']
                except:
                    pass
            
            # Make API request with cookies
            session = requests.Session()
            if cookies:
                session.cookies.update(cookies)
            
            response = session.get(api_url, headers=headers, timeout=10)
            metadata['debug_info']['api_status_code'] = response.status_code
            print(f"[API] API response status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                no_of_jobs = data.get('noOfJobs', 0)
                metadata['debug_info']['api_response_jobs_count'] = no_of_jobs
                metadata['debug_info']['total_jobs_available'] = no_of_jobs
                print(f"[API] API Response received: noOfJobs={no_of_jobs}, page={page}")
                
                # Try different possible field names for job data
                job_data_list = None
                
                # Check common field names
                for field_name in ['jobDetails', 'jobDetailsList', 'jobs', 'results', 'data']:
                    if field_name in data and isinstance(data[field_name], list) and len(data[field_name]) > 0:
                        job_data_list = data[field_name]
                        break
                
                if job_data_list:
                    jobs = self._parse_api_job_data(job_data_list, max_jobs)
                    if jobs:
                        metadata['debug_info']['api_success'] = True
                        print(f"[API] API successfully parsed {len(jobs)} jobs")
                        return jobs, metadata
                
                # If noOfJobs > 0 but no job data found, try parsing the entire response
                if no_of_jobs > 0:
                    print(f"API indicates {no_of_jobs} jobs but job data not found in expected fields")
                    # Try to extract from any array in the response
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if isinstance(value, list) and len(value) > 0:
                                # Check if first item looks like job data
                                if isinstance(value[0], dict) and ('title' in value[0] or 'jobTitle' in value[0]):
                                    jobs = self._parse_api_job_data(value, max_jobs)
                                    if jobs:
                                        metadata['debug_info']['api_success'] = True
                                        print(f"[API] API successfully parsed {len(jobs)} jobs from alternative structure")
                                        return jobs, metadata
                
                print("[API] API returned no job data in response")
                return [], metadata
            else:
                error_msg = f"API request failed with status {response.status_code}"
                print(f"[API] {error_msg}: {response.text[:200]}")
                metadata['debug_info']['api_errors'] = [error_msg]
                return [], metadata
                
        except Exception as e:
            error_msg = f"Error in API scraping: {str(e)}"
            print(f"[API] {error_msg}")
            import traceback
            traceback.print_exc()
            metadata['debug_info']['api_errors'] = [error_msg]
            return [], metadata
    
    def _parse_api_job_data(self, job_details_list, max_jobs=20):
        """
        Parse job data from API response
        
        Args:
            job_details_list: List of job objects from API
            max_jobs: Maximum number of jobs to return
        
        Returns:
            List of job dictionaries in our format
        """
        jobs = []
        
        for job_detail in job_details_list[:max_jobs]:
            try:
                job_data = {
                    'job_title': '',
                    'company_name': '',
                    'company_logo': '',
                    'rating': '',
                    'reviews': '',
                    'experience': '',
                    'salary': '',
                    'location': '',
                    'job_description': '',
                    'tags': [],
                    'job_post_date': '',
                    'job_url': ''
                }
                
                # Extract job title
                if 'title' in job_detail:
                    job_data['job_title'] = job_detail['title']
                elif 'jobTitle' in job_detail:
                    job_data['job_title'] = job_detail['jobTitle']
                
                # Extract company name
                if 'companyName' in job_detail:
                    job_data['company_name'] = job_detail['companyName']
                elif 'company' in job_detail and isinstance(job_detail['company'], dict):
                    job_data['company_name'] = job_detail['company'].get('name', '')
                
                # Extract company logo
                if 'companyLogo' in job_detail:
                    job_data['company_logo'] = job_detail['companyLogo']
                elif 'company' in job_detail and isinstance(job_detail['company'], dict):
                    job_data['company_logo'] = job_detail['company'].get('logo', '')
                
                # Extract location
                if 'placeholders' in job_detail and isinstance(job_detail['placeholders'], list):
                    location_parts = []
                    for placeholder in job_detail['placeholders']:
                        if isinstance(placeholder, dict) and 'label' in placeholder:
                            location_parts.append(placeholder['label'])
                    if location_parts:
                        job_data['location'] = ', '.join(location_parts)
                
                # Extract experience
                if 'workExp' in job_detail and isinstance(job_detail['workExp'], dict):
                    min_exp = job_detail['workExp'].get('minExp', '')
                    max_exp = job_detail['workExp'].get('maxExp', '')
                    if min_exp and max_exp:
                        job_data['experience'] = f"{min_exp}-{max_exp} Yrs"
                    elif min_exp:
                        job_data['experience'] = f"{min_exp}+ Yrs"
                
                # Extract salary
                if 'salaryDetail' in job_detail:
                    salary_detail = job_detail['salaryDetail']
                    if isinstance(salary_detail, dict):
                        salary_label = salary_detail.get('label', '')
                        if salary_label:
                            job_data['salary'] = salary_label
                
                # Extract job description
                if 'description' in job_detail:
                    desc = job_detail['description']
                    if isinstance(desc, str):
                        job_data['job_description'] = desc[:500]  # Limit description length
                
                # Extract tags/skills
                if 'tagsAndSkills' in job_detail:
                    tags = job_detail['tagsAndSkills']
                    if isinstance(tags, list):
                        job_data['tags'] = [tag.get('label', tag) if isinstance(tag, dict) else str(tag) for tag in tags[:5]]
                
                # Extract job post date
                if 'createdDate' in job_detail:
                    job_data['job_post_date'] = job_detail['createdDate']
                elif 'postedDate' in job_detail:
                    job_data['job_post_date'] = job_detail['postedDate']
                
                # Extract job URL
                if 'jobUrl' in job_detail:
                    job_url = job_detail['jobUrl']
                    if job_url:
                        if job_url.startswith('/'):
                            job_url = f"https://www.naukri.com{job_url}"
                        job_data['job_url'] = job_url
                elif 'applyUrl' in job_detail:
                    job_url = job_detail['applyUrl']
                    if job_url:
                        if job_url.startswith('/'):
                            job_url = f"https://www.naukri.com{job_url}"
                        job_data['job_url'] = job_url
                elif 'jdURL' in job_detail:
                    job_url = job_detail['jdURL']
                    if job_url:
                        if job_url.startswith('/'):
                            job_url = f"https://www.naukri.com{job_url}"
                        job_data['job_url'] = job_url
                
                # Only add if we have at least a job title
                if job_data['job_title']:
                    jobs.append(job_data)
                    
            except Exception as e:
                print(f"Error parsing API job data: {e}")
                continue
        
        return jobs
    
    def _extract_job_data(self, card_element, card_index):
        """Extract data from a single job card element"""
        job_data = {
            'job_title': '',
            'company_name': '',
            'company_logo': '',
            'rating': '',
            'reviews': '',
            'experience': '',
            'salary': '',
            'location': '',
            'job_description': '',
            'tags': [],
            'job_post_date': '',
            'job_url': ''
        }
        
        try:
            # Row 1: Job title, company name, company logo
            try:
                title_element = card_element.find_element(By.XPATH, ".//div[1]/h2")
                job_data['job_title'] = title_element.text.strip()
                # Try to get job URL from title link
                try:
                    title_link = title_element.find_element(By.XPATH, ".//a")
                    job_url = title_link.get_attribute('href')
                    if job_url:
                        # Convert relative URLs to absolute
                        if job_url.startswith('/'):
                            job_url = f"https://www.naukri.com{job_url}"
                        job_data['job_url'] = job_url
                except:
                    pass
            except:
                # Try alternative
                try:
                    title_element = card_element.find_element(By.XPATH, ".//h2")
                    job_data['job_title'] = title_element.text.strip()
                    # Try to get job URL from title link
                    try:
                        title_link = title_element.find_element(By.XPATH, ".//a")
                        job_url = title_link.get_attribute('href')
                        if job_url:
                            if job_url.startswith('/'):
                                job_url = f"https://www.naukri.com{job_url}"
                            job_data['job_url'] = job_url
                    except:
                        pass
                except:
                    pass
            
            # Also try to get URL from card wrapper or any link in the card
            if not job_data.get('job_url'):
                try:
                    # Try to find any link that looks like a job detail link
                    card_link = card_element.find_element(By.XPATH, ".//a[contains(@href, 'job-listings') or contains(@href, '/jobs/')]")
                    job_url = card_link.get_attribute('href')
                    if job_url:
                        if job_url.startswith('/'):
                            job_url = f"https://www.naukri.com{job_url}"
                        job_data['job_url'] = job_url
                except:
                    pass
            
            try:
                logo_element = card_element.find_element(By.XPATH, ".//div[1]/span/img")
                job_data['company_logo'] = logo_element.get_attribute('src') or ''
            except:
                # Try alternative
                try:
                    logo_element = card_element.find_element(By.XPATH, ".//span/img")
                    job_data['company_logo'] = logo_element.get_attribute('src') or ''
                except:
                    pass
            
            try:
                # Company name is in div[2]/span/a[1] according to XPath structure
                company_link = card_element.find_element(By.XPATH, ".//div[2]/span/a[1]")
                job_data['company_name'] = company_link.text.strip()
            except:
                # Try alternative locations
                try:
                    company_link = card_element.find_element(By.XPATH, ".//div[1]/span/a[1]")
                    job_data['company_name'] = company_link.text.strip()
                except:
                    try:
                        # Try getting from span text
                        company_span = card_element.find_element(By.XPATH, ".//div[1]/span")
                        company_text = company_span.text.strip()
                        lines = [line.strip() for line in company_text.split('\n') if line.strip()]
                        if lines:
                            job_data['company_name'] = lines[0]
                    except:
                        pass
            
            # Row 2: Rating and reviews
            try:
                rating_element = card_element.find_element(By.XPATH, ".//div[2]/span/a[2]/span[2]")
                job_data['rating'] = rating_element.text.strip()
            except:
                # Try alternative paths
                try:
                    rating_element = card_element.find_element(By.XPATH, ".//span[contains(@class, 'rating') or contains(text(), '.')]")
                    job_data['rating'] = rating_element.text.strip()
                except:
                    pass
            
            try:
                reviews_element = card_element.find_element(By.XPATH, ".//div[2]/span/a[3]")
                job_data['reviews'] = reviews_element.text.strip()
            except:
                pass
            
            # Row 3: Experience, Salary, Location
            try:
                exp_element = card_element.find_element(By.XPATH, ".//div[3]/div/span[1]/span/span")
                job_data['experience'] = exp_element.text.strip()
            except:
                # Try alternative
                try:
                    exp_element = card_element.find_element(By.XPATH, ".//span[contains(text(), 'Yrs') or contains(text(), 'Experience')]")
                    job_data['experience'] = exp_element.text.strip()
                except:
                    pass
            
            try:
                salary_element = card_element.find_element(By.XPATH, ".//div[3]/div/span[2]/span/span")
                job_data['salary'] = salary_element.text.strip()
            except:
                # Try alternative
                try:
                    salary_element = card_element.find_element(By.XPATH, ".//span[contains(text(), 'Lakhs') or contains(text(), 'LPA')]")
                    job_data['salary'] = salary_element.text.strip()
                except:
                    pass
            
            try:
                loc_element = card_element.find_element(By.XPATH, ".//div[3]/div/span[3]/span/span")
                job_data['location'] = loc_element.text.strip()
            except:
                # Try alternative
                try:
                    loc_element = card_element.find_element(By.XPATH, ".//span[contains(@class, 'loc') or contains(text(), 'Location')]")
                    job_data['location'] = loc_element.text.strip()
                except:
                    pass
            
            # Row 4: Job description
            try:
                desc_element = card_element.find_element(By.XPATH, ".//div[4]/span")
                job_data['job_description'] = desc_element.text.strip()
            except:
                # Try alternative
                try:
                    desc_element = card_element.find_element(By.XPATH, ".//span[contains(@class, 'desc') or contains(@class, 'job-desc')]")
                    job_data['job_description'] = desc_element.text.strip()
                except:
                    pass
            
            # Row 5: Tags
            try:
                tags_list = card_element.find_element(By.XPATH, ".//div[5]/ul")
                tag_items = tags_list.find_elements(By.TAG_NAME, "li")
                job_data['tags'] = [tag.text.strip() for tag in tag_items if tag.text.strip()]
            except:
                # Try alternative
                try:
                    tags_list = card_element.find_element(By.XPATH, ".//ul")
                    tag_items = tags_list.find_elements(By.TAG_NAME, "li")
                    job_data['tags'] = [tag.text.strip() for tag in tag_items if tag.text.strip()][:5]  # Limit to 5 tags
                except:
                    pass
            
            # Row 6: Job post date
            try:
                date_element = card_element.find_element(By.XPATH, ".//div[6]/span[1]")
                job_data['job_post_date'] = date_element.text.strip()
            except:
                # Try alternative
                try:
                    date_element = card_element.find_element(By.XPATH, ".//span[contains(text(), 'ago') or contains(text(), 'Posted')]")
                    job_data['job_post_date'] = date_element.text.strip()
                except:
                    pass
            
        except Exception as e:
            print(f"Error extracting job data for card {card_index}: {e}")
        
        return job_data
    
    def scrape_job_details(self, job_url):
        """
        Scrape detailed job information from a Naukri.com job detail page
        
        Args:
            job_url: URL of the job detail page
        
        Returns:
            Dictionary with all job detail fields
        """
        job_details = {
            'header_title': '',
            'company_title': '',
            'company_logo': '',
            'rating': '',
            'reviews': '',
            'experience': '',
            'salary': '',
            'location': '',
            'posted': '',
            'openings': '',
            'applicants': '',
            'apply_button_text': '',
            'internship_label': '',
            'job_highlights': {'title': '', 'items': []},
            'job_match_score': '',
            'job_description_header': '',
            'job_description_content': '',
            'job_description_div': '',
            'role_and_responsibilities': {'title': '', 'items': []},
            'role': '',
            'industry_type': '',
            'department': '',
            'employment_type': '',
            'role_category': '',
            'education_title': '',
            'ug_education': '',
            'pg_education': '',
            'key_skills': [],
            'about_company_header': '',
            'about_company_description': '',
            'company_info_header': '',
            'company_address': {'label': '', 'address': ''}
        }
        
        try:
            print(f"[SCRAPER] Scraping job details from: {job_url}")
            self.driver.get(job_url)
            
            # Wait for page to be interactive
            try:
                WebDriverWait(self.driver, 10).until(
                    lambda driver: driver.execute_script('return document.readyState') == 'complete'
                )
                print("[SCRAPER] Page loaded (document.readyState = complete)")
            except:
                print("[SCRAPER] Warning: Page readyState check timeout")
            
            time.sleep(5)  # Additional wait for dynamic content
            
            # Check page title for debugging
            try:
                page_title = self.driver.title
                print(f"[SCRAPER] Page title: {page_title}")
                current_url = self.driver.current_url
                print(f"[SCRAPER] Current URL: {current_url}")
            except:
                pass
            
            # Handle popups
            try:
                popup_selectors = [
                    "//button[contains(text(), 'Close')]",
                    "//button[contains(text(), 'Skip')]",
                    "//span[contains(@class, 'close')]",
                    "//div[contains(@class, 'closeIcon')]"
                ]
                for selector in popup_selectors:
                    try:
                        popup = self.driver.find_element(By.XPATH, selector)
                        if popup and popup.is_displayed():
                            popup.click()
                            time.sleep(1)
                            break
                    except:
                        continue
            except:
                pass
            
            # Wait for main content to load - try multiple XPath options
            content_found = False
            content_xpaths = [
                "/html/body/div[1]/div/main/div[1]/div[1]/section[1]",
                "//section[contains(@class, 'job')]",
                "//main//section[1]",
                "//h1",  # Just wait for header title
            ]
            
            for xpath in content_xpaths:
                try:
                    self.wait.until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    content_found = True
                    print(f"[SCRAPER] Found content using XPath: {xpath}")
                    break
                except:
                    continue
            
            if not content_found:
                print("[SCRAPER] Warning: Main content section not found, but continuing with extraction...")
                time.sleep(3)  # Extra wait in case content is still loading
                # Debug: Check page source snippet
                try:
                    page_source_preview = self.driver.page_source[:1000]
                    print(f"[SCRAPER] Page source preview (first 1000 chars): {page_source_preview}")
                except:
                    pass
            
            # Debug: Try to find any h1 on the page
            try:
                all_h1s = self.driver.find_elements(By.XPATH, "//h1")
                print(f"[SCRAPER] Found {len(all_h1s)} h1 elements on page")
                for i, h1 in enumerate(all_h1s[:3]):  # Show first 3
                    try:
                        print(f"[SCRAPER] H1 #{i+1}: {h1.text.strip()[:100]}")
                    except:
                        pass
            except:
                pass
            
            # Extract header title - try multiple XPaths
            try:
                header_title = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[1]/div[1]/div[1]/header/h1")
                job_details['header_title'] = header_title.text.strip()
            except:
                try:
                    # Try alternative: just find h1 in main
                    header_title = self.driver.find_element(By.XPATH, "//main//h1")
                    job_details['header_title'] = header_title.text.strip()
                    print(f"[SCRAPER] Found header title using alternative XPath")
                except:
                    try:
                        header_title = self.driver.find_element(By.XPATH, "//h1")
                        job_details['header_title'] = header_title.text.strip()
                        print(f"[SCRAPER] Found header title using simple h1")
                    except:
                        print("[SCRAPER] Could not find header title with XPath, trying BeautifulSoup...")
                        # Try using BeautifulSoup as fallback
                        try:
                            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                            h1_tag = soup.find('h1')
                            if h1_tag:
                                job_details['header_title'] = h1_tag.get_text(strip=True)
                                print(f"[SCRAPER] Found header title using BeautifulSoup: {job_details['header_title'][:80]}")
                        except Exception as bs_error:
                            print(f"[SCRAPER] BeautifulSoup fallback failed: {bs_error}")
                        pass
            
            # Extract company title - try multiple XPaths
            try:
                company_title = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[1]/div[1]/div[1]/div/a")
                job_details['company_title'] = company_title.text.strip()
            except:
                try:
                    company_title = self.driver.find_element(By.XPATH, "//section[1]//a[contains(@href, 'company')]")
                    job_details['company_title'] = company_title.text.strip()
                except:
                    pass
            
            # Extract company logo - try multiple XPaths
            try:
                company_logo = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[1]/div[1]/a/img")
                job_details['company_logo'] = company_logo.get_attribute('src') or ''
            except:
                try:
                    company_logo = self.driver.find_element(By.XPATH, "//section[1]//img[contains(@alt, 'company') or contains(@src, 'logo')]")
                    job_details['company_logo'] = company_logo.get_attribute('src') or ''
                except:
                    pass
            
            # Extract rating
            try:
                rating = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[1]/div[1]/div[1]/div/div/a/span[1]")
                job_details['rating'] = rating.text.strip()
            except:
                pass
            
            # Extract reviews
            try:
                reviews = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[1]/div[1]/div[1]/div/div/a/span[2]")
                job_details['reviews'] = reviews.text.strip()
            except:
                pass
            
            # Extract experience
            try:
                experience = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[1]/div[1]/div[2]/div[1]/div[1]/span")
                job_details['experience'] = experience.text.strip()
            except:
                pass
            
            # Extract salary
            try:
                salary = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[1]/div[1]/div[2]/div[1]/div[2]/span")
                job_details['salary'] = salary.text.strip()
            except:
                pass
            
            # Extract location
            try:
                location = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[1]/div[1]/div[2]/div[2]/span")
                job_details['location'] = location.text.strip()
            except:
                pass
            
            # Extract posted date
            try:
                posted = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[1]/div[2]/div[1]/span[1]/span")
                job_details['posted'] = posted.text.strip()
            except:
                pass
            
            # Extract openings
            try:
                openings = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[1]/div[2]/div[1]/span[2]/span")
                job_details['openings'] = openings.text.strip()
            except:
                pass
            
            # Extract applicants
            try:
                applicants = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[1]/div[2]/div[1]/span[3]/span")
                job_details['applicants'] = applicants.text.strip()
            except:
                pass
            
            # Extract apply button text
            try:
                apply_button = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[1]/div[2]/div[2]/button[2]")
                job_details['apply_button_text'] = apply_button.text.strip()
            except:
                pass
            
            # Extract internship label
            try:
                internship_label = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[1]/div[1]/div[2]/div[4]/p")
                job_details['internship_label'] = internship_label.text.strip()
            except:
                pass
            
            # Extract job highlights
            try:
                highlights_title = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[2]/div[1]/div[1]/span")
                job_details['job_highlights']['title'] = highlights_title.text.strip()
            except:
                pass
            
            try:
                highlights_list = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[2]/div[1]/div[1]/ul")
                highlight_items = highlights_list.find_elements(By.XPATH, "./li")
                job_details['job_highlights']['items'] = [item.text.strip() for item in highlight_items if item.text.strip()]
            except:
                try:
                    # Try finding all li elements directly
                    highlight_items = self.driver.find_elements(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[2]/div[1]/div[1]/ul/li")
                    job_details['job_highlights']['items'] = [item.text.strip() for item in highlight_items if item.text.strip()]
                except:
                    pass
            
            # Extract job match score
            try:
                match_score = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[2]/div[1]/div[2]/span")
                job_details['job_match_score'] = match_score.text.strip()
            except:
                pass
            
            # Extract job description header
            try:
                job_desc_header = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[2]/div[2]/h2")
                job_details['job_description_header'] = job_desc_header.text.strip()
            except:
                pass
            
            # Extract job description div (alternative location)
            try:
                job_desc_div = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[2]/div[2]")
                job_details['job_description_div'] = job_desc_div.text.strip()
            except:
                pass
            
            # Extract job description content - combine multiple divs
            job_desc_parts = []
            desc_div_xpaths = [
                "/html/body/div[1]/div/main/div[1]/div[1]/section[2]/div[3]/div[1]/div[2]",
                "/html/body/div[1]/div/main/div[1]/div[1]/section[2]/div[3]/div[1]/div[3]",
                "/html/body/div[1]/div/main/div[1]/div[1]/section[2]/div[3]/div[1]/div[4]"
            ]
            
            for xpath in desc_div_xpaths:
                try:
                    desc_div = self.driver.find_element(By.XPATH, xpath)
                    text = desc_div.text.strip()
                    if text:
                        job_desc_parts.append(text)
                except:
                    pass
            
            if job_desc_parts:
                job_details['job_description_content'] = "\n\n".join(job_desc_parts)
                print(f"[SCRAPER] Job description combined from {len(job_desc_parts)} divs")
            else:
                # Fallback to old method
                try:
                    job_desc_content = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[2]/div[3]/div[1]")
                    job_details['job_description_content'] = job_desc_content.text.strip()
                except:
                    try:
                        # Try alternative structure
                        job_desc_content = self.driver.find_element(By.XPATH, "//section[2]//div[contains(@class, 'job-description') or contains(@class, 'description')]")
                        job_details['job_description_content'] = job_desc_content.text.strip()
                    except:
                        pass
            
            # Extract role and responsibilities
            try:
                role_resp_title = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[2]/div[3]/div[1]/p/strong")
                job_details['role_and_responsibilities']['title'] = role_resp_title.text.strip()
            except:
                pass
            
            try:
                role_resp_list = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[2]/div[3]/div[1]/ul")
                role_resp_items = role_resp_list.find_elements(By.XPATH, "./li")
                job_details['role_and_responsibilities']['items'] = [item.text.strip() for item in role_resp_items if item.text.strip()]
            except:
                try:
                    # Try finding all li elements directly
                    role_resp_items = self.driver.find_elements(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[2]/div[3]/div[1]/ul/li")
                    job_details['role_and_responsibilities']['items'] = [item.text.strip() for item in role_resp_items if item.text.strip()]
                except:
                    pass
            
            # Extract additional role and responsibilities div content
            try:
                role_resp_div = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[2]/div[3]/div[2]")
                # Extract all div content within
                div_content = role_resp_div.text.strip()
                if div_content:
                    # Split by lines and filter empty
                    lines = [line.strip() for line in div_content.split('\n') if line.strip()]
                    # Add to items if not already included
                    existing_items = set(job_details['role_and_responsibilities']['items'])
                    for line in lines:
                        if line and line not in existing_items:
                            job_details['role_and_responsibilities']['items'].append(line)
            except:
                pass
            
            # Extract role
            try:
                role = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[2]/div[3]/div[2]/div[1]/span")
                job_details['role'] = role.text.strip()
            except:
                pass
            
            # Extract industry type
            try:
                industry_type = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[2]/div[3]/div[2]/div[2]/span/a")
                job_details['industry_type'] = industry_type.text.strip()
            except:
                pass
            
            # Extract department
            try:
                department = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[2]/div[3]/div[2]/div[3]/span")
                job_details['department'] = department.text.strip()
            except:
                pass
            
            # Extract employment type
            try:
                employment_type = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[2]/div[3]/div[2]/div[4]/span/span")
                job_details['employment_type'] = employment_type.text.strip()
            except:
                pass
            
            # Extract role category
            try:
                role_category = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[2]/div[3]/div[2]/div[5]/span/span")
                job_details['role_category'] = role_category.text.strip()
            except:
                pass
            
            # Extract education title
            try:
                education_title = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[2]/div[3]/div[3]/div[1]")
                job_details['education_title'] = education_title.text.strip()
            except:
                pass
            
            # Extract UG education - try new wrapper div first
            try:
                # Try new wrapper div location
                ug_wrapper = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[2]/div[3]/div[3]/div[2]")
                job_details['ug_education'] = ug_wrapper.text.strip()
            except:
                try:
                    # Fallback to old XPath
                    ug_education = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[2]/div[3]/div[3]/div[2]/span")
                    job_details['ug_education'] = ug_education.text.strip()
                except:
                    pass
            
            # Extract PG education - try new wrapper div first
            try:
                # Try new wrapper div location (if PG is in div[3])
                pg_wrapper = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[2]/div[3]/div[3]/div[3]")
                job_details['pg_education'] = pg_wrapper.text.strip()
            except:
                try:
                    # Fallback to old XPath
                    pg_education = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[2]/div[3]/div[3]/div[3]/span")
                    job_details['pg_education'] = pg_education.text.strip()
                except:
                    pass
            
            # Also try extracting from div[2] structure (label and span)
            try:
                edu_label = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[2]/div[3]/div[2]/div[2]/label")
                edu_span = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[2]/div[3]/div[2]/div[2]/span")
                if edu_label.text.strip() and 'ug' in edu_label.text.strip().lower():
                    job_details['ug_education'] = edu_span.text.strip()
            except:
                pass
            
            # Extract key skills (can be multiple) - try new location first
            try:
                # Try new XPath location first
                skill_elements = self.driver.find_elements(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[2]/div[4]/div[3]/a/span")
                if not skill_elements:
                    # Try old XPath location
                    skill_elements = self.driver.find_elements(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[2]/div[4]/div[2]/a/span")
                if not skill_elements:
                    # Try alternative: find all spans within the key skills section
                    skill_elements = self.driver.find_elements(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[2]/div[4]/div[2]//a/span")
                if not skill_elements:
                    # Try alternative in div[3]
                    skill_elements = self.driver.find_elements(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[2]/div[4]/div[3]//a/span")
                
                job_details['key_skills'] = [skill.text.strip() for skill in skill_elements if skill.text.strip()]
                print(f"[SCRAPER] Found {len(job_details['key_skills'])} key skills")
            except Exception as e:
                print(f"[SCRAPER] Error extracting key skills: {e}")
                pass
            
            # Extract about company header
            try:
                about_header = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[3]/header/h2")
                job_details['about_company_header'] = about_header.text.strip()
            except:
                pass
            
            # Extract company info header
            try:
                company_info_header = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[3]/div[2]")
                job_details['company_info_header'] = company_info_header.text.strip()
            except:
                pass
            
            # Extract company address
            try:
                address_label = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[3]/div[3]/label")
                job_details['company_address']['label'] = address_label.text.strip()
            except:
                pass
            
            try:
                address_span = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[3]/div[3]/span")
                job_details['company_address']['address'] = address_span.text.strip()
            except:
                pass
            
            # Extract about company description
            try:
                # XPath with /text() won't work with Selenium, use the div and get text
                about_desc = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[3]/div")
                job_details['about_company_description'] = about_desc.text.strip()
            except:
                try:
                    # Try alternative: get direct text content if available
                    about_desc = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/section[3]/div")
                    # Try to get text using JavaScript if Selenium's text property is empty
                    script = "return arguments[0].innerText || arguments[0].textContent || '';"
                    text_content = self.driver.execute_script(script, about_desc)
                    job_details['about_company_description'] = text_content.strip() if text_content else ''
                except:
                    pass
            
            # Debug: Print summary of scraped fields
            def has_value(v):
                """Check if a value has actual content"""
                if isinstance(v, dict):
                    return any(has_value(val) for val in v.values())
                elif isinstance(v, list):
                    return len(v) > 0
                elif isinstance(v, str):
                    return bool(v.strip())
                return bool(v)
            
            non_empty_fields = {k: v for k, v in job_details.items() if has_value(v)}
            empty_fields = [k for k, v in job_details.items() if not has_value(v)]
            
            print(f"\n[SCRAPER] === Job Details Scraping Summary ===")
            print(f"[SCRAPER] Successfully scraped: {len(non_empty_fields)}/{len(job_details)} fields")
            print(f"[SCRAPER] Fields found: {', '.join(non_empty_fields.keys())}")
            if empty_fields:
                print(f"[SCRAPER] Fields not found ({len(empty_fields)}): {', '.join(empty_fields[:10])}")
                if len(empty_fields) > 10:
                    print(f"[SCRAPER] ... and {len(empty_fields) - 10} more")
            
            # Show structured fields detail
            structured_fields = ['job_highlights', 'role_and_responsibilities', 'company_address']
            for field in structured_fields:
                value = job_details.get(field, {})
                if isinstance(value, dict) and has_value(value):
                    if field == 'job_highlights':
                        items_count = len(value.get('items', []))
                        print(f"[SCRAPER] {field}: title='{value.get('title', '')[:50]}', {items_count} items")
                    elif field == 'role_and_responsibilities':
                        items_count = len(value.get('items', []))
                        print(f"[SCRAPER] {field}: title='{value.get('title', '')[:50]}', {items_count} items")
                    elif field == 'company_address':
                        print(f"[SCRAPER] {field}: label='{value.get('label', '')[:30]}', address='{value.get('address', '')[:50]}'")
            
            title_found = job_details.get('header_title', '').strip()
            if title_found:
                print(f"[SCRAPER] Job Title: {title_found}")
            else:
                print(f"[SCRAPER] WARNING: No job title found!")
                # Print page title as debug
                try:
                    page_title = self.driver.title
                    print(f"[SCRAPER] Page title: {page_title}")
                except:
                    pass
            print(f"[SCRAPER] ======================================\n")
            
        except Exception as e:
            print(f"[SCRAPER] Error scraping job details: {e}")
            import traceback
            traceback.print_exc()
        
        return job_details
    
    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()

