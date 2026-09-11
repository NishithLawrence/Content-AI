import React from 'react';
import CopyButton from './CopyButton';

function HashtagList({ hashtags = [] }) {
  if (!hashtags || hashtags.length === 0) return null;

  const formattedHashtagsText = hashtags.join(' ');

  return (
    <div className="hashtag-section">
      <div className="hashtag-header">
        <span className="section-label">Hashtags</span>
        <CopyButton
          textToCopy={formattedHashtagsText}
          label="Copy Hashtags"
          copiedLabel="Hashtags Copied!"
          className="small-copy-btn"
        />
      </div>

      <div className="hashtag-chips">
        {hashtags.map((tag, idx) => (
          <span key={idx} className="hashtag-chip">
            {tag.startsWith('#') ? tag : `#${tag}`}
          </span>
        ))}
      </div>
    </div>
  );
}

export default HashtagList;
