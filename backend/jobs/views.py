"""
API views for job scraping
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import JobSearchSerializer, JobSerializer
from scraper.naukri_scraper import NaukriScraper


@api_view(['POST'])
def search_jobs(request):
    """
    Search and scrape jobs from Naukri.com
    
    Expected payload:
    {
        "job_type": "job" or "internship",
        "keyword": "web development",
        "location": "india",
        "experience": 1
    }
    """
    serializer = JobSearchSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {
                'success': False,
                'error': 'Invalid request data',
                'details': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    validated_data = serializer.validated_data
    scraper = None
    
    try:
        # Get pagination parameters
        page = validated_data.get('page', 1)
        page_size = validated_data.get('page_size', 20)
        
        # Initialize scraper
        scraper = NaukriScraper(headless=True)
        
        # Scrape jobs (now returns jobs and metadata)
        result = scraper.scrape_jobs(
            job_type=validated_data['job_type'],
            keyword=validated_data['keyword'],
            location=validated_data['location'],
            experience=validated_data.get('experience'),
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
        
        # Serialize job data
        job_serializer = JobSerializer(jobs, many=True)
        
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
        
        # Build response with metadata and pagination
        response_data = {
            'success': True,
            'count': current_count,
            'jobs': job_serializer.data,
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
            }
        }
        
        # Log the data source for debugging
        data_source = metadata.get('source', 'unknown')
        print(f"[VIEW] Request completed: {len(jobs)} jobs returned, data source: {data_source}")
        if data_source == 'api_fallback' or data_source == 'api':
            print(f"[VIEW] ⚠️  Data retrieved from API (scraping failed or unavailable)")
        else:
            print(f"[VIEW] ✓ Data retrieved from web scraping")
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        import traceback
        error_details = str(e)
        print(f"Error in search_jobs: {error_details}")
        traceback.print_exc()
        
        return Response(
            {
                'success': False,
                'error': 'An error occurred while scraping jobs',
                'message': error_details
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    finally:
        # Always close the scraper
        if scraper:
            try:
                scraper.close()
            except:
                pass


@api_view(['GET'])
def job_details(request):
    """
    Get detailed job information from a Naukri.com job detail page
    
    Query parameters:
    - url: The job detail URL from Naukri.com (required)
    """
    job_url = request.query_params.get('url', None)
    
    if not job_url:
        return Response(
            {
                'success': False,
                'error': 'Job URL is required',
                'message': 'Please provide a job URL in the query parameters'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    scraper = None
    
    try:
        # Initialize scraper
        scraper = NaukriScraper(headless=True)
        
        # Scrape job details
        job_details = scraper.scrape_job_details(job_url)
        
        return Response({
            'success': True,
            'job_details': job_details
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        import traceback
        error_details = str(e)
        print(f"Error in job_details: {error_details}")
        traceback.print_exc()
        
        return Response(
            {
                'success': False,
                'error': 'An error occurred while scraping job details',
                'message': error_details
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    finally:
        # Always close the scraper
        if scraper:
            try:
                scraper.close()
            except:
                pass

