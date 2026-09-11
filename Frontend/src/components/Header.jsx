import React from 'react';

function Header({ backendStatus }) {
  return (
    <header className="saas-header">
      <div className="header-left">
        <div className="logo-container">
          <div className="logo-icon-box">⚡</div>
          <div className="logo-text-group">
            <span className="logo-brand">ContentAI</span>
            <span className="logo-subtitle">AI-powered social content planning</span>
          </div>
        </div>
      </div>

      <div className="header-right">
        <div className="status-indicator-badge">
          <span className={`status-dot ${backendStatus === 'connected' ? 'connected' : backendStatus === 'connecting' ? 'connecting' : 'disconnected'}`}></span>
          <span className="status-text">
            {backendStatus === 'connected' ? 'API Online' : backendStatus === 'connecting' ? 'Connecting...' : 'API Offline'}
          </span>
        </div>
        <div className="studio-badge">AI Content Studio</div>
      </div>
    </header>
  );
}

export default Header;
