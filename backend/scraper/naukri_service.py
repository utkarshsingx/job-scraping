"""
Standalone service module for Naukri.com scraping operations.

This module provides a reusable function that can be called directly
without requiring HTTP requests, making it suitable for use in workers,
scripts, or other APIs.
"""
from typing import Dict, Any, Optional
from .naukri_scraper import NaukriScraper


def get_naukri_data(
    task_type: str,
    job_type: Optional[str] = None,
    keyword: Optional[str] = None,
    location: Optional[str] = None,
    experience: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
    job_url: Optional[str] = None,
    headless: bool = True
) -> Dict[str, Any]:
    """
    Main function to get Naukri.com data (jobs or job details).
    
    This function abstracts all scraping logic, handling scraper initialization,
    execution, and cleanup. It can be called directly from any Python code.
    
    Args:
        task_type: 'search' or 'details' - determines which operation to perform
        job_type: 'job' or 'internship' (required for search task)
        keyword: Search keyword (required for search task)
        location: Search location (required for search task)
        experience: Years of experience (optional for search task)
        page: Page number for pagination (optional for search task, default: 1)
        page_size: Number of jobs per page (optional for search task, default: 20)
        job_url: URL of job detail page (required for details task)
        headless: Whether to run browser in headless mode (default: True)
    
    Returns:
        For 'search' task:
        {
            'success': bool,
            'count': int,
            'jobs': list[dict],
            'pagination': {
                'current_page': int,
                'page_size': int,
                'has_next': bool,
                'has_previous': bool,
                'total_pages': int | None,
                'total_jobs': int | None
            },
            'metadata': {
                'data_source': str,
                'debug_info': dict
            },
            'error': str | None,
            'message': str | None
        }
        
        For 'details' task:
        {
            'success': bool,
            'job_details': dict,
            'error': str | None,
            'message': str | None
        }
    """
    scraper = None
    
    try:
        # Validate task_type
        if task_type not in ['search', 'details']:
            return {
                'success': False,
                'error': 'Invalid task_type',
                'message': f"task_type must be 'search' or 'details', got '{task_type}'"
            }
        
        # Validate parameters based on task_type
        if task_type == 'search':
            if not job_type:
                return {
                    'success': False,
                    'error': 'Missing required parameter',
                    'message': 'job_type is required for search task'
                }
            if not keyword:
                return {
                    'success': False,
                    'error': 'Missing required parameter',
                    'message': 'keyword is required for search task'
                }
            if not location:
                return {
                    'success': False,
                    'error': 'Missing required parameter',
                    'message': 'location is required for search task'
                }
            if job_type not in ['job', 'internship']:
                return {
                    'success': False,
                    'error': 'Invalid job_type',
                    'message': "job_type must be 'job' or 'internship'"
                }
        elif task_type == 'details':
            if not job_url:
                return {
                    'success': False,
                    'error': 'Missing required parameter',
                    'message': 'job_url is required for details task'
                }
        
        # Initialize scraper
        scraper = NaukriScraper(headless=headless)
        
        # Execute appropriate operation
        if task_type == 'search':
            return _handle_search_task(
                scraper, job_type, keyword, location, experience, page, page_size
            )
        else:  # task_type == 'details'
            return _handle_details_task(scraper, job_url)
    
    except Exception as e:
        import traceback
        error_details = str(e)
        traceback.print_exc()
        
        return {
            'success': False,
            'error': f'An error occurred during {task_type} operation',
            'message': error_details
        }
    
    finally:
        # Always close the scraper
        if scraper:
            try:
                scraper.close()
            except:
                pass


def _handle_search_task(
    scraper: NaukriScraper,
    job_type: str,
    keyword: str,
    location: str,
    experience: Optional[int],
    page: int,
    page_size: int
) -> Dict[str, Any]:
    """
    Handle job search task.
    
    Args:
        scraper: Initialized NaukriScraper instance
        job_type: 'job' or 'internship'
        keyword: Search keyword
        location: Search location
        experience: Years of experience (optional)
        page: Page number
        page_size: Number of jobs per page
    
    Returns:
        Structured response dictionary
    """
    try:
        # Scrape jobs (returns tuple of (jobs, metadata))
        result = scraper.scrape_jobs(
            job_type=job_type,
            keyword=keyword,
            location=location,
            experience=experience,
            max_jobs=page_size,
            page=page
        )
        
        # Handle both old format (list) and new format (tuple)
        if isinstance(result, tuple) and len(result) == 2:
            jobs, metadata = result
        else:
            # Fallback for old format
            jobs = result if isinstance(result, list) else []
            metadata = {
                'source': 'unknown',
                'debug_info': {}
            }
        
        # Get total jobs available from API response if available
        debug_info = metadata.get('debug_info', {})
        total_jobs_available = debug_info.get('total_jobs_available', 0)
        current_count = len(jobs)
        
        # Calculate pagination info
        has_next_page = current_count >= page_size
        if total_jobs_available > 0:
            total_pages = (total_jobs_available + page_size - 1) // page_size
            has_next_page = page < total_pages
        elif current_count >= page_size:
            # If we got full page, assume there might be more
            has_next_page = True
            total_pages = None
        else:
            has_next_page = False
            total_pages = page
        
        # Return structured response
        return {
            'success': True,
            'count': current_count,
            'jobs': jobs,  # Return raw job dictionaries
            'pagination': {
                'current_page': page,
                'page_size': page_size,
                'has_next': has_next_page,
                'has_previous': page > 1,
                'total_pages': total_pages,
                'total_jobs': total_jobs_available if total_jobs_available > 0 else None
            },
            'metadata': {
                'data_source': metadata.get('source', 'unknown'),
                'debug_info': debug_info
            },
            'error': None,
            'message': None
        }
    
    except Exception as e:
        import traceback
        error_details = str(e)
        traceback.print_exc()
        
        return {
            'success': False,
            'count': 0,
            'jobs': [],
            'pagination': {
                'current_page': page,
                'page_size': page_size,
                'has_next': False,
                'has_previous': page > 1,
                'total_pages': None,
                'total_jobs': None
            },
            'metadata': {
                'data_source': 'unknown',
                'debug_info': {}
            },
            'error': 'An error occurred while scraping jobs',
            'message': error_details
        }


def _handle_details_task(
    scraper: NaukriScraper,
    job_url: str
) -> Dict[str, Any]:
    """
    Handle job details task.
    
    Args:
        scraper: Initialized NaukriScraper instance
        job_url: URL of the job detail page
    
    Returns:
        Structured response dictionary
    """
    try:
        # Scrape job details
        job_details = scraper.scrape_job_details(job_url)
        
        return {
            'success': True,
            'job_details': job_details,
            'error': None,
            'message': None
        }
    
    except Exception as e:
        import traceback
        error_details = str(e)
        traceback.print_exc()
        
        return {
            'success': False,
            'job_details': {},
            'error': 'An error occurred while scraping job details',
            'message': error_details
        }

