import React from 'react';
import JobCard from './JobCard';
import '../styles/JobList.css';

const JobList = ({ jobs, loading, hasSearched }) => {
  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Scraping jobs from Naukri.com...</p>
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
    return (
      <div className="empty-state">
        <p>No jobs found. Try adjusting your search criteria.</p>
      </div>
    );
  }

  return (
    <div className="job-list-container">
      <div className="job-list-header">
        <h2>Found {jobs.length} job{jobs.length !== 1 ? 's' : ''}</h2>
      </div>
      <div className="job-list">
        {jobs.map((job, index) => (
          <JobCard key={index} job={job} />
        ))}
      </div>
    </div>
  );
};

export default JobList;

