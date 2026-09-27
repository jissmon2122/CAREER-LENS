import React from 'react';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="container footer-content">
        <div>
          <div style={{ fontWeight: 800, color: '#fff', marginBottom: '0.25rem' }}>
            Career Lens Platform
          </div>
          <p className="footer-text">
            AI-Powered Skill Demand Forecasting, Resume Intelligence & Career Analytics.
          </p>
        </div>
        <div className="footer-text">
          &copy; {new Date().getFullYear()} AI Career Lens. Final Year B.Tech CSE Project.
        </div>
      </div>
    </footer>
  );
};

export default Footer;
