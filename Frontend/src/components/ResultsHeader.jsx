import React from 'react';
import CopyButton from './CopyButton';

function ResultsHeader({
  generatedContent,
  referenceFileCount = 0,
  onEditInputs,
  onResetPlan,
  onExportCSV
}) {
  const { industry, duration, platform, total_posts, posts, content_strategy } = generatedContent;

  const buildFullPlanText = () => {
    let text = `=========================================\n`;
    text += `AI CONTENT PLAN: ${industry.toUpperCase()}\n`;
    text += `=========================================\n`;
    text += `Duration: ${duration} (${total_posts} Posts)\n`;
    text += `Platform: ${platform}\n`;
    if (referenceFileCount > 0) {
      text += `Reference Files: ${referenceFileCount} file(s) attached\n`;
    }
    text += `\nCONTENT STRATEGY:\n`;
    text += `- Target Audience: ${content_strategy.target_audience}\n`;
    text += `- Brand Tone: ${content_strategy.tone}\n`;
    text += `- Content Pillars: ${content_strategy.content_pillars.join(', ')}\n`;
    text += `\n=========================================\n`;

    posts.forEach((post) => {
      text += `\n[POST ${String(post.post_number).padStart(2, '0')} - ${post.day.toUpperCase()}]\n`;
      text += `Pillar: ${post.content_pillar}\n`;
      text += `\nCAPTION:\n${post.caption}\n`;
      text += `\nVISUAL DIRECTION:\n${post.visual_direction}\n`;
      text += `\nHASHTAGS:\n${post.hashtags.join(' ')}\n`;
      text += `-----------------------------------------\n`;
    });

    return text;
  };

  return (
    <div className="results-header-container">
      {/* Top Bar Navigation & Actions */}
      <div className="results-top-nav">
        <button
          type="button"
          className="nav-btn edit-inputs-btn"
          onClick={onEditInputs}
          title="Back to generator screen while keeping your selections"
        >
          ← Edit Inputs
        </button>

        <div className="results-nav-actions">
          <button
            type="button"
            className="nav-btn reset-plan-btn"
            onClick={onResetPlan}
            title="Start a new content plan"
          >
            🔄 New Plan
          </button>

          <CopyButton
            textToCopy={buildFullPlanText()}
            label="Copy All"
            copiedLabel="All Copied!"
            className="nav-copy-all-btn"
          />

          <button
            type="button"
            className="nav-btn export-csv-btn"
            onClick={onExportCSV}
            title="Export complete plan as CSV spreadsheet"
          >
            📥 Export CSV
          </button>
        </div>
      </div>

      {/* Main Title & Subtitle */}
      <div className="results-title-section">
        <h2 className="results-main-title">Your Content Plan</h2>
        <p className="results-main-subtitle">Your AI-generated social media content calendar is ready.</p>
      </div>

      {/* Summary Badges */}
      <div className="results-summary-badges">
        <div className="badge-item">
          <span className="badge-label">Industry</span>
          <span className="badge-value industry-badge">{industry}</span>
        </div>

        <div className="badge-item">
          <span className="badge-label">Duration</span>
          <span className="badge-value duration-badge">{duration}</span>
        </div>

        <div className="badge-item">
          <span className="badge-label">Posts</span>
          <span className="badge-value posts-badge">{total_posts} Posts</span>
        </div>

        <div className="badge-item">
          <span className="badge-label">Platform</span>
          <span className="badge-value platform-badge">{platform}</span>
        </div>

        {referenceFileCount > 0 && (
          <div className="badge-item">
            <span className="badge-label">Grounding</span>
            <span className="badge-value reference-badge">
              📎 {referenceFileCount} reference {referenceFileCount === 1 ? 'file' : 'files'}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

export default ResultsHeader;
