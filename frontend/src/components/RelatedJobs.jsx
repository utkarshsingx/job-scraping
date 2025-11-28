import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/RelatedJobs.css';

const RelatedJobs = ({ jobs, currentJobUrl, searchState }) => {
  const navigate = useNavigate();

  // Get company initial for logo fallback
  const getCompanyInitial = (companyName) => {
    if (!companyName || companyName === 'N/A') return '?';
    const words = companyName.trim().split(/\s+/);
    if (words.length >= 2) {
      return (words[0][0] + words[1][0]).toUpperCase();
    }
    return companyName[0].toUpperCase();
  };

  // Filter out current job and limit to 6 jobs
  const relatedJobs = jobs
    .filter(job => {
      if (!currentJobUrl || !job.job_url) return true;
      // Compare URLs (handle both encoded and decoded versions)
      const jobUrlClean = job.job_url.replace(/\/$/, '').trim();
      const currentUrlClean = currentJobUrl.replace(/\/$/, '').trim();
      return jobUrlClean !== currentUrlClean;
    })
    .slice(0, 6);

  if (relatedJobs.length === 0) {
    return null;
  }

  const handleJobClick = (job) => {
    if (job.job_url) {
      // Save current scroll position
      sessionStorage.setItem('jobSearchScrollPosition', window.scrollY.toString());
      
      // Encode the URL for use in route
      const encodedUrl = encodeURIComponent(job.job_url);
      // Pass search state so it can be restored when going back
      navigate(`/job/${encodedUrl}`, {
        state: {
          restoreState: searchState
        }
      });
    }
  };

  return (
    <div className="related-jobs-sidebar">
      <h2 className="related-jobs-title">Jobs you might be interested in</h2>
      <div className="related-jobs-list">
        {relatedJobs.map((job, index) => {
          const companyInitial = getCompanyInitial(job.company_name);
          
          return (
            <div
              key={index}
              className="related-job-card"
              onClick={() => handleJobClick(job)}
            >
              <div className="related-job-content">
                <div className="related-job-left">
                  <h3 className="related-job-title">{job.job_title || 'N/A'}</h3>
                  <div className="related-job-company">{job.company_name || 'N/A'}</div>
                  {(job.rating || job.reviews) && (
                    <div className="related-job-rating">
                      {job.rating && (
                        <span className="related-rating">
                          <span className="star">★</span>
                          {job.rating}
                        </span>
                      )}
                      {job.reviews && (
                        <span className="related-reviews">{job.reviews}</span>
                      )}
                    </div>
                  )}
                  {job.location && (
                    <div className="related-job-location">{job.location}</div>
                  )}
                </div>
                <div className="related-job-right">
                  <div 
                    className={`related-job-logo-wrapper ${!job.company_logo ? 'no-logo' : ''}`}
                    data-initial={companyInitial}
                  >
                    {job.company_logo ? (
                      <img 
                        src={job.company_logo} 
                        alt={job.company_name || 'Company logo'}
                        className="related-job-logo"
                        onError={(e) => {
                          e.target.style.display = 'none';
                          e.target.parentElement.classList.add('no-logo');
                        }}
                      />
                    ) : (
                      <span className="related-company-initial">{companyInitial}</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default RelatedJobs;

