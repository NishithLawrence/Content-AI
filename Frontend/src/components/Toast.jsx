import React, { useEffect } from 'react';

function Toast({ message, onClose, duration = 4000 }) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, duration);
    return () => clearTimeout(timer);
  }, [onClose, duration]);

  return (
    <div className="toast-container" role="status" aria-live="polite">
      <div className="toast-content">
        <span className="toast-icon">🚀</span>
        <span className="toast-message">{message}</span>
        <button type="button" className="toast-close" onClick={onClose} aria-label="Close notification">
          ✕
        </button>
      </div>
    </div>
  );
}

export default Toast;
