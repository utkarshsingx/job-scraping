import React, { useState, useEffect } from 'react';
import '../styles/FilterSidebar.css';

const FilterSidebar = ({ jobs, selectedTags = [], onFilterChange }) => {
  const [allTags, setAllTags] = useState([]);

  useEffect(() => {
    // Extract all unique tags from jobs
    const tags = new Set();
    jobs.forEach(job => {
      if (job.tags && Array.isArray(job.tags)) {
        job.tags.forEach(tag => {
          if (tag && tag.trim()) {
            tags.add(tag.trim());
          }
        });
      }
    });
    setAllTags(Array.from(tags).sort());
  }, [jobs]);

  const handleTagToggle = (tag) => {
    const newSelected = selectedTags.includes(tag)
      ? selectedTags.filter(t => t !== tag)
      : [...selectedTags, tag];
    
    // Notify parent component
    if (onFilterChange) {
      onFilterChange(newSelected);
    }
  };

  const clearFilters = () => {
    if (onFilterChange) {
      onFilterChange([]);
    }
  };

  if (jobs.length === 0) {
    return null;
  }

  return (
    <div className="filter-sidebar">
      <div className="filter-header">
        <h3>Filter by Skills</h3>
        {selectedTags.length > 0 && (
          <button className="clear-filters" onClick={clearFilters}>
            Clear All
          </button>
        )}
      </div>
      
      <div className="filter-tags">
        {allTags.length === 0 ? (
          <p className="no-tags">No tags available</p>
        ) : (
          allTags.map((tag, index) => (
            <button
              key={index}
              className={`filter-tag ${selectedTags.includes(tag) ? 'active' : ''}`}
              onClick={() => handleTagToggle(tag)}
            >
              {tag}
            </button>
          ))
        )}
      </div>
      
      {selectedTags.length > 0 && (
        <div className="selected-filters">
          <p className="selected-count">
            {selectedTags.length} filter{selectedTags.length !== 1 ? 's' : ''} applied
          </p>
        </div>
      )}
    </div>
  );
};

export default FilterSidebar;

