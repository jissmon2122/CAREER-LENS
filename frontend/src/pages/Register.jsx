import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';
import { useAuth } from '../context/AuthContext';
import GoogleAuthButton from '../components/GoogleAuthButton';

const Register = () => {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirm_password: '',
    education: 'Bachelor\'s Degree',
    degree: '',
    preferred_job_role: '',
    preferred_location: '',
    experience_level: 'Fresher'
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleLocalSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!formData.name.trim() || !formData.email.trim() || !formData.password) {
      setError('Please fill in all required fields');
      return;
    }

    if (formData.password !== formData.confirm_password) {
      setError('Password and Confirm Password do not match');
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters in length');
      return;
    }

    setLoading(true);

    try {
      const response = await authService.register(formData);
      if (response.success) {
        navigate('/login', {
          state: { message: 'Account created successfully! Please log in.' }
        });
      } else {
        setError(response.message || 'Registration failed');
      }
    } catch (err) {
      const apiMsg = err.response?.data?.message || err.message || 'Server error during registration';
      setError(apiMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSuccess = async (credentialToken) => {
    setLoading(true);
    setError('');

    try {
      const response = await authService.googleLogin(credentialToken);
      if (response.success && response.data.token) {
        login(response.data.token, response.data.user);
        navigate('/dashboard', { replace: true });
      } else {
        setError(response.message || 'Google authentication failed');
      }
    } catch (err) {
      const apiMsg = err.response?.data?.message || err.message || 'Google authentication error';
      setError(apiMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container" style={{ padding: '3.5rem 1.5rem' }}>
      <div style={{ maxWidth: '640px', margin: '0 auto' }}>
        <div className="glass-card">
          <div style={{ textAlign: 'center', marginBottom: '1.75rem' }}>
            <h2 style={{ fontSize: '1.75rem', fontWeight: '800', marginBottom: '0.5rem' }}>Create Candidate Account</h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.925rem' }}>
              Set up your profile to upload resumes and unlock Career Lens features.
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

          {/* Primary Google Sign-In Button */}
          <GoogleAuthButton
            onSuccess={handleGoogleSuccess}
            onError={(msg) => setError(msg)}
            disabled={loading}
          />

          {/* Divider */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            margin: '1.5rem 0',
            color: 'var(--text-subtle)',
            fontSize: '0.825rem',
            fontWeight: '600',
            textTransform: 'uppercase',
            letterSpacing: '0.05em'
          }}>
            <div style={{ flex: 1, borderBottom: '1px solid var(--border-color)' }}></div>
            <span style={{ padding: '0 0.75rem' }}>OR CREATE LOCAL ACCOUNT</span>
            <div style={{ flex: 1, borderBottom: '1px solid var(--border-color)' }}></div>
          </div>

          {/* Local Registration Form */}
          <form onSubmit={handleLocalSubmit}>
            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">Full Name *</label>
                <input
                  type="text"
                  name="name"
                  className="form-input"
                  placeholder="e.g. Rahul Sharma"
                  value={formData.name}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Email Address *</label>
                <input
                  type="email"
                  name="email"
                  className="form-input"
                  placeholder="rahul@example.com"
                  value={formData.email}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">Password *</label>
                <input
                  type="password"
                  name="password"
                  className="form-input"
                  placeholder="••••••••"
                  value={formData.password}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Confirm Password *</label>
                <input
                  type="password"
                  name="confirm_password"
                  className="form-input"
                  placeholder="••••••••"
                  value={formData.confirm_password}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">Education Qualification</label>
                <select name="education" className="form-select" value={formData.education} onChange={handleChange}>
                  <option value="Trade Certificate / ITI">Trade Certificate / ITI / Apprenticeship</option>
                  <option value="Vocational Diploma">Vocational / Technical Diploma</option>
                  <option value="Associate Degree">Associate Degree (AAS / AS)</option>
                  <option value="Bachelor's Degree">Bachelor's Degree (B.Sc / B.Tech / B.A / B.Com / BSN)</option>
                  <option value="Master's Degree">Master's Degree (M.Sc / M.Tech / M.A / MBA / MSN)</option>
                  <option value="High School / Secondary">High School / Secondary</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Degree / Field of Study</label>
                <input
                  type="text"
                  name="degree"
                  className="form-input"
                  placeholder="e.g. Electrical, Nursing, Mechanical, CS, Accounting"
                  value={formData.degree}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">Preferred Job Role</label>
                <input
                  type="text"
                  name="preferred_job_role"
                  className="form-input"
                  placeholder="e.g. Electrician, Nurse, Accountant, Welder, Developer"
                  value={formData.preferred_job_role}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Preferred Location</label>
                <input
                  type="text"
                  name="preferred_location"
                  className="form-input"
                  placeholder="e.g. Chennai, Remote"
                  value={formData.preferred_location}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Experience Level</label>
              <select name="experience_level" className="form-select" value={formData.experience_level} onChange={handleChange}>
                <option value="Student">Student</option>
                <option value="Fresher">Fresher</option>
                <option value="0–2 Years">0–2 Years</option>
                <option value="2–5 Years">2–5 Years</option>
                <option value="5+ Years">5+ Years</option>
              </select>
            </div>

            <button type="submit" className="btn btn-primary btn-block" disabled={loading} style={{ marginTop: '1rem' }}>
              {loading ? 'Creating Account...' : 'Create Account'}
            </button>
          </form>

          <div style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
            Already have an account?{' '}
            <Link to="/login" style={{ color: 'var(--primary)', fontWeight: '600' }}>
              Sign In
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;
