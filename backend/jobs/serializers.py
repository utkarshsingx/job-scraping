"""
Serializers for job data
"""
from rest_framework import serializers


class JobSerializer(serializers.Serializer):
    """Serializer for job data"""
    job_title = serializers.CharField(required=False, allow_blank=True)
    company_name = serializers.CharField(required=False, allow_blank=True)
    company_logo = serializers.URLField(required=False, allow_blank=True)
    rating = serializers.CharField(required=False, allow_blank=True)
    reviews = serializers.CharField(required=False, allow_blank=True)
    experience = serializers.CharField(required=False, allow_blank=True)
    salary = serializers.CharField(required=False, allow_blank=True)
    location = serializers.CharField(required=False, allow_blank=True)
    job_description = serializers.CharField(required=False, allow_blank=True)
    tags = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    job_post_date = serializers.CharField(required=False, allow_blank=True)


class JobSearchSerializer(serializers.Serializer):
    """Serializer for job search request"""
    job_type = serializers.ChoiceField(
        choices=[('job', 'Job'), ('internship', 'Internship')],
        required=True
    )
    keyword = serializers.CharField(required=True, max_length=200)
    location = serializers.CharField(required=True, max_length=200)
    experience = serializers.IntegerField(required=True, min_value=0)

