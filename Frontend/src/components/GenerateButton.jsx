import React from 'react';

function GenerateButton({ isFormValid, isGenerating, loadingStage, onGenerate, selectedIndustry, selectedDuration }) {
  const getDisabledReason = () => {
    if (isGenerating) return loadingStage || 'AI is generating your content plan...';
    if (!selectedIndustry && !selectedDuration) return 'Select an industry and content plan to generate';
    if (!selectedIndustry) return 'Select an industry to generate';
    if (!selectedDuration) return 'Select a content plan duration to generate';
    return '';
  };

  return (
    <div className="generate-section">
      <button
        type="button"
        className={`generate-cta-button ${isGenerating ? 'loading' : ''}`}
        disabled={!isFormValid || isGenerating}
        onClick={onGenerate}
        title={!isFormValid || isGenerating ? getDisabledReason() : 'Generate social media content plan'}
      >
        {isGenerating ? (
          <>
            <span className="btn-spinner" aria-hidden="true">⏳</span>
            <span className="btn-text">{loadingStage || 'Generating Content Plan...'}</span>
          </>
        ) : (
          <>
            <span className="btn-sparkle">✨</span>
            <span className="btn-text">Generate Content</span>
          </>
        )}
      </button>

      {(!isFormValid || isGenerating) && (
        <p className="generate-hint">
          {getDisabledReason()}
        </p>
      )}
    </div>
  );
}

export default GenerateButton;
