import React from 'react';
import JobCard from './JobCard';
import '../styles/JobList.css';

const JobList = ({ jobs, loading, hasSearched, totalCount = null, searchState = null }) => {
  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Searching for jobs...</p>
      </div>
    );
  }

  if (!hasSearched) {
    return (
      <div className="empty-state">
        <p>Enter search criteria above to find jobs</p>
      </div>
    );
  }

  if (jobs.length === 0) {
    if (hasSearched && totalCount !== null && totalCount > 0) {
      return (
        <div className="empty-state">
          <p>No jobs match the selected filters. Try adjusting your filters.</p>
        </div>
      );
    }
    return (
      <div className="empty-state">
        <p>No jobs found. Try adjusting your search criteria.</p>
      </div>
    );
  }

  return (
    <div className="job-list-container">
      <div className="job-list-header">
        <h2>
          {totalCount !== null && totalCount !== jobs.length 
            ? `Showing ${jobs.length} of ${totalCount} job${totalCount !== 1 ? 's' : ''}`
            : `Found ${jobs.length} job${jobs.length !== 1 ? 's' : ''}`
          }
        </h2>
      </div>
      <div className="job-list">
        {jobs.map((job, index) => (
          <JobCard key={index} job={job} searchState={searchState} />
        ))}
      </div>
    </div>
  );
};

export default JobList;

