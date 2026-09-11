import React from 'react';
import PlanCard from './PlanCard';

const PLANS = [
  { id: '1-week', duration: '1 Week', postCount: 3 },
  { id: '2-weeks', duration: '2 Weeks', postCount: 6 },
  { id: '1-month', duration: '1 Month', postCount: 12 },
];

function ContentPlanSelector({ selectedDuration, onSelectPlan }) {
  return (
    <section className="section-container">
      <div className="section-header">
        <span className="step-number">Step 2</span>
        <h2 className="section-title">Choose your content plan</h2>
        <p className="section-subtitle">Select your publishing timeframe to calculate post volume.</p>
      </div>

      <div className="cards-grid plan-grid" role="radiogroup" aria-label="Choose your content plan">
        {PLANS.map((plan) => (
          <PlanCard
            key={plan.id}
            id={plan.id}
            duration={plan.duration}
            postCount={plan.postCount}
            isSelected={selectedDuration === plan.duration}
            onSelect={onSelectPlan}
          />
        ))}
      </div>
    </section>
  );
}

export default ContentPlanSelector;
