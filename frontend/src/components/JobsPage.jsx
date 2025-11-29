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
  const [filters, setFilters] = useState({});
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
      setFilters(restoredState.filters || {});
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
        setFilters(parsedState.filters || {});
        setCurrentPage(parsedState.currentPage || 1);
        setPagination(parsedState.pagination || null);
        setSearchParams(parsedState.searchParams || null);
      }
    } catch (err) {
      // Error restoring state from sessionStorage
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
        filters,
        currentPage,
        pagination,
        searchParams
      };
      try {
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(stateToSave));
      } catch (err) {
        // Error saving state to sessionStorage
      }
    }
  }, [jobs, hasSearched, filters, currentPage, pagination, searchParams]);

  const handleSearch = async (params, page = 1) => {
    setLoading(true);
    setError(null);
    setHasSearched(true);
    setCurrentPage(page);
    setSearchParams(params);
    
    // Clear filters and pagination on new search (not when changing page)
    if (page === 1) {
      setFilters({});
      // Clear saved state for new search
      try {
        sessionStorage.removeItem(STORAGE_KEY);
      } catch (err) {
        // Error clearing sessionStorage
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

  // Filter jobs based on all selected filters
  const filteredJobs = useMemo(() => {
    const hasActiveFilters = Object.values(filters).some(arr => arr && arr.length > 0);
    
    if (!hasActiveFilters) {
      return jobs;
    }
    
    return jobs.filter(job => {
      // Department filter
      if (filters.department && filters.department.length > 0) {
        const jobTitle = (job.job_title || '').toLowerCase();
        const matchesDepartment = filters.department.some(dept => {
          const deptLower = dept.toLowerCase();
          if (deptLower.includes('engineering') && (jobTitle.includes('engineering') || jobTitle.includes('developer') || jobTitle.includes('software'))) return true;
          if (deptLower.includes('marketing') && jobTitle.includes('marketing')) return true;
          if (deptLower.includes('sales') && jobTitle.includes('sales')) return true;
          if (deptLower.includes('design') && (jobTitle.includes('design') || jobTitle.includes('ui') || jobTitle.includes('ux'))) return true;
          if (deptLower.includes('data') && (jobTitle.includes('data') || jobTitle.includes('analyst') || jobTitle.includes('science'))) return true;
          if (deptLower.includes('hr') && jobTitle.includes('hr')) return true;
          if (deptLower.includes('finance') && jobTitle.includes('finance')) return true;
          if (deptLower.includes('operations') && jobTitle.includes('operations')) return true;
          return false;
        });
        if (!matchesDepartment) return false;
      }

      // Role Category filter
      if (filters.roleCategory && filters.roleCategory.length > 0) {
        const tags = (job.tags || []).map(t => t.toLowerCase()).join(' ');
        const jobTitle = (job.job_title || '').toLowerCase();
        const matchesRole = filters.roleCategory.some(role => {
          const roleLower = role.toLowerCase();
          return tags.includes(roleLower) || jobTitle.includes(roleLower);
        });
        if (!matchesRole) return false;
      }

      // Stipend filter
      if (filters.stipend && filters.stipend.length > 0) {
        const salary = (job.salary || '').toLowerCase();
        const matchesStipend = filters.stipend.some(stipend => {
          if (stipend === 'Unpaid' && (salary.includes('unpaid') || salary.includes('no stipend') || salary === 'not disclosed')) return true;
          if (stipend === '0-10k') {
            const match = salary.match(/(\d+)\s*k|(\d+)\s*thousand/i);
            if (match) {
              const amount = parseInt(match[1] || match[2]);
              return amount >= 0 && amount < 10;
            }
            return !salary.includes('lakh') && !salary.includes('lpa');
          }
          if (stipend === '10k-20k') {
            const match = salary.match(/(\d+)\s*k|(\d+)\s*thousand/i);
            if (match) {
              const amount = parseInt(match[1] || match[2]);
              return amount >= 10 && amount < 20;
            }
            return salary.includes('lakh') || salary.includes('lpa');
          }
          if (stipend === '20k-30k') {
            const match = salary.match(/(\d+)\s*k|(\d+)\s*thousand/i);
            if (match) {
              const amount = parseInt(match[1] || match[2]);
              return amount >= 20 && amount < 30;
            }
            return false;
          }
          if (stipend === '30k+') {
            const match = salary.match(/(\d+)\s*k|(\d+)\s*thousand/i);
            if (match) {
              const amount = parseInt(match[1] || match[2]);
              return amount >= 30;
            }
            return false;
          }
          return false;
        });
        if (!matchesStipend) return false;
      }

      // Work Mode filter
      if (filters.workMode && filters.workMode.length > 0) {
        const location = (job.location || '').toLowerCase();
        const description = (job.job_description || '').toLowerCase();
        const matchesWorkMode = filters.workMode.some(mode => {
          if (mode === 'Remote') {
            return location.includes('remote') || location.includes('work from home') || location.includes('wfh') ||
                   description.includes('remote') || description.includes('work from home') || description.includes('wfh');
          }
          if (mode === 'On-site') {
            return !location.includes('remote') && !location.includes('work from home') && !location.includes('wfh') &&
                   !description.includes('remote') && !description.includes('work from home') && !description.includes('wfh');
          }
          if (mode === 'Hybrid') {
            return description.includes('hybrid');
          }
          return false;
        });
        if (!matchesWorkMode) return false;
      }


      // Location filter
      if (filters.location && filters.location.length > 0) {
        const jobLocations = (job.location || '').split(',').map(loc => loc.trim());
        const matchesLocation = filters.location.some(filterLoc => {
          return jobLocations.some(jobLoc => 
            jobLoc.toLowerCase().includes(filterLoc.toLowerCase()) || 
            filterLoc.toLowerCase().includes(jobLoc.toLowerCase())
      );
        });
        if (!matchesLocation) return false;
      }

      return true;
    });
  }, [jobs, filters]);

  return (
    <>
      <header className="app-header">
        <div className="header-content">
          <div className="logo-section">
            <h1 className="logo-text">JobPortal</h1>
          </div>
      <SearchForm onSearch={handleSearch} loading={loading} />
        </div>
      </header>
      
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
              filters={filters}
              onFilterChange={setFilters}
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
                filters,
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

