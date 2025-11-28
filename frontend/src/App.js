import React, { useState } from 'react';
import SearchForm from './components/SearchForm';
import JobList from './components/JobList';
import { searchJobs } from './services/api';
import './styles/App.css';

function App() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async (searchParams) => {
    setLoading(true);
    setError(null);
    setHasSearched(true);
    
    try {
      const data = await searchJobs(searchParams);

      if (data.success) {
        setJobs(data.jobs || []);
        // Don't show error for empty results - let JobList handle it
        if (!data.jobs || data.jobs.length === 0) {
          setError(null);
        }
      } else {
        setError(data.message || data.error || 'An error occurred while searching for jobs');
        setJobs([]);
      }
    } catch (err) {
      const errorMessage = err.message || err.error || 'Failed to connect to the server. Please make sure the backend is running.';
      setError(errorMessage);
      setJobs([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>Job Scraper</h1>
        <p>Find your dream job from Naukri.com</p>
      </header>
      
      <main className="app-main">
        <SearchForm onSearch={handleSearch} loading={loading} />
        
        {error && (
          <div className="error-message">
            <p>{error}</p>
          </div>
        )}
        
        <JobList 
          jobs={jobs} 
          loading={loading} 
          hasSearched={hasSearched}
        />
      </main>
    </div>
  );
}

export default App;

