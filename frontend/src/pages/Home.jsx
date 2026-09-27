import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Home = () => {
  const { isAuthenticated } = useAuth();

  return (
    <div className="home-page">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="container">
          <div className="hero-chip">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
            </svg>
            Career Lens — Final Year CSE B.Tech Project Platform
          </div>
          
          <h1 className="hero-title">
            Build Your Career With <br />
            Career Lens AI
          </h1>
          
          <p className="hero-subtitle">
            Analyze your skills, discover career opportunities, identify skill gaps, and prepare for the future job market.
          </p>

          <div className="hero-cta">
            {isAuthenticated ? (
              <Link to="/dashboard" className="btn btn-primary" style={{ padding: '0.85rem 2rem', fontSize: '1.05rem' }}>
                Go to Dashboard
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <line x1="5" y1="12" x2="19" y2="12" />
                  <polyline points="12 5 19 12 12 19" />
                </svg>
              </Link>
            ) : (
              <>
                <Link to="/register" className="btn btn-primary" style={{ padding: '0.85rem 2rem', fontSize: '1.05rem' }}>
                  Get Started
                </Link>
                <Link to="/login" className="btn btn-secondary" style={{ padding: '0.85rem 2rem', fontSize: '1.05rem' }}>
                  Login Account
                </Link>
              </>
            )}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Core Intelligence Modules</h2>
            <p className="section-subtitle">
              Designed to transform raw resume data into actionable career insights
            </p>
          </div>

          <div className="features-grid">
            <div className="glass-card glass-card-interactive">
              <div className="feature-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                  <line x1="16" y1="13" x2="8" y2="13" />
                  <line x1="16" y1="17" x2="8" y2="17" />
                  <polyline points="10 9 9 9 8 9" />
                </svg>
              </div>
              <h3 className="feature-title">Resume Intelligence</h3>
              <p className="feature-desc">
                Upload your resume in PDF format to establish your candidate profile and maintain metadata tracking.
              </p>
            </div>

            <div className="glass-card glass-card-interactive">
              <div className="feature-icon" style={{ color: 'var(--accent-purple)', background: 'rgba(168, 85, 247, 0.15)' }}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="2" y="7" width="20" height="14" rx="2" ry="2" />
                  <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
                </svg>
              </div>
              <h3 className="feature-title">Smart Job Matching</h3>
              <p className="feature-desc">
                Match your profile with relevant technical job roles based on skills, location, and experience criteria.
              </p>
            </div>

            <div className="glass-card glass-card-interactive">
              <div className="feature-icon" style={{ color: 'var(--accent-pink)', background: 'rgba(236, 72, 153, 0.15)' }}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                  <polyline points="22 4 12 14.01 9 11.01" />
                </svg>
              </div>
              <h3 className="feature-title">Skill Gap Analysis</h3>
              <p className="feature-desc">
                Identify key missing technical competencies required to qualify for top-tier industry designations.
              </p>
            </div>

            <div className="glass-card glass-card-interactive">
              <div className="feature-icon" style={{ color: 'var(--accent-cyan)', background: 'rgba(6, 182, 212, 0.15)' }}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
                  <polyline points="17 6 23 6 23 12" />
                </svg>
              </div>
              <h3 className="feature-title">Career Forecasting</h3>
              <p className="feature-desc">
                Predict emerging domain skills, salary trends, and high-demand roles using market data models.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
