#!/usr/bin/env python3
"""
Verification script to test job details scraping and verify all fields are extracted correctly
"""

import sys
import os
import json

# Add parent directory to path to allow imports
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir) if os.path.basename(script_dir) == 'backend' else script_dir
sys.path.insert(0, parent_dir)
sys.path.insert(0, script_dir)

try:
    from scraper.naukri_scraper import NaukriScraper
except ImportError as e:
    print("=" * 80)
    print("IMPORT ERROR")
    print("=" * 80)
    print(f"\nFailed to import scraper module: {e}")
    print("\nMake sure you:")
    print("  1. Are running this script from the backend directory")
    print("  2. Have activated the virtual environment")
    print("  3. Have installed all dependencies (pip install -r requirements.txt)")
    print("\nTo activate virtual environment:")
    print("  cd backend")
    print("  source venv/bin/activate  # On macOS/Linux")
    print("  # or")
    print("  venv\\Scripts\\activate  # On Windows")
    print("\nThen run:")
    print("  python3 verify_job_details_scraping.py <job_url>")
    print("=" * 80)
    sys.exit(1)


def verify_job_details_scraping(job_url):
    """
    Test job details scraping and verify all fields
    
    Args:
        job_url: URL of a job detail page to test
    """
    print("=" * 80)
    print("JOB DETAILS SCRAPING VERIFICATION")
    print("=" * 80)
    print(f"\nTesting with job URL: {job_url}\n")
    
    scraper = None
    try:
        # Initialize scraper
        print("[1/3] Initializing scraper...")
        scraper = NaukriScraper(headless=True)
        print("✓ Scraper initialized\n")
        
        # Scrape job details
        print("[2/3] Scraping job details...")
        print("-" * 80)
        job_details = scraper.scrape_job_details(job_url)
        print("-" * 80)
        print("✓ Scraping completed\n")
        
        # Verify fields
        print("[3/3] Verifying extracted fields...")
        print("=" * 80)
        
        # Define all expected fields
        expected_fields = {
            'Basic Information': [
                'header_title',
                'company_title',
                'company_logo',
                'rating',
                'reviews',
                'experience',
                'salary',
                'location',
                'posted',
                'openings',
                'applicants',
                'apply_button_text',
                'internship_label'
            ],
            'Job Highlights & Match': [
                'job_highlights',
                'job_match_score'
            ],
            'Job Description': [
                'job_description_header',
                'job_description_content',
                'job_description_div'
            ],
            'Role & Responsibilities': [
                'role_and_responsibilities'
            ],
            'Job Details': [
                'role',
                'industry_type',
                'department',
                'employment_type',
                'role_category'
            ],
            'Education': [
                'education_title',
                'ug_education',
                'pg_education'
            ],
            'Skills': [
                'key_skills'
            ],
            'Company Information': [
                'about_company_header',
                'about_company_description',
                'company_info_header',
                'company_address'
            ]
        }
        
        # Count extracted fields
        total_fields = 0
        extracted_fields = 0
        missing_fields = []
        
        for category, fields in expected_fields.items():
            print(f"\n{category}:")
            print("-" * 60)
            
            for field in fields:
                total_fields += 1
                value = job_details.get(field)
                
                # Check if field has value
                has_value = False
                if isinstance(value, dict):
                    # For structured fields, check if they have any content
                    if value:
                        has_value = any(v for v in value.values() if v)
                elif isinstance(value, list):
                    has_value = len(value) > 0
                elif value:
                    has_value = bool(str(value).strip())
                
                if has_value:
                    extracted_fields += 1
                    status = "✓"
                    
                    # Show preview of value
                    if isinstance(value, dict):
                        preview = f"{field}: {{"
                        for k, v in value.items():
                            if v:
                                if isinstance(v, list):
                                    preview += f" {k}: [{len(v)} items],"
                                else:
                                    preview_val = str(v)[:50] + "..." if len(str(v)) > 50 else str(v)
                                    preview += f" {k}: '{preview_val}',"
                        preview = preview.rstrip(',') + " }"
                        print(f"  {status} {preview}")
                    elif isinstance(value, list):
                        preview = f"{field}: [{len(value)} items]"
                        if value:
                            sample = str(value[0])[:30] + "..." if len(str(value[0])) > 30 else str(value[0])
                            preview += f" (e.g., '{sample}')"
                        print(f"  {status} {preview}")
                    else:
                        preview = str(value)[:80] + "..." if len(str(value)) > 80 else str(value)
                        print(f"  {status} {field}: '{preview}'")
                else:
                    status = "✗"
                    missing_fields.append(field)
                    print(f"  {status} {field}: NOT FOUND")
        
        # Summary
        print("\n" + "=" * 80)
        print("VERIFICATION SUMMARY")
        print("=" * 80)
        print(f"Total fields expected: {total_fields}")
        print(f"Fields successfully extracted: {extracted_fields}")
        print(f"Fields not found: {total_fields - extracted_fields}")
        print(f"Success rate: {(extracted_fields/total_fields)*100:.1f}%")
        
        if missing_fields:
            print(f"\nMissing fields: {', '.join(missing_fields)}")
        
        # Show key fields status
        print("\n" + "-" * 80)
        print("KEY FIELDS STATUS:")
        print("-" * 80)
        key_fields = ['header_title', 'company_title', 'job_description_content', 
                     'key_skills', 'about_company_description']
        for field in key_fields:
            value = job_details.get(field)
            has_value = bool(value and (isinstance(value, (list, dict)) and value or str(value).strip()))
            status = "✓ FOUND" if has_value else "✗ MISSING"
            print(f"  {field}: {status}")
        
        # Save full details to file for inspection
        output_file = 'job_details_verification_output.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(job_details, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Full job details saved to: {output_file}")
        
        print("\n" + "=" * 80)
        
        # Return success if key fields are present
        key_fields_found = all(
            job_details.get(field) and 
            (isinstance(job_details.get(field), (list, dict)) and job_details.get(field) or 
             str(job_details.get(field)).strip())
            for field in key_fields[:3]  # At least header_title, company_title, job_description_content
        )
        
        if key_fields_found:
            print("✓ VERIFICATION PASSED: Key fields successfully extracted")
            return True
        else:
            print("✗ VERIFICATION FAILED: Some key fields are missing")
            return False
            
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if scraper:
            try:
                scraper.close()
                print("\n✓ Scraper closed")
            except:
                pass


if __name__ == '__main__':
    # Check if running from correct directory and with venv
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(os.path.join(script_dir, 'scraper', 'naukri_scraper.py')):
        print("ERROR: Cannot find scraper module.")
        print(f"Expected location: {os.path.join(script_dir, 'scraper', 'naukri_scraper.py')}")
        print("\nMake sure you're running this script from the backend directory.")
        sys.exit(1)
    
    # Test with a sample job URL (user should provide a real one)
    if len(sys.argv) > 1:
        job_url = sys.argv[1].strip()
        
        # Validate URL format
        if not job_url.startswith('http'):
            print("=" * 80)
            print("ERROR: Invalid URL format")
            print("=" * 80)
            print("\nPlease provide a full URL starting with http:// or https://")
            print(f"\nYou provided: {job_url}")
            print("\nExample of valid URL:")
            print("  https://www.naukri.com/job-listings-software-engineer-abc-company-mumbai-2-to-5-years-123456")
            print("=" * 80)
            sys.exit(1)
            
        success = verify_job_details_scraping(job_url)
        sys.exit(0 if success else 1)
    else:
        print("=" * 80)
        print("JOB DETAILS SCRAPING VERIFICATION SCRIPT")
        print("=" * 80)
        print("\nThis script tests job details scraping with a specific job URL.")
        print("\n✓ Script is ready. A job URL is required to run the verification.")
        print("\nUSAGE:")
        print("  cd backend")
        print("  source venv/bin/activate  # Activate virtual environment")
        print("  python3 verify_job_details_scraping.py <job_url>")
        print("\nEXAMPLE:")
        print("  python3 verify_job_details_scraping.py 'https://www.naukri.com/job-listings-...'")
        print("\nHOW TO GET A JOB URL:")
        print("  1. Search for jobs on your frontend application")
        print("  2. Click on any job card to view details")
        print("  3. Copy the job URL from the browser address bar")
        print("  4. Use that URL with this script")
        print("\n  OR")
        print("  1. Search for jobs on Naukri.com directly")
        print("  2. Click on a job listing")
        print("  3. Copy the full URL from the address bar")
        print("\nNOTE: This is not an error - the script requires a job URL to test.")
        print("=" * 80)
        sys.exit(0)  # Exit with 0 (success) since this is just showing help

