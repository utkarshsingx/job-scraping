import React, { useState } from 'react';
import '../styles/SearchForm.css';

const SearchForm = ({ onSearch, loading }) => {
  const [formData, setFormData] = useState({
    job_type: 'job',
    keyword: '',
    location: '',
    experience: '',
  });

  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: '',
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.keyword.trim()) {
      newErrors.keyword = 'Keyword is required';
    }

    if (!formData.location.trim()) {
      newErrors.location = 'Location is required';
    }

    if (formData.experience === '' || formData.experience < 0) {
      newErrors.experience = 'Experience is required (0 or more years)';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    onSearch({
      job_type: formData.job_type,
      keyword: formData.keyword.trim(),
      location: formData.location.trim(),
      experience: parseInt(formData.experience, 10),
    });
  };

  return (
    <div className="search-form-container">
      <form onSubmit={handleSubmit} className="search-form">
        <div className="form-group">
          <label htmlFor="job_type">Job Type</label>
          <select
            id="job_type"
            name="job_type"
            value={formData.job_type}
            onChange={handleChange}
            className="form-control"
            disabled={loading}
          >
            <option value="job">Job</option>
            <option value="internship">Internship</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="keyword">Keyword</label>
          <input
            type="text"
            id="keyword"
            name="keyword"
            value={formData.keyword}
            onChange={handleChange}
            placeholder="e.g., web development, python developer"
            className={`form-control ${errors.keyword ? 'error' : ''}`}
            disabled={loading}
          />
          {errors.keyword && <span className="error-text">{errors.keyword}</span>}
        </div>

        <div className="form-group">
          <label htmlFor="location">Location</label>
          <input
            type="text"
            id="location"
            name="location"
            value={formData.location}
            onChange={handleChange}
            placeholder="e.g., india, bangalore, mumbai"
            className={`form-control ${errors.location ? 'error' : ''}`}
            disabled={loading}
          />
          {errors.location && <span className="error-text">{errors.location}</span>}
        </div>

        <div className="form-group">
          <label htmlFor="experience">Experience (Years)</label>
          <input
            type="number"
            id="experience"
            name="experience"
            value={formData.experience}
            onChange={handleChange}
            placeholder="e.g., 1, 2, 3"
            min="0"
            className={`form-control ${errors.experience ? 'error' : ''}`}
            disabled={loading}
          />
          {errors.experience && <span className="error-text">{errors.experience}</span>}
        </div>

        <button
          type="submit"
          className="submit-button"
          disabled={loading}
        >
          {loading ? 'Searching...' : 'Search Jobs'}
        </button>
      </form>
    </div>
  );
};

export default SearchForm;

