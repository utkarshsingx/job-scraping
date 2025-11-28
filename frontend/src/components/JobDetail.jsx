import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { getJobDetails } from '../services/api';
import RelatedJobs from './RelatedJobs';
import '../styles/JobDetail.css';

const JobDetail = () => {
  const { jobUrl } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [jobDetails, setJobDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [relatedJobs, setRelatedJobs] = useState([]);
  const [searchState, setSearchState] = useState(null);

  // Get related jobs from location state or sessionStorage
  useEffect(() => {
    // First try location state (most recent)
    if (location.state && location.state.restoreState) {
      const restoredState = location.state.restoreState;
      setRelatedJobs(restoredState.jobs || []);
      setSearchState(restoredState);
      return;
    }

    // Otherwise try sessionStorage
    try {
      const savedState = sessionStorage.getItem('jobSearchState');
      if (savedState) {
        const parsedState = JSON.parse(savedState);
        setRelatedJobs(parsedState.jobs || []);
        setSearchState(parsedState);
      }
    } catch (err) {
      console.error('Error loading related jobs from sessionStorage:', err);
    }
  }, [location]);

  const handleBack = () => {
    // If we have restore state, navigate to home with it
    if (location.state && location.state.restoreState) {
      navigate('/', { state: { restoreState: location.state.restoreState } });
    } else {
      navigate(-1);
    }
  };

  useEffect(() => {
    const fetchJobDetails = async () => {
      if (!jobUrl) {
        setError('Job URL is missing');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const decodedUrl = decodeURIComponent(jobUrl);
        const data = await getJobDetails(decodedUrl);
        
        if (data.success) {
          setJobDetails(data.job_details);
        } else {
          setError(data.message || data.error || 'Failed to load job details');
        }
      } catch (err) {
        setError(err.message || 'Failed to connect to the server. Please make sure the backend is running.');
      } finally {
        setLoading(false);
      }
    };

    fetchJobDetails();
  }, [jobUrl]);

  if (loading) {
    return (
      <div className="job-detail-wrapper">
        <div className="job-detail-main-content">
          <div className="job-detail-container">
            <div className="loading-container">
              <div className="spinner"></div>
              <p>Loading job details...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="job-detail-wrapper">
        <div className="job-detail-main-content">
          <div className="job-detail-container">
            <div className="error-message">
              <p>{error}</p>
              <button className="back-button" onClick={handleBack}>
                ← Go Back
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!jobDetails) {
    return (
      <div className="job-detail-wrapper">
        <div className="job-detail-main-content">
          <div className="job-detail-container">
            <div className="error-message">
              <p>No job details found</p>
              <button className="back-button" onClick={handleBack}>
                ← Go Back
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const decodedJobUrl = jobUrl ? decodeURIComponent(jobUrl) : null;

  return (
    <div className="job-detail-wrapper">
      <div className="job-detail-main-content">
        <div className="job-detail-container">
          <button className="back-button" onClick={handleBack}>
            ← Back to Jobs
          </button>

          <div className="job-detail-header">
        <div className="job-detail-header-content">
          {jobDetails.company_logo && (
            <div className="company-logo-large">
              <img 
                src={jobDetails.company_logo} 
                alt={jobDetails.company_title || 'Company logo'}
                onError={(e) => {
                  e.target.style.display = 'none';
                }}
              />
            </div>
          )}
          <div className="job-detail-title-section">
            <h1 className="job-detail-title">{jobDetails.header_title || 'Job Title'}</h1>
            <div className="company-info-header">
              {jobDetails.company_title && (
                <span className="company-title">{jobDetails.company_title}</span>
              )}
              {(jobDetails.rating || jobDetails.reviews) && (
                <div className="rating-section">
                  {jobDetails.rating && (
                    <span className="rating">
                      <span className="star">★</span>
                      {jobDetails.rating}
                    </span>
                  )}
                  {jobDetails.reviews && (
                    <span className="reviews">{jobDetails.reviews}</span>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
        
        <div className="job-detail-meta">
          {jobDetails.experience && (
            <div className="meta-item">
              <span className="detail-icon experience-icon"></span>
              <span className="meta-value">{jobDetails.experience}</span>
            </div>
          )}
          {jobDetails.salary && (
            <div className="meta-item">
              <span className="detail-icon salary-icon"></span>
              <span className="meta-value">{jobDetails.salary}</span>
            </div>
          )}
          {jobDetails.location && (
            <div className="meta-item">
              <span className="detail-icon location-icon"></span>
              <span className="meta-value">{jobDetails.location}</span>
            </div>
          )}
        </div>

        <div className="job-detail-stats">
          {jobDetails.posted && (
            <span className="stat-item">Posted: {jobDetails.posted}</span>
          )}
          {jobDetails.openings && (
            <span className="stat-item">Openings: {jobDetails.openings}</span>
          )}
          {jobDetails.applicants && (
            <span className="stat-item">Applicants: {jobDetails.applicants}</span>
          )}
        </div>

        {jobDetails.internship_label && (
          <div className="internship-badge">{jobDetails.internship_label}</div>
        )}

        {jobDetails.job_match_score && (
          <div className="job-match-score">
            {jobDetails.job_match_score}
          </div>
        )}

        {jobDetails.apply_button_text && (
          <button className="apply-button-large">
            {jobDetails.apply_button_text}
          </button>
        )}
      </div>

      {jobDetails.job_highlights && (jobDetails.job_highlights.title || (jobDetails.job_highlights.items && jobDetails.job_highlights.items.length > 0)) && (
        <div className="job-detail-section">
          <h2 className="section-title">
            {jobDetails.job_highlights.title || 'Job Highlights'}
          </h2>
          {jobDetails.job_highlights.items && jobDetails.job_highlights.items.length > 0 && (
            <ul className="job-highlights-list">
              {jobDetails.job_highlights.items.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          )}
        </div>
      )}

      {jobDetails.job_description_content && (
        <div className="job-detail-section">
          <h2 className="section-title">
            {jobDetails.job_description_header || 'Job Description'}
          </h2>
          <div className="job-description-content">
            {jobDetails.job_description_content.split('\n').map((paragraph, index) => (
              paragraph.trim() && (
                <p key={index}>{paragraph.trim()}</p>
              )
            ))}
          </div>
        </div>
      )}

      {jobDetails.job_description_div && !jobDetails.job_description_content && (
        <div className="job-detail-section">
          <h2 className="section-title">
            {jobDetails.job_description_header || 'Job Description'}
          </h2>
          <div className="job-description-content">
            {jobDetails.job_description_div.split('\n').map((paragraph, index) => (
              paragraph.trim() && (
                <p key={index}>{paragraph.trim()}</p>
              )
            ))}
          </div>
        </div>
      )}

      {jobDetails.role_and_responsibilities && (jobDetails.role_and_responsibilities.title || (jobDetails.role_and_responsibilities.items && jobDetails.role_and_responsibilities.items.length > 0)) && (
        <div className="job-detail-section">
          <h2 className="section-title">
            {jobDetails.role_and_responsibilities.title || 'Role and Responsibilities'}
          </h2>
          {jobDetails.role_and_responsibilities.items && jobDetails.role_and_responsibilities.items.length > 0 && (
            <div className="role-responsibilities-tags">
              {jobDetails.role_and_responsibilities.items.map((item, index) => (
                <React.Fragment key={index}>
                  <span className="responsibility-tag">{item.trim()}</span>
                  {index < jobDetails.role_and_responsibilities.items.length - 1 && (
                    <span className="tag-separator">•</span>
                  )}
                </React.Fragment>
              ))}
            </div>
          )}
        </div>
      )}

      {(jobDetails.role || jobDetails.industry_type || jobDetails.department || 
        jobDetails.employment_type || jobDetails.role_category) && (
        <div className="job-detail-section">
          <h2 className="section-title">Job Details</h2>
          <div className="job-details-grid">
            {jobDetails.role && (
              <div className="detail-row">
                <span className="detail-label">Role:</span>
                <span className="detail-value">{jobDetails.role}</span>
              </div>
            )}
            {jobDetails.industry_type && (
              <div className="detail-row">
                <span className="detail-label">Industry Type:</span>
                <span className="detail-value">{jobDetails.industry_type}</span>
              </div>
            )}
            {jobDetails.department && (
              <div className="detail-row">
                <span className="detail-label">Department:</span>
                <span className="detail-value">{jobDetails.department}</span>
              </div>
            )}
            {jobDetails.employment_type && (
              <div className="detail-row">
                <span className="detail-label">Employment Type:</span>
                <span className="detail-value">{jobDetails.employment_type}</span>
              </div>
            )}
            {jobDetails.role_category && (
              <div className="detail-row">
                <span className="detail-label">Role Category:</span>
                <span className="detail-value">{jobDetails.role_category}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {(jobDetails.ug_education || jobDetails.pg_education) && (
        <div className="job-detail-section">
          <h2 className="section-title">
            {jobDetails.education_title || 'Education'}
          </h2>
          <div className="education-details">
            {jobDetails.ug_education && (
              <div className="education-item">
                <span className="education-type">UG:</span>
                <span className="education-value">{jobDetails.ug_education}</span>
              </div>
            )}
            {jobDetails.pg_education && (
              <div className="education-item">
                <span className="education-type">PG:</span>
                <span className="education-value">{jobDetails.pg_education}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {jobDetails.key_skills && jobDetails.key_skills.length > 0 && (
        <div className="job-detail-section">
          <h2 className="section-title">Key Skills</h2>
          <div className="key-skills">
            {jobDetails.key_skills.map((skill, index) => (
              <React.Fragment key={index}>
                <span className="skill-tag">{skill}</span>
                {index < jobDetails.key_skills.length - 1 && <span className="tag-separator">•</span>}
              </React.Fragment>
            ))}
          </div>
        </div>
      )}

      {(jobDetails.about_company_description || jobDetails.company_info_header || (jobDetails.company_address && (jobDetails.company_address.label || jobDetails.company_address.address))) && (
        <div className="job-detail-section">
          <h2 className="section-title">
            {jobDetails.about_company_header || 'About Company'}
          </h2>
          
          {jobDetails.company_info_header && (
            <div className="company-info-header">
              <h3>{jobDetails.company_info_header}</h3>
            </div>
          )}
          
          {jobDetails.about_company_description && (
            <div className="about-company">
              {jobDetails.about_company_description.split('\n').map((paragraph, index) => (
                paragraph.trim() && (
                  <p key={index}>{paragraph.trim()}</p>
                )
              ))}
            </div>
          )}
          
          {jobDetails.company_address && (jobDetails.company_address.label || jobDetails.company_address.address) && (
            <div className="company-address">
              {jobDetails.company_address.label && (
                <span className="address-label">{jobDetails.company_address.label}: </span>
              )}
              {jobDetails.company_address.address && (
                <span className="address-value">{jobDetails.company_address.address}</span>
              )}
            </div>
          )}
        </div>
      )}
        </div>
      </div>

      {relatedJobs.length > 0 && (
        <div className="job-detail-sidebar">
          <RelatedJobs 
            jobs={relatedJobs} 
            currentJobUrl={decodedJobUrl}
            searchState={searchState}
          />
        </div>
      )}
    </div>
  );
};

export default JobDetail;

