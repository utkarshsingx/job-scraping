# Job Scrapper

A full-stack web application for scraping job listings from Naukri.com with a modern React frontend and Django REST API backend.

## Features

- 🔍 Search jobs with multiple parameters:
  - Job type (Job/Internship)
  - Keyword (job title, skills, etc.)
  - Location
  - Experience (years)
- 📋 Display job cards with:
  - Job title
  - Company name, logo, rating, and reviews
  - Experience, salary, and location
  - Job description
  - Tags/skills
  - Job post date
- 🎨 Modern, responsive UI
- ⚡ Fast scraping using Selenium WebDriver

## Tech Stack

### Backend
- Django 4.2
- Django REST Framework
- Selenium WebDriver
- BeautifulSoup4
- Pandas & NumPy

### Frontend
- React 18
- Axios (for API calls)
- Modern CSS with gradient design

## Prerequisites

- Python 3.8+
- Node.js 14+
- npm or yarn
- Chrome browser (for Selenium)

## Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Run database migrations:
```bash
python3 manage.py migrate
```

5. Start the Django development server:
```bash
python3 manage.py runserver
```

The backend will be running at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node dependencies:
```bash
npm install
```

3. Start the React development server:
```bash
npm start
```

The frontend will be running at `http://localhost:3000`

## Usage

1. Make sure both backend and frontend servers are running
2. Open `http://localhost:3000` in your browser
3. Fill in the search form:
   - Select job type (Job or Internship)
   - Enter keyword (e.g., "web development", "python developer")
   - Enter location (e.g., "india", "bangalore")
   - Enter experience in years (e.g., 1, 2, 3)
4. Click "Search Jobs" to scrape and display results
5. Browse through the job cards with all details

## API Endpoints

### POST `/api/jobs/search/`

Search and scrape jobs from Naukri.com

**Request Body:**
```json
{
  "job_type": "job",
  "keyword": "web development",
  "location": "india",
  "experience": 1
}
```

**Response:**
```json
{
  "success": true,
  "count": 20,
  "jobs": [
    {
      "job_title": "Web Developer",
      "company_name": "ABC Company",
      "company_logo": "https://...",
      "rating": "4.5",
      "reviews": "150 reviews",
      "experience": "1-3 Yrs",
      "salary": "3-5 Lakhs",
      "location": "Bangalore",
      "job_description": "Job description text...",
      "tags": ["React", "JavaScript", "Node.js"],
      "job_post_date": "2 days ago"
    }
  ]
}
```

## Project Structure

```
job-scrapper/
├── backend/
│   ├── backend/          # Django project settings
│   ├── jobs/             # Jobs app (API views, serializers)
│   ├── scraper/          # Web scraping logic
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── services/     # API service
│   │   └── styles/       # CSS files
│   └── package.json
└── README.md
```

## Notes

- The scraper uses Selenium WebDriver in headless mode
- ChromeDriver is automatically downloaded and managed by webdriver-manager
- Scraping may take 10-30 seconds depending on the number of results
- Make sure Chrome browser is installed for Selenium to work
- The scraper handles missing elements gracefully

## Troubleshooting

1. **ChromeDriver issues**: Make sure Chrome browser is installed and up to date
2. **CORS errors**: Ensure backend CORS settings allow requests from frontend (localhost:3000)
3. **No jobs found**: Check your search parameters and try different keywords/locations
4. **Scraping timeout**: Increase wait times in the scraper if pages load slowly

## License

This project is for educational purposes only. Please respect Naukri.com's terms of service when using this scraper.

