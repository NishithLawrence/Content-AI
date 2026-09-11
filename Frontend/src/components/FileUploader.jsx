import React, { useState, useRef } from 'react';

const ALLOWED_EXTENSIONS = ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt', 'jpg', 'jpeg', 'png'];

function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

function FileUploader({ files, onAddFiles, onRemoveFile }) {
  const [dragActive, setDragActive] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const fileInputRef = useRef(null);

  const validateAndAddFiles = (fileList) => {
    setErrorMessage('');
    const validFiles = [];
    const invalidNames = [];

    Array.from(fileList).forEach((file) => {
      const ext = file.name.split('.').pop().toLowerCase();
      if (ALLOWED_EXTENSIONS.includes(ext)) {
        // Prevent exact duplicate file entries
        if (!files.some((f) => f.name === file.name && f.size === file.size)) {
          validFiles.push(file);
        }
      } else {
        invalidNames.push(file.name);
      }
    });

    if (invalidNames.length > 0) {
      setErrorMessage(`Unsupported format for: ${invalidNames.join(', ')}. Supported: PDF, DOC, DOCX, PPT, PPTX, XLS, XLSX, TXT, JPG, PNG`);
    }

    if (validFiles.length > 0) {
      onAddFiles(validFiles);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndAddFiles(e.dataTransfer.files);
    }
  };

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndAddFiles(e.target.files);
      e.target.value = ''; // Reset input to allow re-uploading same file if removed
    }
  };

  return (
    <section className="section-container">
      <div className="section-header">
        <span className="step-number">Step 4</span>
        <h2 className="section-title">Add reference materials <span className="optional-tag">(Optional)</span></h2>
        <p className="section-subtitle">Upload brand information, product details, brochures or other reference material.</p>
      </div>

      <div
        className={`dropzone-container ${dragActive ? 'active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        tabIndex={0}
        role="button"
        aria-label="Upload reference material files"
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            fileInputRef.current?.click();
          }
        }}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.txt,.jpg,.jpeg,.png"
          onChange={handleChange}
          style={{ display: 'none' }}
        />

        <div className="dropzone-icon">📁</div>
        <div className="dropzone-text">
          <strong>Click to upload</strong> or drag and drop reference files here
        </div>
        <div className="dropzone-formats">
          Supported formats: PDF, DOC, DOCX, PPT, PPTX, XLS, XLSX, TXT, JPG, PNG
        </div>
      </div>

      {errorMessage && (
        <div className="uploader-error-alert" role="alert">
          <span className="alert-icon">⚠️</span>
          <span>{errorMessage}</span>
        </div>
      )}

      {files.length > 0 && (
        <div className="file-list-container">
          <h4 className="file-list-header">Attached Reference Files ({files.length})</h4>
          <ul className="file-list">
            {files.map((file, index) => {
              const ext = file.name.split('.').pop().toUpperCase();
              return (
                <li key={`${file.name}-${index}`} className="file-item">
                  <div className="file-info">
                    <span className="file-ext-badge">{ext}</span>
                    <div className="file-details">
                      <span className="file-name">{file.name}</span>
                      <span className="file-size">{formatFileSize(file.size)}</span>
                    </div>
                  </div>
                  <button
                    type="button"
                    className="file-remove-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      onRemoveFile(index);
                    }}
                    aria-label={`Remove file ${file.name}`}
                    title="Remove file"
                  >
                    ✕
                  </button>
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </section>
  );
}

export default FileUploader;
