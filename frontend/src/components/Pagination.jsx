import React from 'react';
import '../styles/Pagination.css';

const Pagination = ({ currentPage, hasNext, hasPrevious, onPageChange, loading }) => {
  const handlePrevious = () => {
    if (hasPrevious && !loading) {
      onPageChange(currentPage - 1);
    }
  };

  const handleNext = () => {
    if (hasNext && !loading) {
      onPageChange(currentPage + 1);
    }
  };

  return (
    <div className="pagination">
      <button
        className="pagination-button pagination-prev"
        onClick={handlePrevious}
        disabled={!hasPrevious || loading}
        aria-label="Previous page"
      >
        <span>←</span>
        <span>Previous</span>
      </button>
      
      <div className="pagination-info">
        <span className="pagination-page">Page {currentPage}</span>
      </div>
      
      <button
        className="pagination-button pagination-next"
        onClick={handleNext}
        disabled={!hasNext || loading}
        aria-label="Next page"
      >
        <span>Next</span>
        <span>→</span>
      </button>
    </div>
  );
};

export default Pagination;

