import React from 'react';

function StrategySummary({ strategy }) {
  if (!strategy) return null;

  return (
    <div className="strategy-summary-card">
      <div className="strategy-header">
        <span className="strategy-icon">🎯</span>
        <h3 className="strategy-title">Content Strategy</h3>
      </div>

      <div className="strategy-grid">
        <div className="strategy-item">
          <span className="strategy-label">Target Audience</span>
          <p className="strategy-value">{strategy.target_audience}</p>
        </div>

        <div className="strategy-item">
          <span className="strategy-label">Brand Tone</span>
          <p className="strategy-value">{strategy.tone}</p>
        </div>

        <div className="strategy-item pillars-item">
          <span className="strategy-label">Content Pillars</span>
          <div className="strategy-pillars-tags">
            {strategy.content_pillars && strategy.content_pillars.map((pillar, idx) => (
              <span key={idx} className="strategy-pillar-chip">
                {pillar}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default StrategySummary;
