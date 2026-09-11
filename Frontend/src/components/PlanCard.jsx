import React from 'react';

function PlanCard({ id, duration, postCount, isSelected, onSelect }) {
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onSelect(duration, postCount);
    }
  };

  return (
    <div
      className={`plan-card ${isSelected ? 'selected' : ''}`}
      onClick={() => onSelect(duration, postCount)}
      onKeyDown={handleKeyDown}
      tabIndex={0}
      role="radio"
      aria-checked={isSelected}
      aria-label={`Select plan ${duration} with ${postCount} posts`}
    >
      <div className="card-selection-check">
        {isSelected ? '✓' : ''}
      </div>
      <div className="plan-duration">{duration}</div>
      <div className="plan-posts-count">
        <span className="count-number">{postCount}</span>
        <span className="count-label">Posts</span>
      </div>
    </div>
  );
}

export default PlanCard;
