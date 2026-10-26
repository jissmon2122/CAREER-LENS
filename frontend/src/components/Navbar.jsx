import React from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { user, isAuthenticated, logout, isOffline, retryAuth } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <>
      {isOffline && (
        <div style={{ backgroundColor: '#fff3cd', color: '#856404', padding: '0.4rem 1rem', textAlign: 'center', fontSize: '0.82rem', borderBottom: '1px solid #ffeeba', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
          <span>⚠️ Server is connecting or temporarily unreachable. Cached session preserved.</span>
          <button onClick={retryAuth} style={{ padding: '2px 8px', fontSize: '0.78rem', cursor: 'pointer', borderRadius: '4px', border: '1px solid #856404', background: '#fff' }}>
            Retry Connection
          </button>
        </div>
      )}
      <nav className="navbar">
      <div className="container nav-wrapper">
        <Link to="/" className="brand-logo">
          <div className="logo-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <polygon points="12 2 2 7 12 12 22 7 12 2" />
              <polyline points="2 17 12 22 22 17" />
              <polyline points="2 12 12 17 22 12" />
            </svg>
          </div>
          <span>Career Lens</span>
        </Link>

        <ul className="nav-links">
          <li>
            <NavLink to="/" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
              Home
            </NavLink>
          </li>
          
          {isAuthenticated ? (
            <>
              <li>
                <NavLink to="/dashboard" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
                  Dashboard
                </NavLink>
              </li>
              <li>
                <NavLink to="/jobs/search" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
                  Recommended Jobs
                </NavLink>
              </li>
              <li>
                <NavLink to="/resume-upload" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
                  Upload Resume
                </NavLink>
              </li>
              <li>
                <NavLink to="/salary" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
                  Salary Predictor
                </NavLink>
              </li>
              <li>
                <NavLink to="/dashboard/skill-demand" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
                  Skill Demand
                </NavLink>
              </li>
              <li className="nav-user">
                <span className="user-badge">
                  {user?.profile_picture ? (
                    <img
                      src={user.profile_picture}
                      alt={user.name}
                      style={{ width: '22px', height: '22px', borderRadius: '50%', objectFit: 'cover' }}
                    />
                  ) : (
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                      <circle cx="12" cy="7" r="4" />
                    </svg>
                  )}
                  {user?.name?.split(' ')[0] || 'Candidate'}
                </span>
                <button onClick={handleLogout} className="btn btn-secondary" style={{ padding: '0.4rem 0.9rem', fontSize: '0.85rem' }}>
                  Logout
                </button>
              </li>
            </>
          ) : (
            <>
              <li>
                <NavLink to="/login" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
                  Login
                </NavLink>
              </li>
              <li>
                <Link to="/register" className="btn btn-primary" style={{ padding: '0.5rem 1.1rem', fontSize: '0.875rem' }}>
                  Get Started
                </Link>
              </li>
            </>
          )}
        </ul>
      </div>
    </nav>
    </>
  );
};

export default Navbar;
