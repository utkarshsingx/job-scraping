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
    
    def scrape_jobs(self, job_type, keyword, location, experience=None, max_jobs=20):
        """
        Scrape jobs from Naukri.com
        
        Args:
            job_type: 'job' or 'internship'
            keyword: Job search keyword
            location: Job location
            experience: Years of experience (optional)
            max_jobs: Maximum number of jobs to scrape
        
        Returns:
            List of job dictionaries
        """
        url = self.build_url(job_type, keyword, location, experience)
        print(f"Scraping URL: {url}")
        
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
                print("Job cards container not found")
                return []
            
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
            
            # If scraping returned no jobs, try API fallback
            if len(jobs) == 0:
                print("No jobs found via scraping, trying API fallback...")
                api_jobs = self.scrape_jobs_via_api(job_type, keyword, location, experience, max_jobs)
                if api_jobs and len(api_jobs) > 0:
                    print(f"API fallback returned {len(api_jobs)} jobs")
                    return api_jobs
            
            return jobs
            
        except Exception as e:
            print(f"Error scraping jobs: {e}")
            import traceback
            traceback.print_exc()
            # Try API as fallback even on error
            try:
                print("Trying API fallback after scraping error...")
                api_jobs = self.scrape_jobs_via_api(job_type, keyword, location, experience, max_jobs)
                if api_jobs:
                    return api_jobs
            except:
                pass
            return []
    
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
    
    def scrape_jobs_via_api(self, job_type, keyword, location, experience=None, max_jobs=20):
        """
        Scrape jobs using Naukri.com API endpoint (fallback method)
        Uses cookies from Selenium session if available
        
        Args:
            job_type: 'job' or 'internship'
            keyword: Job search keyword
            location: Job location
            experience: Years of experience (optional)
            max_jobs: Maximum number of jobs to scrape
        
        Returns:
            List of job dictionaries
        """
        try:
            api_url = self.build_api_url(job_type, keyword, location, experience)
            print(f"Trying API URL: {api_url}")
            
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
            
            if response.status_code == 200:
                data = response.json()
                no_of_jobs = data.get('noOfJobs', 0)
                print(f"API Response received: noOfJobs={no_of_jobs}")
                
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
                        print(f"API returned {len(jobs)} jobs")
                        return jobs
                
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
                                        return jobs
                
                print("API returned no job data")
                return []
            else:
                print(f"API request failed with status {response.status_code}: {response.text[:200]}")
                return []
                
        except Exception as e:
            print(f"Error in API scraping: {e}")
            import traceback
            traceback.print_exc()
            return []
    
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
                    'job_post_date': ''
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
            'job_post_date': ''
        }
        
        try:
            # Row 1: Job title, company name, company logo
            try:
                title_element = card_element.find_element(By.XPATH, ".//div[1]/h2")
                job_data['job_title'] = title_element.text.strip()
            except:
                # Try alternative
                try:
                    title_element = card_element.find_element(By.XPATH, ".//h2")
                    job_data['job_title'] = title_element.text.strip()
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
                # Try to get company name from various possible locations
                company_span = card_element.find_element(By.XPATH, ".//div[1]/span")
                company_text = company_span.text.strip()
                # Get text but exclude image alt text
                # The company name is usually the first text in the span
                lines = [line.strip() for line in company_text.split('\n') if line.strip()]
                if lines:
                    job_data['company_name'] = lines[0]
            except:
                # Try alternative: look for anchor tags or divs with company name
                try:
                    company_link = card_element.find_element(By.XPATH, ".//div[1]/span/a[1]")
                    job_data['company_name'] = company_link.text.strip()
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
    
    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()

