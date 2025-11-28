import React, { useState, useMemo, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import SearchForm from './SearchForm';
import JobList from './JobList';
import FilterSidebar from './FilterSidebar';
import Pagination from './Pagination';
import { searchJobs } from '../services/api';

const STORAGE_KEY = 'jobSearchState';

const JobsPage = () => {
  const location = useLocation();
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [selectedTags, setSelectedTags] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [pagination, setPagination] = useState(null);
  const [searchParams, setSearchParams] = useState(null);

  // Restore state from location state (when coming back from job detail) or sessionStorage
  useEffect(() => {
    // First, try to restore from location state (most recent)
    if (location.state && location.state.restoreState) {
      const restoredState = location.state.restoreState;
      setJobs(restoredState.jobs || []);
      setHasSearched(restoredState.hasSearched || false);
      setSelectedTags(restoredState.selectedTags || []);
      setCurrentPage(restoredState.currentPage || 1);
      setPagination(restoredState.pagination || null);
      setSearchParams(restoredState.searchParams || null);
      setError(restoredState.error || null);
      
      // Clear the location state to prevent restoring again
      window.history.replaceState({}, document.title);
      
      // Restore scroll position after a brief delay to allow rendering
      setTimeout(() => {
        const savedScrollPosition = sessionStorage.getItem('jobSearchScrollPosition');
        if (savedScrollPosition) {
          window.scrollTo(0, parseInt(savedScrollPosition, 10));
          sessionStorage.removeItem('jobSearchScrollPosition');
        }
      }, 100);
      return;
    }

    // Otherwise, try to restore from sessionStorage
    try {
      const savedState = sessionStorage.getItem(STORAGE_KEY);
      if (savedState) {
        const parsedState = JSON.parse(savedState);
        setJobs(parsedState.jobs || []);
        setHasSearched(parsedState.hasSearched || false);
        setSelectedTags(parsedState.selectedTags || []);
        setCurrentPage(parsedState.currentPage || 1);
        setPagination(parsedState.pagination || null);
        setSearchParams(parsedState.searchParams || null);
      }
    } catch (err) {
      console.error('Error restoring state from sessionStorage:', err);
    }
  }, [location]);

  // Save scroll position before navigating away
  useEffect(() => {
    const handleBeforeUnload = () => {
      sessionStorage.setItem('jobSearchScrollPosition', window.scrollY.toString());
    };
    
    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, []);

  // Save state to sessionStorage whenever it changes
  useEffect(() => {
    if (hasSearched && jobs.length > 0) {
      const stateToSave = {
        jobs,
        hasSearched,
        selectedTags,
        currentPage,
        pagination,
        searchParams
      };
      try {
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(stateToSave));
      } catch (err) {
        console.error('Error saving state to sessionStorage:', err);
      }
    }
  }, [jobs, hasSearched, selectedTags, currentPage, pagination, searchParams]);

  const handleSearch = async (params, page = 1) => {
    setLoading(true);
    setError(null);
    setHasSearched(true);
    setCurrentPage(page);
    setSearchParams(params);
    
    // Clear filters and pagination on new search (not when changing page)
    if (page === 1) {
      setSelectedTags([]);
      // Clear saved state for new search
      try {
        sessionStorage.removeItem(STORAGE_KEY);
      } catch (err) {
        console.error('Error clearing sessionStorage:', err);
      }
    }
    
    try {
      const data = await searchJobs({ ...params, page });

      if (data.success) {
        if (page === 1) {
          setJobs(data.jobs || []);
        } else {
          setJobs(data.jobs || []);
        }
        setPagination(data.pagination || null);
        
        if (!data.jobs || data.jobs.length === 0) {
          setError(null);
        }
      } else {
        setError(data.message || data.error || 'An error occurred while searching for jobs');
        setJobs([]);
        setPagination(null);
      }
    } catch (err) {
      const errorMessage = err.message || err.error || 'Failed to connect to the server. Please make sure the backend is running.';
      setError(errorMessage);
      setJobs([]);
      setPagination(null);
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (newPage) => {
    if (searchParams && !loading) {
      window.scrollTo({ top: 0, behavior: 'smooth' });
      handleSearch(searchParams, newPage);
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
      return job.tags.some(tag => 
        selectedTags.includes(tag.trim())
      );
    });
  }, [jobs, selectedTags]);

  return (
    <>
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
          <div style={{ flex: 1 }}>
            <JobList 
              jobs={filteredJobs} 
              loading={loading} 
              hasSearched={hasSearched}
              totalCount={jobs.length}
              searchState={{
                jobs,
                hasSearched,
                selectedTags,
                currentPage,
                pagination,
                searchParams
              }}
            />
            
            {pagination && jobs.length > 0 && (
              <Pagination
                currentPage={pagination.current_page}
                hasNext={pagination.has_next}
                hasPrevious={pagination.has_previous}
                onPageChange={handlePageChange}
                loading={loading}
              />
            )}
          </div>
        </div>
      )}
    </>
  );
};

export default JobsPage;

