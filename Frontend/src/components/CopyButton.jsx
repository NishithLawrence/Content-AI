import React, { useState } from 'react';

function CopyButton({ textToCopy, label = 'Copy', copiedLabel = 'Copied!', className = '' }) {
  const [isCopied, setIsCopied] = useState(false);

  const handleCopy = async () => {
    if (!textToCopy) return;
    try {
      await navigator.clipboard.writeText(textToCopy);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  };

  return (
    <button
      type="button"
      className={`action-btn copy-btn ${isCopied ? 'copied' : ''} ${className}`}
      onClick={handleCopy}
      title={isCopied ? 'Copied to clipboard!' : label}
    >
      <span className="btn-icon">{isCopied ? '✓' : '📋'}</span>
      <span className="btn-label">{isCopied ? copiedLabel : label}</span>
    </button>
  );
}

export default CopyButton;
