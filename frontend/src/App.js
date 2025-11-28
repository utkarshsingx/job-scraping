import React, { useState, useMemo } from 'react';
import SearchForm from './components/SearchForm';
import JobList from './components/JobList';
import FilterSidebar from './components/FilterSidebar';
import { searchJobs } from './services/api';
import './styles/App.css';

function App() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [selectedTags, setSelectedTags] = useState([]);

  const handleSearch = async (searchParams) => {
    setLoading(true);
    setError(null);
    setHasSearched(true);
    setSelectedTags([]); // Clear filters on new search
    
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

  // Filter jobs based on selected tags
  const filteredJobs = useMemo(() => {
    if (selectedTags.length === 0) {
      return jobs;
    }
    
    return jobs.filter(job => {
      if (!job.tags || !Array.isArray(job.tags)) {
        return false;
      }
      // Job must have at least one of the selected tags
      return job.tags.some(tag => 
        selectedTags.includes(tag.trim())
      );
    });
  }, [jobs, selectedTags]);

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <div className="logo-section">
            <h1 className="logo-text">JobPortal</h1>
            <span className="logo-subtitle">Find Your Dream Job</span>
          </div>
        </div>
      </header>
      
      <main className="app-main">
        <SearchForm onSearch={handleSearch} loading={loading} />
        
        {error && (
          <div className="error-message">
            <p>{error}</p>
          </div>
        )}
        
        {hasSearched && (
          <div className={jobs.length > 0 ? "content-layout" : ""}>
            {jobs.length > 0 && (
              <FilterSidebar 
                jobs={jobs} 
                selectedTags={selectedTags}
                onFilterChange={setSelectedTags}
              />
            )}
            <JobList 
              jobs={filteredJobs} 
              loading={loading} 
              hasSearched={hasSearched}
              totalCount={jobs.length}
            />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;

