import React, { useMemo } from 'react';
import '../styles/FilterSidebar.css';

const FilterSidebar = ({ jobs, filters = {}, onFilterChange }) => {
  // Extract unique values for each filter category
  const filterOptions = useMemo(() => {
    const departments = new Set();
    const roleCategories = new Set();
    const stipends = new Set();
    const workModes = new Set();
    const durations = new Set();
    const locations = new Set();

    jobs.forEach(job => {
      // Extract department from job title or tags
      if (job.job_title) {
        const title = job.job_title.toLowerCase();
        if (title.includes('engineering') || title.includes('developer') || title.includes('software')) {
          departments.add('Engineering');
        } else if (title.includes('marketing') || title.includes('digital')) {
          departments.add('Marketing');
        } else if (title.includes('sales') || title.includes('business')) {
          departments.add('Sales');
        } else if (title.includes('design') || title.includes('ui') || title.includes('ux')) {
          departments.add('Design');
        } else if (title.includes('data') || title.includes('analyst') || title.includes('science')) {
          departments.add('Data & Analytics');
        } else if (title.includes('hr') || title.includes('human')) {
          departments.add('HR');
        } else if (title.includes('finance') || title.includes('accounting')) {
          departments.add('Finance');
        } else if (title.includes('operations') || title.includes('ops')) {
          departments.add('Operations');
        }
      }

      // Extract role category from tags or job title
      if (job.tags && Array.isArray(job.tags)) {
        job.tags.forEach(tag => {
          const tagLower = tag.toLowerCase();
          if (tagLower.includes('frontend') || tagLower.includes('react') || tagLower.includes('angular') || tagLower.includes('vue')) {
            roleCategories.add('Frontend');
          } else if (tagLower.includes('backend') || tagLower.includes('node') || tagLower.includes('python') || tagLower.includes('java')) {
            roleCategories.add('Backend');
          } else if (tagLower.includes('full') || tagLower.includes('stack')) {
            roleCategories.add('Full Stack');
          } else if (tagLower.includes('mobile') || tagLower.includes('android') || tagLower.includes('ios')) {
            roleCategories.add('Mobile');
          } else if (tagLower.includes('devops') || tagLower.includes('cloud') || tagLower.includes('aws')) {
            roleCategories.add('DevOps');
          } else if (tagLower.includes('data') || tagLower.includes('machine') || tagLower.includes('ai')) {
            roleCategories.add('Data Science');
          }
        });
      }

      // Extract stipend from salary field
      if (job.salary) {
        const salary = job.salary.toLowerCase();
        if (salary.includes('unpaid') || salary.includes('no stipend') || salary === 'not disclosed') {
          stipends.add('Unpaid');
        } else {
          // Try to extract numeric values
          const match = salary.match(/(\d+)\s*k|(\d+)\s*thousand/i);
          if (match) {
            const amount = parseInt(match[1] || match[2]);
            if (amount >= 0 && amount < 10) {
              stipends.add('0-10k');
            } else if (amount >= 10 && amount < 20) {
              stipends.add('10k-20k');
            } else if (amount >= 20 && amount < 30) {
              stipends.add('20k-30k');
            } else if (amount >= 30) {
              stipends.add('30k+');
            }
          } else {
            // Default categorization
            if (salary.includes('lakh') || salary.includes('lpa')) {
              // Converted to monthly for internships
              stipends.add('10k-20k');
            } else {
              stipends.add('0-10k');
            }
          }
        }
      }

      // Extract work mode from location or job description
      if (job.location) {
        const location = job.location.toLowerCase();
        if (location.includes('remote') || location.includes('work from home') || location.includes('wfh')) {
          workModes.add('Remote');
        } else {
          workModes.add('On-site');
        }
      }
      if (job.job_description) {
        const desc = job.job_description.toLowerCase();
        if (desc.includes('remote') || desc.includes('work from home') || desc.includes('wfh')) {
          workModes.add('Remote');
        }
        if (desc.includes('hybrid')) {
          workModes.add('Hybrid');
        }
      }

      // Extract duration from job description or title
      if (job.job_description) {
        const desc = job.job_description.toLowerCase();
        if (desc.match(/\b3\s*month/i) || desc.match(/three\s*month/i)) {
          durations.add('3 months');
        } else if (desc.match(/\b6\s*month/i) || desc.match(/six\s*month/i)) {
          durations.add('6 months');
        } else if (desc.match(/\b12\s*month/i) || desc.match(/one\s*year/i) || desc.match(/1\s*year/i)) {
          durations.add('12 months');
        }
      }

      // Extract location
      if (job.location) {
        const locationParts = job.location.split(',').map(loc => loc.trim()).filter(loc => loc);
        locationParts.forEach(loc => {
          if (loc && !loc.toLowerCase().includes('remote') && !loc.toLowerCase().includes('work from home')) {
            locations.add(loc);
          }
        });
      }
    });

    return {
      departments: Array.from(departments).sort(),
      roleCategories: Array.from(roleCategories).sort(),
      stipends: Array.from(stipends).length > 0 ? Array.from(stipends).sort() : ['0-10k', '10k-20k', '20k-30k', '30k+', 'Unpaid'],
      workModes: Array.from(workModes).length > 0 ? Array.from(workModes).sort() : ['Remote', 'On-site', 'Hybrid'],
      durations: Array.from(durations).length > 0 ? Array.from(durations).sort() : ['3 months', '6 months', '12 months'],
      locations: Array.from(locations).sort()
    };
  }, [jobs]);

  const handleFilterToggle = (category, value) => {
    const currentFilters = { ...filters };
    if (!currentFilters[category]) {
      currentFilters[category] = [];
    }
    
    const categoryFilters = [...currentFilters[category]];
    const index = categoryFilters.indexOf(value);
    
    if (index > -1) {
      categoryFilters.splice(index, 1);
    } else {
      categoryFilters.push(value);
    }
    
    currentFilters[category] = categoryFilters;
    
    if (onFilterChange) {
      onFilterChange(currentFilters);
    }
  };

  const clearFilters = () => {
    if (onFilterChange) {
      onFilterChange({});
    }
  };

  const getTotalActiveFilters = () => {
    return Object.values(filters || {}).reduce((sum, arr) => sum + (arr?.length || 0), 0);
  };

  if (jobs.length === 0) {
    return null;
  }

  const totalActive = getTotalActiveFilters();

  return (
    <div className="filter-sidebar">
      <div className="filter-header">
        <h3>All Filters</h3>
        {totalActive > 0 && (
          <button className="clear-filters" onClick={clearFilters}>
            Clear All
          </button>
        )}
      </div>
      
      <div className="filter-sections">
        {/* Department Filter */}
        <div className="filter-section">
          <h4 className="filter-section-title">Department</h4>
          <div className="filter-checkboxes">
            {filterOptions.departments.length > 0 ? (
              filterOptions.departments.map((dept, index) => (
                <label key={index} className="filter-checkbox">
                  <input
                    type="checkbox"
                    checked={(filters.department || []).includes(dept)}
                    onChange={() => handleFilterToggle('department', dept)}
                  />
                  <span className="checkbox-label">{dept}</span>
                </label>
              ))
            ) : (
              <p className="no-options">No departments available</p>
            )}
          </div>
        </div>

        {/* Role Category Filter */}
        <div className="filter-section">
          <h4 className="filter-section-title">Role Category</h4>
          <div className="filter-checkboxes">
            {filterOptions.roleCategories.length > 0 ? (
              filterOptions.roleCategories.map((role, index) => (
                <label key={index} className="filter-checkbox">
                  <input
                    type="checkbox"
                    checked={(filters.roleCategory || []).includes(role)}
                    onChange={() => handleFilterToggle('roleCategory', role)}
                  />
                  <span className="checkbox-label">{role}</span>
                </label>
              ))
            ) : (
              <p className="no-options">No role categories available</p>
            )}
          </div>
        </div>

        {/* Stipend Filter */}
        <div className="filter-section">
          <h4 className="filter-section-title">Stipend</h4>
          <div className="filter-checkboxes">
            {filterOptions.stipends.map((stipend, index) => (
              <label key={index} className="filter-checkbox">
                <input
                  type="checkbox"
                  checked={(filters.stipend || []).includes(stipend)}
                  onChange={() => handleFilterToggle('stipend', stipend)}
                />
                <span className="checkbox-label">{stipend}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Work Mode Filter */}
        <div className="filter-section">
          <h4 className="filter-section-title">Work Mode</h4>
          <div className="filter-checkboxes">
            {filterOptions.workModes.map((mode, index) => (
              <label key={index} className="filter-checkbox">
                <input
                  type="checkbox"
                  checked={(filters.workMode || []).includes(mode)}
                  onChange={() => handleFilterToggle('workMode', mode)}
                />
                <span className="checkbox-label">{mode}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Duration Filter */}
        <div className="filter-section">
          <h4 className="filter-section-title">Duration</h4>
          <div className="filter-checkboxes">
            {filterOptions.durations.map((duration, index) => (
              <label key={index} className="filter-checkbox">
                <input
                  type="checkbox"
                  checked={(filters.duration || []).includes(duration)}
                  onChange={() => handleFilterToggle('duration', duration)}
                />
                <span className="checkbox-label">{duration}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Location Filter */}
        <div className="filter-section">
          <h4 className="filter-section-title">Location</h4>
          <div className="filter-checkboxes">
            {filterOptions.locations.length > 0 ? (
              filterOptions.locations.slice(0, 20).map((location, index) => (
                <label key={index} className="filter-checkbox">
                  <input
                    type="checkbox"
                    checked={(filters.location || []).includes(location)}
                    onChange={() => handleFilterToggle('location', location)}
                  />
                  <span className="checkbox-label">{location}</span>
                </label>
          ))
            ) : (
              <p className="no-options">No locations available</p>
            )}
          </div>
        </div>
      </div>
      
      {totalActive > 0 && (
        <div className="selected-filters">
          <p className="selected-count">
            {totalActive} filter{totalActive !== 1 ? 's' : ''} applied
          </p>
        </div>
      )}
    </div>
  );
};

export default FilterSidebar;
