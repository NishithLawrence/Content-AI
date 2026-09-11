import React from 'react';
import CopyButton from './CopyButton';
import HashtagList from './HashtagList';

function PostCard({ post, onRegeneratePost, isRegenerating }) {
  const formattedPostNumber = String(post.post_number).padStart(2, '0');

  return (
    <div className={`post-card ${isRegenerating ? 'regenerating' : ''}`}>
      {/* Top Header */}
      <div className="post-card-header">
        <div className="post-meta-left">
          <span className="post-badge post-number-badge">POST {formattedPostNumber}</span>
          <span className="post-badge post-day-badge">{post.day}</span>
        </div>
        <div className="post-meta-right">
          <span className="post-pillar-chip">{post.content_pillar}</span>
        </div>
      </div>

      {/* Caption Body */}
      <div className="post-section caption-section">
        <div className="section-header-row">
          <span className="section-label">Caption</span>
          <CopyButton
            textToCopy={post.caption}
            label="Copy Caption"
            copiedLabel="Caption Copied!"
            className="caption-copy-btn"
          />
        </div>
        <p className="caption-text">{post.caption}</p>
      </div>

      {/* Visual Direction */}
      <div className="post-section visual-direction-section">
        <div className="section-label-with-icon">
          <span className="section-icon">🎬</span>
          <span className="section-label">Visual Direction</span>
        </div>
        <p className="visual-direction-text">{post.visual_direction}</p>
      </div>

      {/* Hashtags List */}
      <HashtagList hashtags={post.hashtags} />

      {/* Card Actions Footer */}
      <div className="post-card-footer">
        <CopyButton
          textToCopy={post.caption}
          label="Copy Caption"
          copiedLabel="Caption Copied!"
        />

        <button
          type="button"
          className="action-btn regenerate-btn"
          disabled={isRegenerating}
          onClick={() => onRegeneratePost(post)}
          title="Regenerate this specific post with AI"
        >
          <span className={`btn-icon ${isRegenerating ? 'spin' : ''}`}>
            {isRegenerating ? '⏳' : '🔄'}
          </span>
          <span className="btn-label">
            {isRegenerating ? 'Regenerating Post...' : 'Regenerate'}
          </span>
        </button>
      </div>
    </div>
  );
}

export default PostCard;
