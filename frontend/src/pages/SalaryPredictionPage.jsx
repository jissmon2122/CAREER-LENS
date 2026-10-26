import React, { useState, useEffect } from 'react';
import { salaryAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';

// Native lightweight SVG icon components (zero external dependencies)
const DollarIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="12" y1="1" x2="12" y2="23"></line>
    <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
  </svg>
);

const TrendingIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
    <polyline points="17 6 23 6 23 12"></polyline>
  </svg>
);

const BriefcaseIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
    <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
  </svg>
);

const CheckIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12"></polyline>
  </svg>
);

const AlertIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"></circle>
    <line x1="12" y1="8" x2="12" y2="12"></line>
    <line x1="12" y1="16" x2="12.01" y2="16"></line>
  </svg>
);

const RefreshIcon = ({ spin }) => (
  <svg
    width="16"
    height="16"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    style={spin ? { animation: 'spin 1s linear infinite' } : {}}
  >
    <polyline points="23 4 23 10 17 10"></polyline>
    <polyline points="1 20 1 14 7 14"></polyline>
    <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
  </svg>
);

const FileTextIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
    <polyline points="14 2 14 8 20 8"></polyline>
    <line x1="16" y1="13" x2="8" y2="13"></line>
    <line x1="16" y1="17" x2="8" y2="17"></line>
    <polyline points="10 9 9 9 8 9"></polyline>
  </svg>
);

const ClockIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"></circle>
    <polyline points="12 6 12 12 16 14"></polyline>
  </svg>
);

const InfoIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"></circle>
    <line x1="12" y1="16" x2="12" y2="12"></line>
    <line x1="12" y1="8" x2="12.01" y2="8"></line>
  </svg>
);

const SalaryPredictionPage = () => {
  const { isAuthenticated } = useAuth();

  // Reference data
  const [rolesData, setRolesData] = useState({ roles: [], domains: {} });
  const [locationsData, setLocationsData] = useState({ countries: [] });
  const [loadingMeta, setLoadingMeta] = useState(true);

  // Form inputs
  const [formData, setFormData] = useState({
    role: 'Software Engineer',
    country: 'IN',
    city: 'Bengaluru',
    experience_years: 3.5,
    seniority: 'mid',
    education: 'bachelor',
    skills: 'Python, Docker, SQL',
    industry: 'Technology',
    company_type: 'standard',
  });

  // State
  const [prediction, setPrediction] = useState(null);
  const [isPredicting, setIsPredicting] = useState(false);
  const [autofillLoading, setAutofillLoading] = useState(false);
  const [autofillMessage, setAutofillMessage] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview'); // 'overview' | 'progression' | 'factors'

  // Load roles & locations on mount
  useEffect(() => {
    const fetchMetadata = async () => {
      try {
        setLoadingMeta(true);
        const [rolesRes, locRes] = await Promise.all([
          salaryAPI.getRoles(),
          salaryAPI.getLocations(),
        ]);
        if (rolesRes.success) {
          setRolesData({ roles: rolesRes.roles, domains: rolesRes.domains });
        }
        if (locRes.success) {
          setLocationsData({ countries: locRes.countries });
        }
      } catch (err) {
        console.error('Failed to load salary metadata:', err);
      } finally {
        setLoadingMeta(false);
      }
    };
    fetchMetadata();
  }, []);

  // Autofill from user resume if authenticated
  const handleAutofill = async () => {
    try {
      setAutofillLoading(true);
      setAutofillMessage(null);
      setError(null);
      const res = await salaryAPI.getAutofillProfile();
      if (res.success && res.profile) {
        const p = res.profile;
        setFormData((prev) => ({
          ...prev,
          role: p.role || prev.role,
          experience_years: p.experience_years ?? prev.experience_years,
          seniority: p.seniority || prev.seniority,
          city: p.city || prev.city,
          country: p.country || prev.country,
          education: p.education || prev.education,
          skills: Array.isArray(p.skills) ? p.skills.join(', ') : prev.skills,
        }));
        setAutofillMessage({
          type: 'success',
          text: `Autofilled from latest resume: ${p.role} (${p.experience_years} yrs exp, ${p.city || 'India'})`,
        });
      } else {
        setAutofillMessage({
          type: 'info',
          text: res.message || 'No parsed resume found. You can enter your details manually.',
        });
      }
    } catch (err) {
      setAutofillMessage({
        type: 'error',
        text: 'Failed to retrieve resume profile. Please enter manually.',
      });
    } finally {
      setAutofillLoading(false);
    }
  };

  // Run prediction
  const handlePredict = async (e) => {
    if (e) e.preventDefault();
    if (!formData.role) {
      setError('Please select or enter a profession.');
      return;
    }
    try {
      setIsPredicting(true);
      setError(null);
      const payload = {
        role: formData.role,
        country: formData.country,
        city: formData.city,
        experience_years: parseFloat(formData.experience_years) || 0,
        seniority: formData.seniority,
        education: formData.education,
        skills: formData.skills ? formData.skills.split(',').map((s) => s.trim()).filter(Boolean) : [],
        industry: formData.industry,
        company_type: formData.company_type,
      };
      const res = await salaryAPI.predictSalary(payload);
      if (res.success && res.data) {
        setPrediction(res.data);
      } else {
        setError(res.error || 'Failed to calculate salary prediction.');
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Network error during prediction.');
    } finally {
      setIsPredicting(false);
    }
  };

  // Run initial prediction once metadata loads
  useEffect(() => {
    if (!loadingMeta && !prediction) {
      handlePredict();
    }
  }, [loadingMeta]);

  // Current country cities
  const selectedCountryObj = locationsData.countries.find((c) => c.code === formData.country);
  const availableCities = selectedCountryObj?.cities || [];

  return (
    <div className="container" style={{ padding: '2.5rem 1rem', maxWidth: '1240px', margin: '0 auto' }}>
      {/* Header Banner */}
      <div style={{ marginBottom: '2rem', textAlign: 'center' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '6px 16px', background: '#eef2ff', color: '#4f46e5', borderRadius: '999px', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.75rem' }}>
          <DollarIcon /> AI Labor Market Intelligence & Quantile Compensation Model
        </div>
        <h1 style={{ fontSize: '2.25rem', fontWeight: 800, color: '#111827', margin: '0 0 0.5rem 0' }}>
          AI-Powered Salary Prediction & Market Benchmarks
        </h1>
        <p style={{ color: '#6b7280', fontSize: '1.05rem', maxWidth: '780px', margin: '0 auto' }}>
          Estimate your market value across 105 canonical professions—including tech, skilled trades, healthcare, finance, education, and engineering—calibrated across global labor datasets.
        </p>
      </div>

      {/* Main Grid: Form Left, Results Right */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(320px, 410px) 1fr', gap: '2rem', alignItems: 'start' }}>
        {/* Left Card: Input Parameters */}
        <div style={{ background: '#fff', borderRadius: '16px', border: '1px solid #e5e7eb', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)', padding: '1.75rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 700, margin: 0, color: '#1f2937', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ color: '#4f46e5', display: 'inline-flex' }}><BriefcaseIcon /></span> Profile Inputs
            </h2>
            {isAuthenticated && (
              <button
                type="button"
                onClick={handleAutofill}
                disabled={autofillLoading}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  background: '#f3f4f6',
                  color: '#374151',
                  border: '1px solid #d1d5db',
                  borderRadius: '8px',
                  padding: '6px 10px',
                  fontSize: '0.78rem',
                  fontWeight: 600,
                  cursor: autofillLoading ? 'wait' : 'pointer',
                  transition: 'all 0.15s ease'
                }}
                title="Autofill fields from your parsed resume"
              >
                {autofillLoading ? <RefreshIcon spin={true} /> : <FileTextIcon />}
                Autofill from Resume
              </button>
            )}
          </div>

          {autofillMessage && (
            <div style={{
              padding: '8px 12px',
              borderRadius: '8px',
              fontSize: '0.82rem',
              marginBottom: '1rem',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              background: autofillMessage.type === 'success' ? '#ecfdf5' : autofillMessage.type === 'error' ? '#fef2f2' : '#f0f9ff',
              color: autofillMessage.type === 'success' ? '#065f46' : autofillMessage.type === 'error' ? '#991b1b' : '#075985',
              border: `1px solid ${autofillMessage.type === 'success' ? '#a7f3d0' : autofillMessage.type === 'error' ? '#fecaca' : '#bae6fd'}`
            }}>
              {autofillMessage.type === 'success' ? <CheckIcon /> : <InfoIcon />}
              <span>{autofillMessage.text}</span>
            </div>
          )}

          <form onSubmit={handlePredict}>
            {/* Target Profession / Canonical Role */}
            <div style={{ marginBottom: '1.2rem' }}>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#374151', marginBottom: '0.35rem' }}>
                Target Profession / Job Role *
              </label>
              <input
                type="text"
                list="roles-datalist"
                value={formData.role}
                onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                placeholder="e.g. Electrician, Software Engineer, Registered Nurse..."
                required
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  borderRadius: '8px',
                  border: '1px solid #d1d5db',
                  fontSize: '0.92rem',
                  outline: 'none',
                  boxSizing: 'border-box'
                }}
              />
              <datalist id="roles-datalist">
                {rolesData.roles.map((r, i) => (
                  <option key={i} value={r} />
                ))}
              </datalist>
            </div>

            {/* Country and City Row */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1.2rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#374151', marginBottom: '0.35rem' }}>
                  Country
                </label>
                <select
                  value={formData.country}
                  onChange={(e) => setFormData({ ...formData, country: e.target.value, city: '' })}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    borderRadius: '8px',
                    border: '1px solid #d1d5db',
                    fontSize: '0.9rem',
                    background: '#fff',
                    boxSizing: 'border-box'
                  }}
                >
                  {locationsData.countries.map((c) => (
                    <option key={c.code} value={c.code}>
                      {c.name} ({c.currency} {c.symbol})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#374151', marginBottom: '0.35rem' }}>
                  City Hub
                </label>
                <input
                  type="text"
                  list="cities-datalist"
                  value={formData.city}
                  onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                  placeholder="e.g. Bengaluru, Austin..."
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    borderRadius: '8px',
                    border: '1px solid #d1d5db',
                    fontSize: '0.9rem',
                    boxSizing: 'border-box'
                  }}
                />
                <datalist id="cities-datalist">
                  {availableCities.map((ct, idx) => (
                    <option key={idx} value={ct.name} />
                  ))}
                </datalist>
              </div>
            </div>

            {/* Experience Slider */}
            <div style={{ marginBottom: '1.2rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                <label style={{ fontSize: '0.875rem', fontWeight: 600, color: '#374151' }}>
                  Years of Experience
                </label>
                <span style={{ fontSize: '0.875rem', fontWeight: 700, color: '#4f46e5' }}>
                  {formData.experience_years} {formData.experience_years === 1 ? 'Year' : 'Years'}
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="25"
                step="0.5"
                value={formData.experience_years}
                onChange={(e) => setFormData({ ...formData, experience_years: parseFloat(e.target.value) })}
                style={{ width: '100%', accentColor: '#4f46e5', cursor: 'pointer' }}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: '#9ca3af' }}>
                <span>Entry (0)</span>
                <span>Mid (5)</span>
                <span>Senior (10)</span>
                <span>Executive (25)</span>
              </div>
            </div>

            {/* Seniority & Education Row */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1.2rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#374151', marginBottom: '0.35rem' }}>
                  Seniority Level
                </label>
                <select
                  value={formData.seniority}
                  onChange={(e) => setFormData({ ...formData, seniority: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '9px 12px',
                    borderRadius: '8px',
                    border: '1px solid #d1d5db',
                    fontSize: '0.88rem',
                    background: '#fff',
                    boxSizing: 'border-box'
                  }}
                >
                  <option value="entry">Entry-Level / Junior</option>
                  <option value="mid">Mid-Level</option>
                  <option value="senior">Senior</option>
                  <option value="lead">Lead / Staff</option>
                  <option value="principal">Principal / Architect</option>
                  <option value="manager">Engineering / Ops Manager</option>
                  <option value="director">Director / Executive</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#374151', marginBottom: '0.35rem' }}>
                  Education Level
                </label>
                <select
                  value={formData.education}
                  onChange={(e) => setFormData({ ...formData, education: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '9px 12px',
                    borderRadius: '8px',
                    border: '1px solid #d1d5db',
                    fontSize: '0.88rem',
                    background: '#fff',
                    boxSizing: 'border-box'
                  }}
                >
                  <option value="high school">High School / GED</option>
                  <option value="diploma">Technical Diploma / ITI</option>
                  <option value="associate">Associate Degree</option>
                  <option value="bachelor">Bachelor's Degree</option>
                  <option value="master">Master's Degree</option>
                  <option value="phd">PhD / Doctorate</option>
                </select>
              </div>
            </div>

            {/* Skills chip input */}
            <div style={{ marginBottom: '1.2rem' }}>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#374151', marginBottom: '0.35rem' }}>
                Key Skills & Certifications (comma separated)
              </label>
              <input
                type="text"
                value={formData.skills}
                onChange={(e) => setFormData({ ...formData, skills: e.target.value })}
                placeholder="e.g. Python, AWS, Docker, Kubernetes, Master Electrician..."
                style={{
                  width: '100%',
                  padding: '9px 12px',
                  borderRadius: '8px',
                  border: '1px solid #d1d5db',
                  fontSize: '0.88rem',
                  boxSizing: 'border-box'
                }}
              />
              <span style={{ fontSize: '0.75rem', color: '#6b7280' }}>
                Premium skills (e.g. Generative AI, PyTorch, Kubernetes, Master License) boost your quantile position.
              </span>
            </div>

            {/* Company Type */}
            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#374151', marginBottom: '0.35rem' }}>
                Company Type / Sector
              </label>
              <select
                value={formData.company_type}
                onChange={(e) => setFormData({ ...formData, company_type: e.target.value })}
                style={{
                  width: '100%',
                  padding: '9px 12px',
                  borderRadius: '8px',
                  border: '1px solid #d1d5db',
                  fontSize: '0.88rem',
                  background: '#fff',
                  boxSizing: 'border-box'
                }}
              >
                <option value="standard">Standard / Industry Average</option>
                <option value="early startup (seed - series a)">Early-Stage Startup</option>
                <option value="growth-stage (series b-d)">Growth-Stage Startup</option>
                <option value="mid-size tech">Mid-Size Product Tech</option>
                <option value="large enterprise / mnc">Large Enterprise / MNC</option>
                <option value="big tech / faang">Tier 1 Big Tech / FAANG</option>
                <option value="global consulting (tier 1)">Tier 1 Global Consulting</option>
                <option value="government / public sector">Public Sector / Govt</option>
              </select>
            </div>

            {/* Calculate Button */}
            <button
              type="submit"
              disabled={isPredicting}
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '10px',
                border: 'none',
                background: '#4f46e5',
                color: '#fff',
                fontSize: '0.98rem',
                fontWeight: 700,
                cursor: isPredicting ? 'wait' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                boxShadow: '0 4px 12px rgba(79, 70, 229, 0.25)',
                transition: 'background 0.2s ease'
              }}
            >
              {isPredicting ? <RefreshIcon spin={true} /> : <TrendingIcon />}
              {isPredicting ? 'Calculating Market Estimate...' : 'Calculate Estimated Salary'}
            </button>
          </form>
        </div>

        {/* Right Section: Prediction Results & Dashboards */}
        <div>
          {error && (
            <div style={{ padding: '1rem', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '12px', color: '#991b1b', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <AlertIcon />
              <span>{error}</span>
            </div>
          )}

          {isPredicting && (
            <div style={{ background: '#fff', borderRadius: '16px', padding: '3rem', textAlign: 'center', border: '1px solid #e5e7eb' }}>
              <div style={{ display: 'inline-block', color: '#4f46e5', marginBottom: '1rem' }}>
                <RefreshIcon spin={true} />
              </div>
              <h3 style={{ margin: '0 0 0.5rem 0', color: '#111827' }}>Evaluating Labor Quantiles...</h3>
              <p style={{ color: '#6b7280', margin: 0 }}>Calibrating model weights against real market data and regional cost tiers.</p>
            </div>
          )}

          {!isPredicting && prediction && (
            <div>
              {/* Primary Compensation Cards */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
                {/* Annual Gross Median */}
                <div style={{ background: 'linear-gradient(135deg, #4f46e5 0%, #3730a3 100%)', borderRadius: '14px', padding: '1.4rem', color: '#fff', boxShadow: '0 8px 16px -4px rgba(79, 70, 229, 0.3)' }}>
                  <div style={{ fontSize: '0.82rem', textTransform: 'uppercase', letterSpacing: '0.05em', opacity: 0.9, marginBottom: '0.35rem' }}>
                    Median Annual Gross
                  </div>
                  <div style={{ fontSize: '1.85rem', fontWeight: 800, marginBottom: '0.35rem' }}>
                    {prediction.annual.median_formatted}
                  </div>
                  <div style={{ fontSize: '0.85rem', opacity: 0.9 }}>
                    Expected Midpoint ({prediction.currency})
                  </div>
                </div>

                {/* Annual 25th - 75th Percentile Range */}
                <div style={{ background: '#fff', borderRadius: '14px', padding: '1.4rem', border: '1px solid #e5e7eb', boxShadow: '0 2px 4px rgba(0,0,0,0.04)' }}>
                  <div style={{ fontSize: '0.82rem', color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.35rem' }}>
                    Typical Market Range (P25 - P75)
                  </div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#111827', marginBottom: '0.35rem' }}>
                    {prediction.annual.range_formatted}
                  </div>
                  <div style={{ fontSize: '0.85rem', color: '#059669', fontWeight: 600 }}>
                    50% of verified roles fall here
                  </div>
                </div>

                {/* Monthly Equivalent */}
                <div style={{ background: '#fff', borderRadius: '14px', padding: '1.4rem', border: '1px solid #e5e7eb', boxShadow: '0 2px 4px rgba(0,0,0,0.04)' }}>
                  <div style={{ fontSize: '0.82rem', color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.35rem' }}>
                    Monthly Gross Equivalent
                  </div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#111827', marginBottom: '0.35rem' }}>
                    {prediction.monthly.median_formatted}
                  </div>
                  <div style={{ fontSize: '0.85rem', color: '#6b7280' }}>
                    {prediction.monthly.range_formatted} / mo
                  </div>
                </div>
              </div>

              {/* Badges: Profession Domain, Confidence Score, Data Freshness */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem', alignItems: 'center', marginBottom: '1.5rem' }}>
                <span style={{ padding: '4px 12px', background: '#f3f4f6', borderRadius: '999px', fontSize: '0.8rem', fontWeight: 600, color: '#374151' }}>
                  Domain: {prediction.role.domain_label}
                </span>
                <span style={{ padding: '4px 12px', background: '#ecfdf5', borderRadius: '999px', fontSize: '0.8rem', fontWeight: 600, color: '#065f46', display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <CheckIcon /> Confidence: {Math.round(prediction.confidence_score * 100)}%
                </span>
                <span style={{ padding: '4px 12px', background: '#eff6ff', borderRadius: '999px', fontSize: '0.8rem', fontWeight: 600, color: '#1e40af', display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <ClockIcon /> {prediction.data_freshness}
                </span>
                {prediction.applied_skill_premiums.length > 0 && (
                  <span style={{ padding: '4px 12px', background: '#fef3c7', borderRadius: '999px', fontSize: '0.8rem', fontWeight: 600, color: '#92400e' }}>
                    +{prediction.applied_skill_premiums.reduce((acc, s) => acc + s.boost_percent, 0).toFixed(0)}% Skills Premium
                  </span>
                )}
              </div>

              {/* Navigation Tabs */}
              <div style={{ display: 'flex', borderBottom: '1px solid #e5e7eb', marginBottom: '1.25rem' }}>
                {[
                  { id: 'overview', label: 'Quantile Distribution & Levels' },
                  { id: 'progression', label: '1, 3, 5 Year Career Progression' },
                  { id: 'factors', label: 'Influencing Factors & Breakdown' },
                ].map((t) => (
                  <button
                    key={t.id}
                    onClick={() => setActiveTab(t.id)}
                    style={{
                      padding: '10px 16px',
                      background: 'none',
                      border: 'none',
                      borderBottom: activeTab === t.id ? '2px solid #4f46e5' : '2px solid transparent',
                      color: activeTab === t.id ? '#4f46e5' : '#6b7280',
                      fontWeight: activeTab === t.id ? 700 : 500,
                      cursor: 'pointer',
                      fontSize: '0.9rem'
                    }}
                  >
                    {t.label}
                  </button>
                ))}
              </div>

              {/* Tab 1: Overview & Seniority Comparison */}
              {activeTab === 'overview' && (
                <div style={{ background: '#fff', borderRadius: '16px', border: '1px solid #e5e7eb', padding: '1.5rem', marginBottom: '1.5rem' }}>
                  <h3 style={{ fontSize: '1.1rem', fontWeight: 700, margin: '0 0 1rem 0', color: '#111827' }}>
                    Compensation by Seniority Level in {prediction.city}
                  </h3>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
                    {Object.entries(prediction.seniority_comparison).map(([level, data]) => (
                      <div
                        key={level}
                        style={{
                          padding: '1.1rem',
                          borderRadius: '12px',
                          border: data.is_current ? '2px solid #4f46e5' : '1px solid #e5e7eb',
                          background: data.is_current ? '#f5f3ff' : '#fafafa',
                          position: 'relative'
                        }}
                      >
                        {data.is_current && (
                          <span style={{ position: 'absolute', top: '-10px', right: '12px', background: '#4f46e5', color: '#fff', fontSize: '0.68rem', fontWeight: 700, padding: '2px 8px', borderRadius: '999px' }}>
                            Current Fit
                          </span>
                        )}
                        <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#4b5563', marginBottom: '0.25rem' }}>
                          {level}
                        </div>
                        <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#111827' }}>
                          {prediction.currency_symbol}{data.salary.toLocaleString()}
                        </div>
                        <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.2rem' }}>
                          {prediction.currency_symbol}{Math.round(data.salary / 12).toLocaleString()} / mo
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Quantile Percentiles Table */}
                  <h4 style={{ fontSize: '0.95rem', fontWeight: 700, margin: '0 0 0.75rem 0', color: '#374151' }}>
                    Quantile Benchmark Breakdown
                  </h4>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '0.5rem', textAlign: 'center', background: '#f9fafb', padding: '1rem', borderRadius: '10px' }}>
                    <div>
                      <div style={{ fontSize: '0.75rem', color: '#6b7280', fontWeight: 600 }}>P10 (Entry Floor)</div>
                      <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#111827' }}>
                        {prediction.currency_symbol}{prediction.annual.p10.toLocaleString()}
                      </div>
                    </div>
                    <div>
                      <div style={{ fontSize: '0.75rem', color: '#6b7280', fontWeight: 600 }}>P25 (Lower Mid)</div>
                      <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#111827' }}>
                        {prediction.currency_symbol}{prediction.annual.p25.toLocaleString()}
                      </div>
                    </div>
                    <div>
                      <div style={{ fontSize: '0.75rem', color: '#4f46e5', fontWeight: 700 }}>P50 (Median)</div>
                      <div style={{ fontSize: '1rem', fontWeight: 800, color: '#4f46e5' }}>
                        {prediction.currency_symbol}{prediction.annual.median.toLocaleString()}
                      </div>
                    </div>
                    <div>
                      <div style={{ fontSize: '0.75rem', color: '#6b7280', fontWeight: 600 }}>P75 (Upper Mid)</div>
                      <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#111827' }}>
                        {prediction.currency_symbol}{prediction.annual.p75.toLocaleString()}
                      </div>
                    </div>
                    <div>
                      <div style={{ fontSize: '0.75rem', color: '#6b7280', fontWeight: 600 }}>P90 (Top 10%)</div>
                      <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#111827' }}>
                        {prediction.currency_symbol}{prediction.annual.p90.toLocaleString()}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 2: Progression */}
              {activeTab === 'progression' && (
                <div style={{ background: '#fff', borderRadius: '16px', border: '1px solid #e5e7eb', padding: '1.5rem', marginBottom: '1.5rem' }}>
                  <h3 style={{ fontSize: '1.1rem', fontWeight: 700, margin: '0 0 0.5rem 0', color: '#111827' }}>
                    Projected Career Salary Progression
                  </h3>
                  <p style={{ color: '#6b7280', fontSize: '0.85rem', margin: '0 0 1.5rem 0' }}>
                    Estimated growth based on compound experience accumulation, natural seniority transitions, and continuous skill upskilling.
                  </p>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                    {[
                      { title: 'Current Baseline', key: 'current', yrs: 0, mult: 0 },
                      { title: '+1 Year Horizon', key: 'year_1', yrs: 1 },
                      { title: '+3 Year Horizon', key: 'year_3', yrs: 3 },
                      { title: '+5 Year Horizon', key: 'year_5', yrs: 5 },
                    ].map((step, idx) => {
                      const item = idx === 0 ? null : prediction.progression[step.key];
                      const sal = idx === 0 ? prediction.annual.median : item.estimated_salary;
                      const growth = idx === 0 ? 0 : item.growth_percent;
                      return (
                        <div
                          key={step.key}
                          style={{
                            padding: '1.25rem',
                            borderRadius: '12px',
                            background: idx === 0 ? '#f9fafb' : '#f0fdf4',
                            border: `1px solid ${idx === 0 ? '#e5e7eb' : '#bbf7d0'}`
                          }}
                        >
                          <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#4b5563', marginBottom: '0.35rem' }}>
                            {step.title}
                          </div>
                          <div style={{ fontSize: '1.35rem', fontWeight: 800, color: '#111827', marginBottom: '0.35rem' }}>
                            {prediction.currency_symbol}{sal.toLocaleString()}
                          </div>
                          {idx > 0 && (
                            <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#16a34a' }}>
                              +{growth}% estimated gain
                            </div>
                          )}
                          <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.35rem' }}>
                            {prediction.currency_symbol}{Math.round(sal / 12).toLocaleString()} / month
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Tab 3: Influencing Factors */}
              {activeTab === 'factors' && (
                <div style={{ background: '#fff', borderRadius: '16px', border: '1px solid #e5e7eb', padding: '1.5rem', marginBottom: '1.5rem' }}>
                  <h3 style={{ fontSize: '1.1rem', fontWeight: 700, margin: '0 0 1rem 0', color: '#111827' }}>
                    Key Weighting Factors in Your Estimate
                  </h3>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
                    {prediction.influential_factors.map((f, i) => (
                      <div key={i} style={{ padding: '1rem', borderRadius: '10px', background: '#f9fafb', border: '1px solid #e5e7eb' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                          <span style={{ fontSize: '0.9rem', fontWeight: 700, color: '#1f2937' }}>{f.factor}</span>
                          <span style={{ fontSize: '0.9rem', fontWeight: 800, color: '#4f46e5' }}>{f.impact}</span>
                        </div>
                        <p style={{ margin: 0, fontSize: '0.8rem', color: '#6b7280' }}>{f.description}</p>
                      </div>
                    ))}
                  </div>

                  {prediction.applied_skill_premiums.length > 0 && (
                    <div>
                      <h4 style={{ fontSize: '0.9rem', fontWeight: 700, margin: '0 0 0.5rem 0', color: '#374151' }}>
                        Verified High-Impact Skill Premiums
                      </h4>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                        {prediction.applied_skill_premiums.map((sk, idx) => (
                          <span
                            key={idx}
                            style={{
                              padding: '5px 12px',
                              background: '#ecfdf5',
                              border: '1px solid #a7f3d0',
                              color: '#065f46',
                              borderRadius: '999px',
                              fontSize: '0.82rem',
                              fontWeight: 600
                            }}
                          >
                            {sk.skill}: +{sk.boost_percent}%
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Tax & Take-Home Pay Explicit Disclaimer */}
              <div style={{ background: '#fffbeb', border: '1px solid #fef3c7', borderRadius: '12px', padding: '1rem 1.25rem', display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                <span style={{ color: '#b45309', display: 'inline-flex', marginTop: '2px', flexShrink: 0 }}>
                  <AlertIcon />
                </span>
                <div style={{ fontSize: '0.82rem', color: '#92400e', lineHeight: 1.5 }}>
                  <strong>Gross Compensation vs. Net Take-Home Pay:</strong> {prediction.tax_disclaimer}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SalaryPredictionPage;
