import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { resumeAPI } from '../services/api';

const ResumeUpload = () => {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [uploadSuccess, setUploadSuccess] = useState(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    validateAndSetFile(file);
  };

  const validateAndSetFile = (file) => {
    setError('');
    setUploadSuccess(null);

    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Invalid file type. Only PDF documents (.pdf) are allowed.');
      setSelectedFile(null);
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setError('File size exceeds maximum limit of 5 MB.');
      setSelectedFile(null);
      return;
    }

    setSelectedFile(file);
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
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a PDF resume file first.');
      return;
    }

    setUploading(true);
    setError('');

    const formData = new FormData();
    formData.append('resume', selectedFile);

    try {
      const response = await resumeAPI.uploadResume(formData);
      if (response.success) {
        setUploadSuccess(response.data.resume);
        setSelectedFile(null);
      } else {
        setError(response.message || 'Failed to upload resume.');
      }
    } catch (err) {
      const msg = err.response?.data?.message || err.message || 'Server error during file upload';
      setError(msg);
    } finally {
      setUploading(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="container" style={{ padding: '3.5rem 1.5rem' }}>
      <div style={{ maxWidth: '640px', margin: '0 auto' }}>
        <div className="glass-card">
          <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
            <h2 style={{ fontSize: '1.75rem', fontWeight: '800', marginBottom: '0.5rem' }}>Upload Resume</h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.925rem' }}>
              Upload your latest resume in PDF format to build your candidate profile.
            </p>
          </div>

          {error && (
            <div className="alert alert-danger">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
              {error}
            </div>
          )}

          {uploadSuccess && (
            <div className="alert alert-success" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '0.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 700 }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                  <polyline points="22 4 12 14.01 9 11.01" />
                </svg>
                ✓ Resume uploaded successfully
              </div>
              <div style={{ fontSize: '0.85rem', color: 'rgba(255,255,255,0.9)', marginTop: '0.25rem' }}>
                <div><strong>File Name:</strong> {uploadSuccess.original_filename || uploadSuccess.filename}</div>
                <div><strong>Upload Date:</strong> {new Date(uploadSuccess.uploaded_at || Date.now()).toLocaleDateString()}</div>
                <div><strong>Status:</strong> <span className="badge badge-success">{uploadSuccess.status}</span></div>
              </div>
              <button 
                onClick={() => navigate('/dashboard')} 
                className="btn btn-primary" 
                style={{ marginTop: '0.75rem', padding: '0.4rem 1rem', fontSize: '0.85rem' }}
              >
                Go to Dashboard
              </button>
            </div>
          )}

          {/* Drag & Drop Upload Zone */}
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            style={{
              border: `2px dashed ${dragActive ? 'var(--primary)' : 'var(--border-color)'}`,
              borderRadius: 'var(--radius-lg)',
              padding: '3rem 1.5rem',
              textAlign: 'center',
              background: dragActive ? 'var(--primary-glow)' : 'rgba(18, 25, 41, 0.4)',
              transition: 'var(--transition-fast)',
              cursor: 'pointer',
              marginBottom: '1.5rem'
            }}
            onClick={() => document.getElementById('resume-file-input').click()}
          >
            <input
              id="resume-file-input"
              type="file"
              accept=".pdf"
              style={{ display: 'none' }}
              onChange={handleFileChange}
            />

            <div style={{
              width: '56px',
              height: '56px',
              borderRadius: '50%',
              background: 'var(--primary-glow)',
              color: 'var(--primary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 1.25rem'
            }}>
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
            </div>

            <p style={{ fontWeight: '700', fontSize: '1.05rem', marginBottom: '0.4rem' }}>
              Drag and drop your PDF resume here
            </p>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
              or click to browse files (PDF only, Max size: 5 MB)
            </p>
          </div>

          {/* Selected File Details Box */}
          {selectedFile && (
            <div style={{
              background: 'var(--bg-input)',
              border: '1px solid var(--border-color-glow)',
              borderRadius: 'var(--radius-md)',
              padding: '1rem 1.25rem',
              marginBottom: '1.5rem',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.9rem' }}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                </svg>
                <div>
                  <div style={{ fontWeight: '600', fontSize: '0.95rem' }}>{selectedFile.name}</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Size: {formatFileSize(selectedFile.size)}
                  </div>
                </div>
              </div>
              <button
                onClick={(e) => { e.stopPropagation(); setSelectedFile(null); }}
                style={{ background: 'none', border: 'none', color: 'var(--text-subtle)', cursor: 'pointer' }}
                title="Remove file"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>
          )}

          {/* Upload Button */}
          <button
            onClick={handleUpload}
            className="btn btn-primary btn-block"
            disabled={!selectedFile || uploading}
          >
            {uploading ? (
              <>
                <div className="spinner" style={{ width: '18px', height: '18px', borderWidth: '2px' }}></div>
                Uploading...
              </>
            ) : (
              'Upload Resume'
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ResumeUpload;
