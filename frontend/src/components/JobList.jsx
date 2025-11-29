import React, { useState, useEffect } from 'react';
import JobCard from './JobCard';
import '../styles/JobList.css';

const LOADING_STEPS = [
  'Analyzing your skills and preferences',
  'Finding matching jobs for your profile',
  'Checking locations and commute options',
  'Evaluating company fit and culture',
  'Sorting results by freshness and relevance',
  'Finalizing your personalized job list'
];

const LOADING_FUN_FACTS = [
  'Fun fact: Most recruiters scan a resume in under 7 seconds.',
  'Fun fact: Tailored applications get far more callbacks than generic ones.',
  'Fun fact: Many great jobs are never advertised publicly.',
  'Fun fact: Clear, concise job titles attract more applicants.',
  'Fun fact: Highlighting skills in-demand can double your profile views.',
  'Fun fact: Recruiters often search by skills before job titles.'
];

const JobList = ({ jobs, loading, hasSearched, totalCount = null, searchState = null }) => {
  const [stepIndex, setStepIndex] = useState(0);
  const [funFact, setFunFact] = useState('');

  useEffect(() => {
    let intervalId;
    if (loading) {
      setStepIndex(0);
      const randomFact =
        LOADING_FUN_FACTS[Math.floor(Math.random() * LOADING_FUN_FACTS.length)];
      setFunFact(randomFact);

      intervalId = setInterval(() => {
        setStepIndex((prev) =>
          prev < LOADING_STEPS.length - 1 ? prev + 1 : prev
        );
      }, 800);
    } else {
      setStepIndex(0);
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [loading]);

  if (loading) {
    const percent = Math.min(
      100,
      Math.round(((stepIndex + 1) / LOADING_STEPS.length) * 100)
    );

    return (
      <div className="loading-container">
        <div className="loading-progress">
          <div className="loading-header-main">
            <div className="loading-left">
              <div className="loading-icon" />
              <div className="loading-meta">
                <span className="loading-label">Searching jobs</span>
                <span className="loading-step-label">
                  Step {stepIndex + 1} of {LOADING_STEPS.length}
                </span>
              </div>
            </div>
            <span className="loading-percent">{percent}%</span>
          </div>
          <p className="loading-main-text">{LOADING_STEPS[stepIndex]}</p>
          <div className="loading-bar">
            <div
              className="loading-bar-fill"
              style={{ width: `${percent}%` }}
            />
          </div>
          <div className="loading-steps-dots">
            {LOADING_STEPS.map((_, index) => (
              <span
                key={index}
                className={
                  index <= stepIndex
                    ? 'loading-step-dot active'
                    : 'loading-step-dot'
                }
              />
            ))}
          </div>
        </div>
        {funFact && (
          <p className="loading-fun-fact">
            <span className="label">Did you know?</span> {funFact}
          </p>
        )}
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

