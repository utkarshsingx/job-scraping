#!/usr/bin/env python3
"""
Quick test script to verify scraping vs API fallback detection
Run this while your Django server is running
"""

import requests
import json

API_URL = "http://localhost:8000/api/jobs/search/"

def test_search(job_type, keyword, location, experience=0):
    """Test a search and show data source"""
    payload = {
        "job_type": job_type,
        "keyword": keyword,
        "location": location,
        "experience": experience
    }
    
    print(f"\n{'='*60}")
    print(f"Testing: {job_type} - {keyword} in {location}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(API_URL, json=payload, timeout=60)
        data = response.json()
        
        print(f"\n✅ Response Status: {response.status_code}")
        print(f"📊 Jobs Found: {data.get('count', 0)}")
        
        # Check metadata
        metadata = data.get('metadata', {})
        data_source = metadata.get('data_source', 'unknown')
        debug_info = metadata.get('debug_info', {})
        
        print(f"\n🔍 DATA SOURCE: {data_source.upper()}")
        
        if data_source == 'scraping':
            print("   ✓ Data retrieved from web scraping")
        elif data_source == 'api_fallback':
            print("   ⚠️  Data retrieved from API (scraping failed)")
        elif data_source == 'api':
            print("   ℹ️  Data retrieved directly from API")
        
        # Show debug info
        print(f"\n📋 Debug Info:")
        if debug_info.get('scraping_attempted'):
            print(f"   • Scraping attempted: Yes")
            print(f"   • Scraping successful: {debug_info.get('scraping_success', False)}")
        
        if debug_info.get('api_fallback_used'):
            print(f"   • API fallback used: Yes")
        
        if debug_info.get('api_attempted'):
            print(f"   • API attempted: Yes")
            print(f"   • API successful: {debug_info.get('api_success', False)}")
            if debug_info.get('api_status_code'):
                print(f"   • API status code: {debug_info.get('api_status_code')}")
        
        # Show errors if any
        scraping_errors = debug_info.get('scraping_errors', [])
        api_errors = debug_info.get('api_errors', [])
        
        if scraping_errors:
            print(f"\n❌ Scraping Errors:")
            for error in scraping_errors:
                print(f"   • {error}")
        
        if api_errors:
            print(f"\n❌ API Errors:")
            for error in api_errors:
                print(f"   • {error}")
        
        return data
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Error: Could not connect to {API_URL}")
        print("   Make sure the Django server is running!")
        return None
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("🧪 Testing Scraper Debug Feature")
    print("Make sure your Django backend is running on http://localhost:8000")
    print("\nPress Ctrl+C to cancel\n")
    
    # Test cases
    tests = [
        ("internship", "graphic designer", "pune", 0),
        ("job", "python developer", "india", 1),
    ]
    
    for test in tests:
        test_search(*test)
        input("\nPress Enter to continue to next test...")
    
    print("\n✅ Testing complete!")

