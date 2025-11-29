"""
API views for job scraping
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import JobSearchSerializer, JobSerializer
from scraper.naukri_service import get_naukri_data


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
    
    # Get pagination parameters
    page = validated_data.get('page', 1)
    page_size = validated_data.get('page_size', 20)
    
    # Call the standalone service function
    result = get_naukri_data(
        task_type='search',
        job_type=validated_data['job_type'],
        keyword=validated_data['keyword'],
        location=validated_data['location'],
        experience=validated_data.get('experience'),
        page=page,
        page_size=page_size,
        headless=True
    )
    
    # Handle error response
    if not result.get('success'):
        return Response(
            {
                'success': False,
                'error': result.get('error', 'An error occurred while scraping jobs'),
                'message': result.get('message', 'Unknown error')
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Serialize job data using Django serializer
    jobs = result.get('jobs', [])
    job_serializer = JobSerializer(jobs, many=True)
    
    # Build response with serialized data
    response_data = {
        'success': True,
        'count': result.get('count', 0),
        'jobs': job_serializer.data,
        'pagination': result.get('pagination', {}),
        'metadata': result.get('metadata', {})
    }
    
    return Response(response_data, status=status.HTTP_200_OK)


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
    
    # Call the standalone service function
    result = get_naukri_data(
        task_type='details',
        job_url=job_url,
        headless=True
    )
    
    # Handle error response
    if not result.get('success'):
        return Response(
            {
                'success': False,
                'error': result.get('error', 'An error occurred while scraping job details'),
                'message': result.get('message', 'Unknown error')
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Return successful response
    return Response({
        'success': True,
        'job_details': result.get('job_details', {})
    }, status=status.HTTP_200_OK)

