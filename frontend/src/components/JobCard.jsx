import React from 'react';
import '../styles/JobCard.css';

const JobCard = ({ job }) => {
  return (
    <div className="job-card">
      <div className="job-card-header">
        <div className="job-title-section">
          <h3 className="job-title">{job.job_title || 'N/A'}</h3>
          <div className="company-info">
            {job.company_logo && (
              <img 
                src={job.company_logo} 
                alt={job.company_name || 'Company logo'}
                className="company-logo"
                onError={(e) => {
                  e.target.style.display = 'none';
                }}
              />
            )}
            <span className="company-name">{job.company_name || 'N/A'}</span>
          </div>
        </div>
      </div>

      {(job.rating || job.reviews) && (
        <div className="job-rating-section">
          {job.rating && (
            <span className="rating">
              ⭐ {job.rating}
            </span>
          )}
          {job.reviews && (
            <span className="reviews">
              ({job.reviews})
            </span>
          )}
        </div>
      )}

      <div className="job-details-section">
        {job.experience && (
          <div className="detail-item">
            <span className="detail-icon">💼</span>
            <span className="detail-text">{job.experience}</span>
          </div>
        )}
        {job.salary && (
          <div className="detail-item">
            <span className="detail-icon">💰</span>
            <span className="detail-text">{job.salary}</span>
          </div>
        )}
        {job.location && (
          <div className="detail-item">
            <span className="detail-icon">📍</span>
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

      {job.job_post_date && (
        <div className="job-post-date">
          <span>Posted: {job.job_post_date}</span>
        </div>
      )}
    </div>
  );
};

export default JobCard;

