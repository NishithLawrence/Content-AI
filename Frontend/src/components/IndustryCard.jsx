import React from 'react';

function IndustryCard({ id, name, icon, description, isSelected, onSelect }) {
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onSelect(id);
    }
  };

  return (
    <div
      className={`industry-card ${isSelected ? 'selected' : ''}`}
      onClick={() => onSelect(id)}
      onKeyDown={handleKeyDown}
      tabIndex={0}
      role="radio"
      aria-checked={isSelected}
      aria-label={`Select industry ${name}`}
    >
      <div className="card-selection-check">
        {isSelected ? '✓' : ''}
      </div>
      <div className="card-icon">{icon}</div>
      <h3 className="card-name">{name}</h3>
      <p className="card-description">{description}</p>
    </div>
  );
}

export default IndustryCard;
