"""
URL routing for jobs app
"""
from django.urls import path
from . import views

urlpatterns = [
    path('jobs/search/', views.search_jobs, name='search_jobs'),
]

