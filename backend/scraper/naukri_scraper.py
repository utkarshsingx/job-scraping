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
        
        # Build base URL
        url_type = 'jobs' if job_type.lower() == 'job' else 'internships'
        base_url = f"https://www.naukri.com/{keyword_formatted}-{url_type}-in-{location_formatted}"
        
        # Add query parameters
        params = {
            'k': keyword,
            'l': location
        }
        
        if experience:
            params['experience'] = experience
        
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
            time.sleep(5)  # Wait for page to load
            
            # Handle popups or modals if they appear
            try:
                popup = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Close') or contains(text(), 'Skip') or contains(@class, 'close')]")
                if popup:
                    popup.click()
                    time.sleep(1)
            except:
                pass  # No popup found
            
            # Wait for job cards container to load - try multiple XPath variations
            container_xpaths = [
                "/html/body/div[1]/div/main/div[1]/div[2]/div[2]/div/div[1]",
                "//div[contains(@class, 'srp-jobtuple-wrapper')]",
                "//div[contains(@class, 'jobTuple')]"
            ]
            
            container_found = False
            for xpath in container_xpaths:
                try:
                    self.wait.until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    container_found = True
                    break
                except:
                    continue
            
            if not container_found:
                print("Job cards container not found")
                return []
            
            # Scroll to load more content
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
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
            
            return jobs
            
        except Exception as e:
            print(f"Error scraping jobs: {e}")
            import traceback
            traceback.print_exc()
            return []
    
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

