import React from 'react';

const LoadingSpinner = ({ text = "Loading..." }) => {
  return (
    <div className="spinner-container">
      <div className="spinner"></div>
      <p style={{ marginTop: '1rem', color: 'var(--text-muted)', fontSize: '0.9rem' }}>{text}</p>
    </div>
  );
};

export default LoadingSpinner;
