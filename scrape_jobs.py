#!/usr/bin/env python3
"""
Standalone Naukri.com Job Scraper

This script scrapes job listings from Naukri.com based on search criteria
and saves the results to a JSON file.

Usage:
    python scrape_jobs.py --job-type job --designation "software engineer" --location "bangalore" --experience 2
    
    python scrape_jobs.py -t internship -d "data science" -l "mumbai" -e 0
    
    python scrape_jobs.py --job-type job --designation "python developer" --location "delhi" --output my_jobs.json

Arguments:
    --job-type, -t:     Type of job ('job' or 'internship') [required]
    --designation, -d:   Job keyword/designation [required]
    --location, -l:      City or state [required]
    --experience, -e:    Years of experience (optional)
    --output, -o:        Output JSON filename (optional, default: jobs_<timestamp>.json)
    --headless:          Run browser in headless mode (default: True)
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
import argparse
import sys
from datetime import datetime


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
                except Exception as e:
                    pass
            
            # Install ChromeDriver
            initial_path = ChromeDriverManager().install()
            
            # ChromeDriverManager sometimes returns wrong file (like THIRD_PARTY_NOTICES.chromedriver)
            # Always search for the actual chromedriver executable
            driver_dir = os.path.dirname(initial_path)
            driver_path = None
            
            # Helper function to check if a path is the actual chromedriver executable
            def is_valid_chromedriver(path):
                if not os.path.exists(path):
                    return False
                # Check if it's a text file (wrong file)
                if 'THIRD_PARTY' in path or 'LICENSE' in path or 'NOTICES' in path:
                    return False
                # Check file size (chromedriver is > 10MB, text files are < 1MB)
                try:
                    size = os.path.getsize(path)
                    if size < 1000000:  # Less than 1MB is likely not the executable
                        return False
                    # Check if it's actually a binary file (not a text file)
                    with open(path, 'rb') as f:
                        first_bytes = f.read(4)
                        # Text files start with readable ASCII, binaries don't
                        if first_bytes.startswith(b'#!/') or first_bytes.startswith(b'# '):
                            # Could be a shell script, check more
                            if b'THIRD_PARTY' in f.read(100):
                                return False
                    return os.path.isfile(path)
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
                    # Search in subdirectories (common on macOS ARM64)
                    if os.path.exists(driver_dir):
                        # Check immediate subdirectories first
                        for item in os.listdir(driver_dir):
                            item_path = os.path.join(driver_dir, item)
                            if os.path.isdir(item_path):
                                # Check for chromedriver in this subdirectory
                                chromedriver_path = os.path.join(item_path, 'chromedriver')
                                if is_valid_chromedriver(chromedriver_path):
                                    driver_path = chromedriver_path
                                    break
                                # Also check nested subdirectories (macOS ARM64 structure)
                                for subitem in os.listdir(item_path):
                                    subitem_path = os.path.join(item_path, subitem)
                                    if os.path.isdir(subitem_path):
                                        nested_chromedriver = os.path.join(subitem_path, 'chromedriver')
                                        if is_valid_chromedriver(nested_chromedriver):
                                            driver_path = nested_chromedriver
                                            break
                                    elif subitem == 'chromedriver':
                                        if is_valid_chromedriver(subitem_path):
                                            driver_path = subitem_path
                                            break
                                if driver_path:
                                    break
                    
                    # If still not found, do recursive search
                    if not driver_path and os.path.exists(driver_cache_path):
                        def find_chromedriver_recursive(directory):
                            for root, dirs, files in os.walk(directory):
                                for file in files:
                                    if file == 'chromedriver' and 'THIRD_PARTY' not in root and 'LICENSE' not in root:
                                        full_path = os.path.join(root, file)
                                        if is_valid_chromedriver(full_path):
                                            return full_path
                            return None
                        
                        driver_path = find_chromedriver_recursive(driver_cache_path)
            
            if not driver_path:
                raise Exception(f"Could not find valid chromedriver executable. Searched in: {driver_dir}")
            
            # Verify the driver path exists and make it executable if needed
            if not os.path.exists(driver_path):
                raise Exception(f"ChromeDriver not found at {driver_path}")
            
            # Ensure it's executable
            if not os.access(driver_path, os.X_OK):
                try:
                    os.chmod(driver_path, 0o755)
                except Exception as e:
                    pass
            
            # Add additional Chrome options to help with connection issues
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--remote-debugging-port=9222')
            
            service = Service(driver_path)
            try:
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as chrome_error:
                # If connection fails, try with additional options
                if 'unable to connect to renderer' in str(chrome_error).lower():
                    chrome_options.add_argument('--disable-software-rasterizer')
                    chrome_options.add_argument('--disable-extensions')
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                else:
                    raise
            self.driver.set_page_load_timeout(30)  # 30 second timeout
            self.wait = WebDriverWait(self.driver, 20)
            
        except Exception as e:
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
                metadata['debug_info']['scraping_errors'].append(error_msg)
                # Try API fallback
                api_jobs, api_metadata = self.scrape_jobs_via_api(job_type, keyword, location, experience, max_jobs)
                if api_jobs and len(api_jobs) > 0:
                    metadata['source'] = 'api_fallback'
                    metadata['debug_info']['api_fallback_used'] = True
                    metadata['debug_info'].update(api_metadata.get('debug_info', {}))
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
                return jobs, metadata
            
            # If scraping returned no jobs, try API fallback
            metadata['debug_info']['scraping_errors'].append("No jobs found in scraping results")
            api_jobs, api_metadata = self.scrape_jobs_via_api(job_type, keyword, location, experience, max_jobs, page)
            if api_jobs and len(api_jobs) > 0:
                metadata['source'] = 'api_fallback'
                metadata['debug_info']['api_fallback_used'] = True
                metadata['debug_info'].update(api_metadata.get('debug_info', {}))
                return api_jobs, metadata
            return jobs, metadata
            
        except Exception as e:
            error_msg = f"Error scraping jobs: {str(e)}"
            import traceback
            traceback.print_exc()
            metadata['debug_info']['scraping_errors'].append(error_msg)
            
            # Try API as fallback even on error
            try:
                api_jobs, api_metadata = self.scrape_jobs_via_api(job_type, keyword, location, experience, max_jobs, page)
                if api_jobs and len(api_jobs) > 0:
                    metadata['source'] = 'api_fallback'
                    metadata['debug_info']['api_fallback_used'] = True
                    metadata['debug_info'].update(api_metadata.get('debug_info', {}))
                    return api_jobs, metadata
            except Exception as api_error:
                api_error_msg = f"API fallback also failed: {str(api_error)}"
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
            
            if response.status_code == 200:
                data = response.json()
                no_of_jobs = data.get('noOfJobs', 0)
                metadata['debug_info']['api_response_jobs_count'] = no_of_jobs
                metadata['debug_info']['total_jobs_available'] = no_of_jobs
                
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
                        return jobs, metadata
                
                # If noOfJobs > 0 but no job data found, try parsing the entire response
                if no_of_jobs > 0:
                    # Try to extract from any array in the response
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if isinstance(value, list) and len(value) > 0:
                                # Check if first item looks like job data
                                if isinstance(value[0], dict) and ('title' in value[0] or 'jobTitle' in value[0]):
                                    jobs = self._parse_api_job_data(value, max_jobs)
                                    if jobs:
                                        metadata['debug_info']['api_success'] = True
                                        return jobs, metadata
                
                return [], metadata
            else:
                error_msg = f"API request failed with status {response.status_code}"
                metadata['debug_info']['api_errors'] = [error_msg]
                return [], metadata
                
        except Exception as e:
            error_msg = f"Error in API scraping: {str(e)}"
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
                pass
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
            pass
        
        return job_data
    
    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Scrape job listings from Naukri.com',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scrape_jobs.py --job-type job --designation "software engineer" --location "bangalore" --experience 2
  python scrape_jobs.py -t internship -d "data science" -l "mumbai" -e 0
  python scrape_jobs.py --job-type job --designation "python developer" --location "delhi" --output my_jobs.json
        """
    )
    
    parser.add_argument(
        '--job-type', '-t',
        required=True,
        choices=['job', 'internship'],
        help='Type of job: "job" or "internship"'
    )
    
    parser.add_argument(
        '--designation', '-d',
        required=True,
        help='Job keyword/designation (e.g., "software engineer", "data scientist")'
    )
    
    parser.add_argument(
        '--location', '-l',
        required=True,
        help='City or state (e.g., "bangalore", "mumbai", "delhi")'
    )
    
    parser.add_argument(
        '--experience', '-e',
        type=int,
        default=None,
        help='Years of experience (optional integer, e.g., 2)'
    )
    
    parser.add_argument(
        '--output', '-o',
        default=None,
        help='Output JSON filename (default: jobs_<timestamp>.json)'
    )
    
    parser.add_argument(
        '--headless',
        action='store_true',
        default=True,
        help='Run browser in headless mode (default: True)'
    )
    
    parser.add_argument(
        '--no-headless',
        action='store_false',
        dest='headless',
        help='Run browser in visible mode (overrides --headless)'
    )
    
    return parser.parse_args()


def main():
    """Main execution function"""
    args = parse_arguments()
    
    # Generate output filename if not provided
    if args.output:
        output_file = args.output
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"jobs_{timestamp}.json"
    
    scraper = None
    
    try:
        # Print progress messages
        print("=" * 60)
        print("Naukri.com Job Scraper")
        print("=" * 60)
        print(f"Job Type: {args.job_type}")
        print(f"Designation: {args.designation}")
        print(f"Location: {args.location}")
        if args.experience is not None:
            print(f"Experience: {args.experience} years")
        print(f"Output File: {output_file}")
        print(f"Headless Mode: {args.headless}")
        print("=" * 60)
        print()
        
        # Initialize scraper
        print("Initializing scraper...")
        scraper = NaukriScraper(headless=args.headless)
        print("✓ Scraper initialized successfully")
        print()
        
        # Scrape jobs
        print("Scraping jobs...")
        jobs, metadata = scraper.scrape_jobs(
            job_type=args.job_type,
            keyword=args.designation,
            location=args.location,
            experience=args.experience,
            max_jobs=100,
            page=1
        )
        print(f"✓ Scraping completed")
        print()
        
        # Prepare output data
        output_data = {
            'search_params': {
                'job_type': args.job_type,
                'designation': args.designation,
                'location': args.location,
                'experience': args.experience
            },
            'results': {
                'count': len(jobs),
                'jobs': jobs,
                'metadata': metadata
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # Save to JSON file
        print(f"Saving results to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"✓ Results saved successfully")
        print()
        
        # Print summary
        print("=" * 60)
        print("Summary")
        print("=" * 60)
        print(f"Jobs found: {len(jobs)}")
        print(f"Data source: {metadata.get('source', 'unknown')}")
        print(f"Output file: {output_file}")
        print("=" * 60)
        
        # Exit with success
        sys.exit(0)
        
    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Always close scraper
        if scraper:
            try:
                print("\nCleaning up...")
                scraper.close()
                print("✓ Cleanup completed")
            except:
                pass


if __name__ == '__main__':
    main()

