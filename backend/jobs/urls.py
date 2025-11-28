"""
URL routing for jobs app
"""
from django.urls import path
from . import views

urlpatterns = [
    path('jobs/search/', views.search_jobs, name='search_jobs'),
    path('jobs/details/', views.job_details, name='job_details'),
]

