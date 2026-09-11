import React from 'react';

const PLATFORMS = [
  { id: 'Instagram', label: 'Instagram', icon: '📸' },
  { id: 'LinkedIn', label: 'LinkedIn', icon: '💼' },
  { id: 'Facebook', label: 'Facebook', icon: '👥' },
];

function PlatformSelector({ selectedPlatform, onSelectPlatform }) {
  return (
    <section className="section-container">
      <div className="section-header">
        <span className="step-number">Step 3</span>
        <h2 className="section-title">Select content format</h2>
        <p className="section-subtitle">Tailor post structure and tone for your primary channel.</p>
      </div>

      <div className="platform-options" role="radiogroup" aria-label="Select target platform">
        {PLATFORMS.map((platform) => (
          <button
            key={platform.id}
            type="button"
            className={`platform-btn ${selectedPlatform === platform.id ? 'selected' : ''}`}
            onClick={() => onSelectPlatform(platform.id)}
            role="radio"
            aria-checked={selectedPlatform === platform.id}
          >
            <span className="platform-icon">{platform.icon}</span>
            <span className="platform-label">{platform.label}</span>
          </button>
        ))}
      </div>
    </section>
  );
}

export default PlatformSelector;
