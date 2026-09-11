import React from 'react';
import IndustryCard from './IndustryCard';

const INDUSTRIES = [
  {
    id: 'Real Estate',
    name: 'Real Estate',
    icon: '🏠',
    description: 'Properties, lifestyle, investment & architecture'
  },
  {
    id: 'Jewellery',
    name: 'Jewellery',
    icon: '💎',
    description: 'Craftsmanship, luxury, occasions & gifting'
  },
  {
    id: 'Perfume',
    name: 'Perfume',
    icon: '🌸',
    description: 'Fragrance, mood, personality & sensory storytelling'
  },
  {
    id: 'FMCG / Food',
    name: 'FMCG / Food',
    icon: '🍔',
    description: 'Taste, ingredients, convenience & everyday moments'
  }
];

function IndustrySelector({ selectedIndustry, onSelectIndustry }) {
  return (
    <section className="section-container">
      <div className="section-header">
        <span className="step-number">Step 1</span>
        <h2 className="section-title">Choose your industry</h2>
        <p className="section-subtitle">Your content strategy will adapt to the selected industry.</p>
      </div>

      <div className="cards-grid industry-grid" role="radiogroup" aria-label="Choose your industry">
        {INDUSTRIES.map((item) => (
          <IndustryCard
            key={item.id}
            id={item.id}
            name={item.name}
            icon={item.icon}
            description={item.description}
            isSelected={selectedIndustry === item.id}
            onSelect={onSelectIndustry}
          />
        ))}
      </div>
    </section>
  );
}

export default IndustrySelector;
