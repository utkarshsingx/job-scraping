import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { HiOutlineCurrencyRupee, HiOutlineBriefcase, HiOutlineLocationMarker } from 'react-icons/hi';
import { getJobDetails } from '../services/api';
import RelatedJobs from './RelatedJobs';
import '../styles/JobDetail.css';

const DETAIL_LOADING_STEPS = [
  'Connecting securely to the job details page',
  'Fetching core information from Naukri',
  'Parsing salary, experience and location',
  'Loading description and key skills',
  'Preparing company and culture insights',
  'Polishing everything for a clean view'
];

const DETAIL_FUN_FACTS = [
  'Fun fact: Many candidates discover new roles while exploring job details.',
  'Fun fact: Clear job descriptions can increase applications by over 30%.',
  'Fun fact: Candidates spend more time reading benefits than responsibilities.',
  'Fun fact: Company culture sections are among the most-read parts of a job ad.',
  'Fun fact: Roles with clear growth paths attract significantly more applicants.'
];

const JobDetail = () => {
  const { jobUrl } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [jobDetails, setJobDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [relatedJobs, setRelatedJobs] = useState([]);
  const [searchState, setSearchState] = useState(null);
  const [loadingStepIndex, setLoadingStepIndex] = useState(0);
  const [loadingFunFact, setLoadingFunFact] = useState('');

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

  useEffect(() => {
    let intervalId;
    if (loading) {
      setLoadingStepIndex(0);
      const randomFact =
        DETAIL_FUN_FACTS[Math.floor(Math.random() * DETAIL_FUN_FACTS.length)];
      setLoadingFunFact(randomFact);

      intervalId = setInterval(() => {
        setLoadingStepIndex((prev) =>
          prev < DETAIL_LOADING_STEPS.length - 1 ? prev + 1 : prev
        );
      }, 800);
    } else {
      setLoadingStepIndex(0);
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [loading]);

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
          console.log('[JobDetail] Received job details:', data.job_details);
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
    const percent = Math.min(
      100,
      Math.round(
        ((loadingStepIndex + 1) / DETAIL_LOADING_STEPS.length) * 100
      )
    );

    return (
      <div className="job-detail-wrapper">
        <div className="job-detail-main-content">
          <div className="job-detail-container">
            <div className="job-detail-skeleton">
              <div className="detail-loading-header">
                <div className="detail-loading-left">
                  <div className="detail-loading-icon" />
                  <div className="detail-loading-meta">
                    <span className="detail-loading-label">Opening job details</span>
                    <span className="detail-loading-step">
                      Step {loadingStepIndex + 1} of {DETAIL_LOADING_STEPS.length}
                    </span>
                  </div>
                </div>
                <span className="detail-loading-percent">{percent}%</span>
              </div>
              <p className="detail-loading-main">
                {DETAIL_LOADING_STEPS[loadingStepIndex]}
              </p>
              <div className="detail-loading-bar">
                <div
                  className="detail-loading-bar-fill"
                  style={{ width: `${percent}%` }}
                />
              </div>
              <div className="detail-loading-steps-dots">
                {DETAIL_LOADING_STEPS.map((_, index) => (
                  <span
                    key={index}
                    className={
                      index <= loadingStepIndex
                        ? 'detail-loading-step-dot active'
                        : 'detail-loading-step-dot'
                    }
                  />
                ))}
              </div>
              {loadingFunFact && (
                <p className="detail-loading-fun-fact">
                  <span className="label">Did you know?</span> {loadingFunFact}
                </p>
              )}
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

  // Debug: Log what we have
  if (jobDetails) {
    console.log('[JobDetail] Rendering with data:', {
      hasHeaderTitle: !!jobDetails.header_title,
      hasCompanyTitle: !!jobDetails.company_title,
      hasCompanyLogo: !!jobDetails.company_logo,
      hasRating: !!jobDetails.rating,
      hasReviews: !!jobDetails.reviews,
      hasExperience: !!jobDetails.experience,
      hasSalary: !!jobDetails.salary,
      hasLocation: !!jobDetails.location,
      hasDescription: !!jobDetails.job_description_content,
      hasSkills: !!jobDetails.key_skills && jobDetails.key_skills.length > 0,
      allKeys: Object.keys(jobDetails)
    });
  }

  return (
    <div className="job-detail-wrapper">
      <div className="job-detail-main-content">
        <div className="job-detail-container">
          <button className="back-button" onClick={handleBack}>
            ← Back to Jobs
          </button>

          {jobDetails && (
            <div className="job-detail-header">
              <div className="job-detail-header-content">
                <div 
                  className={`company-logo-wrapper ${!jobDetails.company_logo ? 'no-logo' : ''}`}
                  data-initial={jobDetails.company_title ? (jobDetails.company_title.split(/\s+/).length >= 2 
                    ? (jobDetails.company_title.split(/\s+/)[0][0] + jobDetails.company_title.split(/\s+/)[1][0]).toUpperCase()
                    : jobDetails.company_title[0].toUpperCase()) : '?'}
                >
                  {jobDetails.company_logo ? (
                    <img 
                      src={jobDetails.company_logo} 
                      alt={jobDetails.company_title || 'Company logo'}
                      className="company-logo"
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.parentElement.classList.add('no-logo');
                      }}
                    />
                  ) : (
                    <span className="company-initial">
                      {jobDetails.company_title ? (jobDetails.company_title.split(/\s+/).length >= 2 
                        ? (jobDetails.company_title.split(/\s+/)[0][0] + jobDetails.company_title.split(/\s+/)[1][0]).toUpperCase()
                        : jobDetails.company_title[0].toUpperCase()) : '?'}
                    </span>
                  )}
                </div>
                <div className="job-title-section">
                  <h1 className="job-detail-title">{jobDetails.header_title || 'Job Title'}</h1>
                  <div className="company-details">
                    {jobDetails.company_title && (
                      <span className="company-name">{jobDetails.company_title}</span>
                    )}
                    {(jobDetails.rating || jobDetails.reviews) && (
                      <div className="job-rating-section">
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
                {jobDetails.apply_button_text && (
                  <button 
                    className="apply-button"
                    onClick={() => {
                      if (decodedJobUrl) {
                        window.open(decodedJobUrl, '_blank');
                      }
                    }}
                  >
                    <span className="apply-text">{jobDetails.apply_button_text}</span>
                    <span className="apply-arrow">→</span>
                  </button>
                )}
              </div>
            
            <div className="job-details-section">
              {jobDetails.experience && (
                <div className="detail-item">
                  <HiOutlineBriefcase className="detail-icon experience-icon" />
                  <span className="detail-text">{jobDetails.experience}</span>
                </div>
              )}
              {jobDetails.salary && (
                <div className="detail-item">
                  <HiOutlineCurrencyRupee className="detail-icon salary-icon" />
                  <span className="detail-text">{jobDetails.salary}</span>
                </div>
              )}
              {jobDetails.location && (
                <div className="detail-item">
                  <HiOutlineLocationMarker className="detail-icon location-icon" />
                  <span className="detail-text">{jobDetails.location}</span>
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

            <div className="job-detail-badges">
              {jobDetails.internship_label && (
                <div className="internship-badge">{jobDetails.internship_label}</div>
              )}
              {jobDetails.job_match_score && (
                <div className="job-match-score">
                  {jobDetails.job_match_score}
                </div>
              )}
            </div>
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
            {jobDetails.role && jobDetails.role.trim() && !jobDetails.role.toLowerCase().includes('industry type') && (
              <div className="detail-row">
                <span className="detail-label">Role</span>
                <span className="detail-value">{jobDetails.role.replace(/^role:/i, '').replace(/^role/i, '').trim().replace(/,$/, '').trim()}</span>
              </div>
            )}
            {jobDetails.industry_type && jobDetails.industry_type.trim() && (
              <div className="detail-row">
                <span className="detail-label">Industry Type</span>
                <span className="detail-value">{jobDetails.industry_type.replace(/^industry type:/i, '').replace(/^industry type/i, '').trim().replace(/,$/, '').trim()}</span>
              </div>
            )}
            {jobDetails.department && jobDetails.department.trim() && (
              <div className="detail-row">
                <span className="detail-label">Department</span>
                <span className="detail-value">{jobDetails.department.replace(/^department:/i, '').replace(/^department/i, '').trim().replace(/,$/, '').trim()}</span>
              </div>
            )}
            {jobDetails.employment_type && jobDetails.employment_type.trim() && (
              <div className="detail-row">
                <span className="detail-label">Employment Type</span>
                <span className="detail-value">{jobDetails.employment_type.replace(/^employment type:/i, '').replace(/^employment type/i, '').trim().replace(/,$/, '').trim()}</span>
              </div>
            )}
            {jobDetails.role_category && jobDetails.role_category.trim() && (
              <div className="detail-row">
                <span className="detail-label">Role Category</span>
                <span className="detail-value">{jobDetails.role_category.replace(/^role category:/i, '').replace(/^role category/i, '').trim().replace(/,$/, '').trim()}</span>
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
            {jobDetails.ug_education && !jobDetails.ug_education.toLowerCase().includes('key skills') && (
              <div className="education-item">
                <span className="education-type">UG</span>
                <span className="education-value">{jobDetails.ug_education.replace(/^ug:/i, '').trim()}</span>
              </div>
            )}
            {jobDetails.pg_education && !jobDetails.pg_education.toLowerCase().includes('key skills') && (
              <div className="education-item">
                <span className="education-type">PG</span>
                <span className="education-value">{jobDetails.pg_education.replace(/^pg:/i, '').trim()}</span>
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
              <span key={index} className="skill-tag">{skill.trim()}</span>
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

