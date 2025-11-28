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
        # Initialize scraper
        scraper = NaukriScraper(headless=True)
        
        # Scrape jobs
        jobs = scraper.scrape_jobs(
            job_type=validated_data['job_type'],
            keyword=validated_data['keyword'],
            location=validated_data['location'],
            experience=validated_data.get('experience'),
            max_jobs=50
        )
        
        # Serialize job data
        job_serializer = JobSerializer(jobs, many=True)
        
        return Response({
            'success': True,
            'count': len(jobs),
            'jobs': job_serializer.data
        }, status=status.HTTP_200_OK)
        
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

