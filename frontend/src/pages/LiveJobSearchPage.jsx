import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useJobContext } from '../context/JobContext';
import { useAuth } from '../context/AuthContext';
import { jobAPI } from '../services/api';
import LiveJobCard from '../components/LiveJobCard';
import JobMatchModal from '../components/JobMatchModal';
import LoadingSpinner from '../components/LoadingSpinner';

const MULTI_PROFESSION_ROLES = [
  // A. Artificial Intelligence & Machine Learning
  "AI Engineer",
  "Machine Learning Engineer",
  "Applied AI Engineer",
  "Generative AI Engineer",
  "NLP Engineer",
  "Computer Vision Engineer",
  "MLOps Engineer",
  "Research Engineer",

  // B. Data Science & Analytics
  "Data Scientist",
  "Junior Data Scientist",
  "Data Analyst",
  "Business Intelligence Analyst",
  "BI Developer",
  "Business Analyst",
  "Reporting Analyst",
  "Data Engineer",
  "Analytics Engineer",

  // C. Software Development
  "Software Developer",
  "Software Engineer",
  "Application Developer",
  "Junior Software Engineer",
  "Graduate Software Engineer",

  // D. Full Stack Development
  "Full Stack Developer",
  "MERN Stack Developer",
  "MEAN Stack Developer",
  "React and Node.js Developer",
  "Java Full Stack Developer",
  "Python Full Stack Developer",

  // E. Frontend Development
  "Frontend Developer",
  "React Developer",
  "Angular Developer",
  "Vue.js Developer",
  "UI Engineer",

  // F. Backend Development
  "Backend Developer",
  "Python Developer",
  "Java Developer",
  "Node.js Developer",
  "API Developer",
  ".NET Developer",
  "PHP Developer",

  // G. Cloud & Infrastructure
  "DevOps Engineer",
  "Cloud Engineer",
  "AWS Engineer",
  "Azure Engineer",
  "Platform Engineer",
  "Site Reliability Engineer",
  "Infrastructure Engineer",

  // H. Cybersecurity
  "Security Analyst",
  "SOC Analyst",
  "Cybersecurity Analyst",
  "Penetration Tester",
  "Security Engineer",
  "Vulnerability Analyst",
  "Incident Response Analyst",

  // I. Other Technology Roles
  "QA Engineer",
  "Software Tester",
  "Automation Test Engineer",
  "Database Administrator",
  "Network Engineer",
  "IT Support Engineer",
  "Mobile App Developer",
  "Embedded Systems Engineer",

  // J. Skilled Trades
  "Electrician",
  "Electrical Technician",
  "Electrical Maintenance Technician",
  "Industrial Electrician",
  "Plumber",
  "Welder",
  "HVAC Technician",
  "Mechanical Technician",
  "Automotive Mechanic",
  "Maintenance Technician",

  // K. Healthcare
  "Registered Nurse",
  "Staff Nurse",
  "Nursing Assistant",
  "Caregiver",
  "Medical Laboratory Technician",
  "Radiology Technician",
  "Clinical Assistant",
  "Healthcare Administrator",

  // L. Business & Finance
  "Accountant",
  "Accounts Executive",
  "Bookkeeper",
  "Financial Analyst",
  "Auditor",
  "Tax Associate",
  "Payroll Specialist",
  "HR Executive",
  "Recruiter",
  "Administrative Assistant",

  // M. Education
  "School Teacher",
  "Subject Teacher",
  "Tutor",
  "Academic Instructor",
  "Trainer",
  "Teaching Assistant",

  // N. Other Sectors
  "Chef",
  "Forklift Operator",
  "Warehouse Associate",
  "Carpenter",
  "Sales Executive",
  "Digital Marketing Specialist",
  "Mechanical Engineer",
  "Civil Engineer",
  "Electrical Engineer"
];

const LiveJobSearchPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  const {
    liveJobsData,
    candidateProfile,
    lastUpdatedAt,
    buckets,
    filters,
    setFilters,
    loading,
    refreshing,
    error,
    resumeRequired,
    savedJobIds,
    fetchLiveJobs,
    refreshLiveJobs,
    toggleSaveJob
  } = useJobContext();

  const { selectedRole, location, remote, experience, minMatch, activeTab } = filters;
  const [selectedMatch, setSelectedMatch] = useState(null);

  const candidateRoles = [
    candidateProfile?.target_role,
    candidateProfile?.primary_search_keyword,
    ...(candidateProfile?.inferred_roles || []),
    ...(candidateProfile?.primary_roles || []),
    ...(candidateProfile?.alternative_roles || [])
  ].filter(Boolean);

  const availableRoles = Array.from(new Set([
    ...candidateRoles,
    ...(user?.preferred_job_role ? [user.preferred_job_role] : []),
    ...MULTI_PROFESSION_ROLES
  ].filter(Boolean)));

  // Initial load: fetch once on mount if liveJobsData is not already cached in context
  const hasInitialFetchedRef = useRef(false);
  useEffect(() => {
    if (!hasInitialFetchedRef.current) {
      hasInitialFetchedRef.current = true;
      if (!liveJobsData && !loading) {
        fetchLiveJobs();
      }
    }
  }, [fetchLiveJobs, liveJobsData, loading]);

  // Debounced search when user modifies filters
  const isFirstMountRef = useRef(true);
  useEffect(() => {
    if (isFirstMountRef.current) {
      isFirstMountRef.current = false;
      return;
    }

    const timer = setTimeout(() => {
      fetchLiveJobs();
    }, 400);

    return () => clearTimeout(timer);
  }, [selectedRole, location, remote, experience, minMatch]);

  const handleFilterChange = (field, value) => {
    setFilters({ [field]: value });
  };

  const handleViewMatch = async (jobId) => {
    try {
      const response = await jobAPI.getJobMatch(jobId);
      if (response.success && response.data) {
        setSelectedMatch(response.data);
      }
    } catch (err) {
      console.error("Failed to fetch match analysis:", err);
      alert("Unable to load detailed match analysis.");
    }
  };

  const handleSaveJob = (jobId, action) => {
    toggleSaveJob(jobId, action);
  };

  const handleOpenRoadmap = (job) => {
    const jobId = job.job_id || job._id;
    navigate(`/dashboard/roadmap/${jobId}`);
  };

  const displayedJobs = activeTab === 'highly'
    ? buckets.highly_relevant
    : activeTab === 'relevant'
    ? buckets.relevant
    : activeTab === 'potential'
    ? buckets.potential
    : buckets.all_recommendations;

  return (
    <div className="container" style={{ padding: '2.5rem 1.5rem 4rem' }}>
      {/* Header */}
      <div style={{ marginBottom: '1.75rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ fontSize: '0.85rem', color: 'var(--accent-cyan)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            AUTOMATED RESUME-BASED LIVE JOB DISCOVERY
          </div>
          <h1 style={{ fontSize: '2.25rem', fontWeight: 800, marginTop: '0.2rem', marginBottom: '0.4rem' }}>
            Recommended Live Jobs For You
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '1.05rem', maxWidth: '800px' }}>
            Personalized active job vacancies automatically retrieved and matched against your uploaded resume profile across all professions.
          </p>
        </div>

        {/* Header Action: Visible Refresh Jobs */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          {lastUpdatedAt && (
            <div className="badge badge-success" style={{ fontSize: '0.8rem', padding: '0.45rem 0.8rem' }}>
              ⏱️ {lastUpdatedAt}
            </div>
          )}
          <button
            onClick={() => refreshLiveJobs(true)}
            disabled={refreshing || loading}
            className="btn btn-secondary"
            style={{ fontSize: '0.85rem', padding: '0.45rem 1rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
            title="Force refresh live jobs directly from providers"
          >
            <span style={{ display: 'inline-block', transform: refreshing ? 'rotate(180deg)' : 'none', transition: 'transform 0.5s' }}>
              🔄
            </span>
            {refreshing ? 'Refreshing...' : 'Refresh Jobs'}
          </button>
        </div>
      </div>

      {/* Subtle background refresh status banner */}
      {refreshing && (
        <div style={{
          background: 'rgba(99, 102, 241, 0.12)',
          border: '1px solid rgba(99, 102, 241, 0.35)',
          color: '#818cf8',
          padding: '0.65rem 1rem',
          borderRadius: 'var(--radius-sm)',
          marginBottom: '1.5rem',
          fontSize: '0.875rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          <span>🔄</span>
          <span>Updating live job listings in the background... Current vacancies remain interactable.</span>
        </div>
      )}

      {/* HARD GATE: Resume Required Alert */}
      {resumeRequired ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '3.5rem 2rem', margin: '2rem 0' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📄</div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800, marginBottom: '0.75rem' }}>
            Resume Upload Required
          </h2>
          <p style={{ color: 'var(--text-muted)', maxWidth: '600px', margin: '0 auto 2rem', fontSize: '1.05rem', lineHeight: '1.6' }}>
            To generate personalized live job recommendations, the system needs to analyze your skills, experience, and profession from your uploaded resume.
          </p>
          <button onClick={() => navigate('/resume-upload')} className="btn btn-primary" style={{ padding: '0.75rem 2rem', fontSize: '1rem', fontWeight: 700 }}>
            Upload & Analyze Resume Now ➔
          </button>
        </div>
      ) : (
        <>
          {/* Ambiguity / Multi-Discipline Callout Banner */}
          {candidateProfile?.is_ambiguous && (
            <div style={{
              background: 'rgba(234, 179, 8, 0.1)',
              border: '1px solid rgba(234, 179, 8, 0.35)',
              borderRadius: 'var(--radius-md)',
              padding: '1rem 1.25rem',
              marginBottom: '1.5rem',
              color: '#fef08a'
            }}>
              <div style={{ fontWeight: 700, fontSize: '0.95rem', marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span>🎯 Multi-Discipline Profile Detected:</span>
                <span style={{ fontWeight: 500, color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                  Your resume demonstrates competencies across multiple domains. Select your target domain below to refine live recommendations:
                </span>
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.5rem' }}>
                {candidateProfile.primary_roles?.slice(0, 3).map(role => (
                  <button
                    key={role}
                    onClick={() => handleFilterChange('selectedRole', role)}
                    className="btn btn-secondary"
                    style={{
                      fontSize: '0.8rem',
                      padding: '0.3rem 0.75rem',
                      border: selectedRole === role ? '1px solid var(--accent-cyan)' : '1px solid rgba(255,255,255,0.2)',
                      background: selectedRole === role ? 'rgba(6, 182, 212, 0.2)' : 'rgba(255,255,255,0.05)',
                      color: selectedRole === role ? '#fff' : 'var(--text-main)',
                      fontWeight: 600
                    }}
                  >
                    🎯 Focus: {role}
                  </button>
                ))}
                {candidateProfile.alternative_professions?.map(alt => (
                  <button
                    key={alt.primary_role}
                    onClick={() => handleFilterChange('selectedRole', alt.primary_role)}
                    className="btn btn-secondary"
                    style={{
                      fontSize: '0.8rem',
                      padding: '0.3rem 0.75rem',
                      border: selectedRole === alt.primary_role ? '1px solid var(--accent-cyan)' : '1px solid rgba(255,255,255,0.2)',
                      background: selectedRole === alt.primary_role ? 'rgba(6, 182, 212, 0.2)' : 'rgba(255,255,255,0.05)',
                      color: selectedRole === alt.primary_role ? '#fff' : 'var(--text-main)',
                      fontWeight: 600
                    }}
                  >
                    🌟 Explore: {alt.primary_role}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Candidate Profile Summary Banner */}
          {candidateProfile && (
            <div className="glass-card" style={{ marginBottom: '1.75rem', padding: '1.5rem', background: 'linear-gradient(135deg, rgba(99,102,241,0.08), rgba(6,182,212,0.08))', border: '1px solid rgba(99,102,241,0.2)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1rem' }}>
                <div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--accent-cyan)', fontWeight: 700, textTransform: 'uppercase' }}>
                    INFERRED CANDIDATE PROFILE
                  </div>
                  <h2 style={{ fontSize: '1.5rem', fontWeight: 800, margin: '0.2rem 0 0.4rem' }}>
                    🎯 {candidateProfile.persona}
                  </h2>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                    Experience Tier: <strong>{candidateProfile.experience_level}</strong> • Education: <strong>{candidateProfile.education}</strong>
                  </div>
                </div>

                <div className="badge badge-primary" style={{ fontSize: '0.8rem', padding: '0.4rem 0.75rem' }}>
                  Target Domain: {candidateProfile.professional_domain?.replace(/_/g, ' ')}
                </div>
              </div>

              {/* Core Skills & Target Roles */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem', borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: '1rem' }}>
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '0.4rem' }}>
                    Extracted Core Professional Skills
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                    {candidateProfile.core_skills?.map(sk => (
                      <span key={sk} className="badge badge-primary" style={{ fontSize: '0.75rem' }}>
                        {sk}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '0.4rem' }}>
                    Inferred Target Roles (Click to focus search)
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                    {candidateProfile.inferred_roles?.map(r => (
                      <button
                        key={r}
                        onClick={() => handleFilterChange('selectedRole', r)}
                        style={{
                          background: selectedRole === r ? 'var(--accent-cyan)' : 'rgba(6, 182, 212, 0.15)',
                          color: selectedRole === r ? '#000' : 'var(--accent-cyan)',
                          border: 'none',
                          padding: '0.2rem 0.55rem',
                          borderRadius: '4px',
                          fontSize: '0.75rem',
                          fontWeight: 700,
                          cursor: 'pointer'
                        }}
                        title={`Filter search for ${r}`}
                      >
                        🔍 {r}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Search & Refining Filter Bar */}
          <div className="glass-card" style={{ marginBottom: '1.75rem', padding: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Active Target Role:</span>
              <span className="badge badge-primary" style={{ fontSize: '0.8rem', padding: '0.3rem 0.65rem' }}>
                🎯 {selectedRole || liveJobsData?.target_role || candidateProfile?.inferred_roles?.[0] || 'Auto-Detected Profile Roles'}
              </span>
              {selectedRole && (
                <button
                  onClick={() => handleFilterChange('selectedRole', '')}
                  style={{ background: 'none', border: 'none', color: 'var(--accent-cyan)', fontSize: '0.75rem', cursor: 'pointer', padding: 0, textDecoration: 'underline' }}
                >
                  (Reset Role Filter)
                </button>
              )}
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem' }}>
              {/* Target Role Dropdown */}
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label" style={{ fontSize: '0.8rem' }}>Filter by Target Role</label>
                <select className="form-select" value={selectedRole} onChange={(e) => handleFilterChange('selectedRole', e.target.value)}>
                  <option value="">All Profile Matching Roles</option>
                  {availableRoles.map(r => (
                    <option key={r} value={r}>{r}</option>
                  ))}
                </select>
              </div>

              {/* Location */}
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label" style={{ fontSize: '0.8rem' }}>Location / Country</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="e.g. India, Remote, Worldwide..."
                  value={location}
                  onChange={(e) => handleFilterChange('location', e.target.value)}
                />
              </div>

              {/* Remote / On-Site */}
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label" style={{ fontSize: '0.8rem' }}>Workplace Type</label>
                <select className="form-select" value={remote} onChange={(e) => handleFilterChange('remote', e.target.value)}>
                  <option value="">Any Workplace Type</option>
                  <option value="true">🌐 Remote Only</option>
                  <option value="false">🏢 On-Site / Hybrid</option>
                </select>
              </div>

              {/* Experience */}
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label" style={{ fontSize: '0.8rem' }}>Experience Tier</label>
                <select className="form-select" value={experience} onChange={(e) => handleFilterChange('experience', e.target.value)}>
                  <option value="">Any Experience</option>
                  <option value="fresher">Fresher / Graduate (0–1 yrs)</option>
                  <option value="0-2">Junior (0–2 Years)</option>
                  <option value="2-5">Mid-Level (2–5 Years)</option>
                  <option value="5+">5+ Years</option>
                </select>
              </div>

              {/* Minimum Match % */}
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label" style={{ fontSize: '0.8rem' }}>AI Match Threshold</label>
                <select className="form-select" value={minMatch} onChange={(e) => handleFilterChange('minMatch', e.target.value)}>
                  <option value="">All Match Scores</option>
                  <option value="75">75%+ Highly Relevant</option>
                  <option value="60">60%+ Relevant</option>
                  <option value="40">40%+ Potential</option>
                </select>
              </div>
            </div>
          </div>

          {/* Relevance Bucket Tabs */}
          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
            <button
              onClick={() => handleFilterChange('activeTab', 'all')}
              className={`btn ${activeTab === 'all' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ fontSize: '0.85rem' }}
            >
              📋 All Recommendations ({buckets.all_recommendations?.length || 0})
            </button>
            <button
              onClick={() => handleFilterChange('activeTab', 'highly')}
              className={`btn ${activeTab === 'highly' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ fontSize: '0.85rem' }}
            >
              🌟 Highly Relevant ({buckets.highly_relevant?.length || 0})
            </button>
            <button
              onClick={() => handleFilterChange('activeTab', 'relevant')}
              className={`btn ${activeTab === 'relevant' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ fontSize: '0.85rem' }}
            >
              ⚡ Relevant Jobs ({buckets.relevant?.length || 0})
            </button>
            <button
              onClick={() => handleFilterChange('activeTab', 'potential')}
              className={`btn ${activeTab === 'potential' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ fontSize: '0.85rem' }}
            >
              💡 Potential Jobs ({buckets.potential?.length || 0})
            </button>
          </div>

          {/* Error / Warning Alert */}
          {error && (
            <div className="alert alert-warning" style={{ marginBottom: '1.5rem' }}>
              ⚠️ {error}
            </div>
          )}

          {/* Main Results Grid */}
          {loading && !liveJobsData ? (
            <div className="glass-card" style={{ padding: '3.5rem 1.5rem', textAlign: 'center' }}>
              <LoadingSpinner text={`Retrieving live vacancies and calculating AI match scores for ${selectedRole || 'your target role'}...`} />
            </div>
          ) : displayedJobs && displayedJobs.length > 0 ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
              {displayedJobs.map(job => (
                <LiveJobCard
                  key={job.job_id || job._id}
                  job={job}
                  onViewMatch={handleViewMatch}
                  onSaveJob={handleSaveJob}
                  onOpenRoadmap={handleOpenRoadmap}
                  isSaved={savedJobIds?.has(job.job_id || job._id)}
                />
              ))}
            </div>
          ) : (
            <div className="glass-card" style={{ textAlign: 'center', padding: '3rem 1.5rem' }}>
              <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>🔍</div>
              <h3 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: '0.5rem' }}>No Matching Vacancies Found</h3>
              <p style={{ color: 'var(--text-muted)', maxWidth: '540px', margin: '0 auto 1.5rem', fontSize: '0.95rem', lineHeight: '1.5' }}>
                {selectedRole
                  ? `No verified live vacancies currently matched "${selectedRole}". All listings are queried directly from real providers without fake entries.`
                  : "No active live vacancies matched your selected refining filters. Try clearing your location or experience filters."}
              </p>
              <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                <button
                  onClick={() => setFilters({ selectedRole: '', location: '', remote: '', experience: '', minMatch: '', activeTab: 'all' })}
                  className="btn btn-secondary"
                  style={{ fontSize: '0.85rem' }}
                >
                  Reset All Filters
                </button>
                <button
                  onClick={() => refreshLiveJobs(true)}
                  className="btn btn-primary"
                  style={{ fontSize: '0.85rem' }}
                >
                  🔄 Retry Live Search
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {/* Match Reasons Modal */}
      {selectedMatch && (
        <JobMatchModal
          matchData={selectedMatch}
          onClose={() => setSelectedMatch(null)}
        />
      )}
    </div>
  );
};

export default LiveJobSearchPage;
