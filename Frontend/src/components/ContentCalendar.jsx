import React from 'react';
import PostCard from './PostCard';

function ContentCalendar({ posts = [], onRegeneratePost, regeneratingPostNumber }) {
  if (!posts || posts.length === 0) return null;

  return (
    <div className="content-calendar-container">
      <div className="calendar-section-header">
        <h3 className="calendar-title">Content Calendar ({posts.length} Posts)</h3>
        <p className="calendar-subtitle">Complete schedule tailored to your strategy and reference guidelines.</p>
      </div>

      <div className="posts-vertical-grid">
        {posts.map((post) => (
          <PostCard
            key={post.post_number}
            post={post}
            onRegeneratePost={onRegeneratePost}
            isRegenerating={regeneratingPostNumber === post.post_number}
          />
        ))}
      </div>
    </div>
  );
}

export default ContentCalendar;
