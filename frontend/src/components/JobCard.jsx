import React from 'react';
import '../styles/JobCard.css';

const JobCard = ({ job }) => {
  // Get company initial for logo fallback
  const getCompanyInitial = (companyName) => {
    if (!companyName || companyName === 'N/A') return '?';
    const words = companyName.trim().split(/\s+/);
    if (words.length >= 2) {
      return (words[0][0] + words[1][0]).toUpperCase();
    }
    return companyName[0].toUpperCase();
  };

  const companyInitial = getCompanyInitial(job.company_name);

  return (
    <div className="job-card">
      <div className="job-card-top">
        <div className="job-card-header">
          <div className="job-title-section">
            <h3 className="job-title">{job.job_title || 'N/A'}</h3>
            <div className="company-info">
              <div 
                className={`company-logo-wrapper ${!job.company_logo ? 'no-logo' : ''}`}
                data-initial={companyInitial}
              >
                {job.company_logo ? (
                  <img 
                    src={job.company_logo} 
                    alt={job.company_name || 'Company logo'}
                    className="company-logo"
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.parentElement.classList.add('no-logo');
                    }}
                  />
                ) : (
                  <span className="company-initial">{companyInitial}</span>
                )}
              </div>
              <div className="company-details">
                <span className="company-name">{job.company_name || 'N/A'}</span>
                {(job.rating || job.reviews) && (
                  <div className="job-rating-section">
                    {job.rating && (
                      <span className="rating">
                        <span className="star">★</span>
                        {job.rating}
                      </span>
                    )}
                    {job.reviews && (
                      <span className="reviews">
                        {job.reviews}
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="job-details-section">
        {job.experience && (
          <div className="detail-item">
            <span className="detail-icon experience-icon"></span>
            <span className="detail-text">{job.experience}</span>
          </div>
        )}
        {job.salary && (
          <div className="detail-item">
            <span className="detail-icon salary-icon"></span>
            <span className="detail-text">{job.salary}</span>
          </div>
        )}
        {job.location && (
          <div className="detail-item">
            <span className="detail-icon location-icon"></span>
            <span className="detail-text">{job.location}</span>
          </div>
        )}
      </div>

      {job.job_description && (
        <div className="job-description">
          <p>{job.job_description}</p>
        </div>
      )}

      {job.tags && job.tags.length > 0 && (
        <div className="job-tags">
          {job.tags.map((tag, index) => (
            <span key={index} className="tag">
              {tag}
            </span>
          ))}
        </div>
      )}

      <div className="job-card-footer">
        {job.job_post_date && (
          <span className="job-post-date">{job.job_post_date}</span>
        )}
        <button className="apply-button">
          <span className="apply-text">Apply</span>
          <span className="apply-arrow">→</span>
        </button>
      </div>
    </div>
  );
};

export default JobCard;

