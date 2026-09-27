import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { jobAPI } from '../services/api';
import LiveJobCard from '../components/LiveJobCard';
import JobMatchModal from '../components/JobMatchModal';
import LoadingSpinner from '../components/LoadingSpinner';

const LiveJobSearchPage = () => {
  const navigate = useNavigate();
  const [candidateProfile, setCandidateProfile] = useState(null);
  const [lastUpdatedAt, setLastUpdatedAt] = useState('');
  const [buckets, setBuckets] = useState({ highly_relevant: [], relevant: [], potential: [], all_recommendations: [] });
  const [activeTab, setActiveTab] = useState('all');

  const [selectedRole, setSelectedRole] = useState('');
  const [location, setLocation] = useState('');
  const [remote, setRemote] = useState('');
  const [experience, setExperience] = useState('');
  const [minMatch, setMinMatch] = useState('');

  const [loading, setLoading] = useState(true);
  const [resumeRequired, setResumeRequired] = useState(false);
  const [error, setError] = useState('');

  const [selectedMatch, setSelectedMatch] = useState(null);
  const [savedJobIds, setSavedJobIds] = useState(new Set());

  const fetchLiveRecommendations = useCallback(async () => {
    setLoading(true);
    setError('');
    setResumeRequired(false);

    try {
      const params = {
        role: selectedRole || undefined,
        location: location || undefined,
        remote: remote ? remote === 'true' : undefined,
        experience: experience || undefined,
        min_match: minMatch || undefined
      };

      const response = await jobAPI.getLiveJobRecommendations(params);

      if (response.success) {
        setCandidateProfile(response.candidate_profile || null);
        setLastUpdatedAt(response.last_updated_at || '');
        const data = response.data || {};
        setBuckets({
          highly_relevant: data.highly_relevant || [],
          relevant: data.relevant || [],
          potential: data.potential || [],
          all_recommendations: data.all_recommendations || []
        });
      } else {
        if (response.status === 'RESUME_REQUIRED') {
          setResumeRequired(true);
        } else {
          setError(response.message || 'Live job data is currently unavailable. Please try again later.');
        }
      }
    } catch (err) {
      console.error('Failed to fetch recommendations:', err);
      if (err.response && err.response.data && err.response.data.status === 'RESUME_REQUIRED') {
        setResumeRequired(true);
      } else {
        setError('Live job data is currently unavailable. Please try again later.');
      }
    } finally {
      setLoading(false);
    }
  }, [selectedRole, location, remote, experience, minMatch]);

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchLiveRecommendations();
    }, 400);
    return () => clearTimeout(timer);
  }, [fetchLiveRecommendations]);

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

  const handleSaveJob = async (jobId, action) => {
    try {
      const response = await jobAPI.saveJobAction(jobId, action);
      if (response.success) {
        setSavedJobIds(prev => {
          const next = new Set(prev);
          if (action === 'SAVED') next.add(jobId);
          else next.delete(jobId);
          return next;
        });
      }
    } catch (err) {
      console.error("Failed to save job action:", err);
    }
  };

  const handleOpenRoadmap = (job) => {
    const jobId = job.job_id || job._id;
    navigate(`/skills/gap?jobId=${jobId}`);
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
      <div style={{ marginBottom: '1.75rem' }}>
        <div style={{ fontSize: '0.85rem', color: 'var(--accent-cyan)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          AUTOMATED RESUME-BASED LIVE JOB DISCOVERY
        </div>
        <h1 style={{ fontSize: '2.25rem', fontWeight: 800, marginTop: '0.2rem', marginBottom: '0.4rem' }}>
          Recommended Live Jobs For You
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '1.05rem', maxWidth: '800px' }}>
          Personalized active job vacancies automatically retrieved and matched against your uploaded resume profile.
        </p>
      </div>

      {/* HARD GATE: Resume Required Alert */}
      {resumeRequired ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '3.5rem 2rem', margin: '2rem 0' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📄</div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800, marginBottom: '0.75rem' }}>
            Resume Upload Required
          </h2>
          <p style={{ color: 'var(--text-muted)', maxWidth: '600px', margin: '0 auto 2rem', fontSize: '1.05rem', lineHeight: '1.6' }}>
            To generate personalized live job recommendations, the system needs to analyze your technical skills, experience, and domain from your resume.
          </p>
          <button onClick={() => navigate('/resume/upload')} className="btn btn-primary" style={{ padding: '0.75rem 2rem', fontSize: '1rem', fontWeight: 700 }}>
            Upload & Analyze Resume Now ➔
          </button>
        </div>
      ) : (
        <>
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

                {lastUpdatedAt && (
                  <div className="badge badge-success" style={{ fontSize: '0.8rem', padding: '0.4rem 0.75rem' }}>
                    ⏱️ Jobs updated: {lastUpdatedAt}
                  </div>
                )}
              </div>

              {/* Core Skills & Target Roles */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem', borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: '1rem' }}>
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '0.4rem' }}>
                    Extracted Core Technical Skills
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                    {candidateProfile.core_skills.map(sk => (
                      <span key={sk} className="badge badge-primary" style={{ fontSize: '0.75rem' }}>
                        {sk}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '0.4rem' }}>
                    Auto-Searched Target Roles
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                    {candidateProfile.inferred_roles.map(r => (
                      <span key={r} style={{ background: 'rgba(6, 182, 212, 0.15)', color: 'var(--accent-cyan)', padding: '0.2rem 0.55rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600 }}>
                        🔍 {r}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Search & Refining Filter Bar */}
          <div className="glass-card" style={{ marginBottom: '1.75rem', padding: '1.25rem' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem' }}>
              {/* Target Role Dropdown */}
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label" style={{ fontSize: '0.8rem' }}>Filter by Inferred Role</label>
                <select className="form-select" value={selectedRole} onChange={(e) => setSelectedRole(e.target.value)}>
                  <option value="">All Inferred Roles</option>
                  {candidateProfile?.inferred_roles?.map(r => (
                    <option key={r} value={r}>{r}</option>
                  ))}
                </select>
              </div>

              {/* Location */}
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label" style={{ fontSize: '0.8rem' }}>Location / City</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. Chennai, Remote"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                />
              </div>

              {/* Workplace Type */}
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label" style={{ fontSize: '0.8rem' }}>Workplace Type</label>
                <select className="form-select" value={remote} onChange={(e) => setRemote(e.target.value)}>
                  <option value="">All Types</option>
                  <option value="true">Remote Only</option>
                  <option value="false">On-Site / Hybrid</option>
                </select>
              </div>

              {/* Experience */}
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label" style={{ fontSize: '0.8rem' }}>Experience Tier</label>
                <select className="form-select" value={experience} onChange={(e) => setExperience(e.target.value)}>
                  <option value="">All Tiers</option>
                  <option value="fresher">Fresher / Graduate</option>
                  <option value="0-2">0-2 Years</option>
                  <option value="2-5">2-5 Years</option>
                  <option value="5+">5+ Years</option>
                </select>
              </div>

              {/* Minimum Match % */}
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label" style={{ fontSize: '0.8rem' }}>AI Match Threshold</label>
                <select className="form-select" value={minMatch} onChange={(e) => setMinMatch(e.target.value)}>
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
              onClick={() => setActiveTab('all')}
              className={`btn ${activeTab === 'all' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ fontSize: '0.85rem' }}
            >
              📋 All Recommendations ({buckets.all_recommendations.length})
            </button>
            <button
              onClick={() => setActiveTab('highly')}
              className={`btn ${activeTab === 'highly' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ fontSize: '0.85rem' }}
            >
              🌟 Highly Relevant ({buckets.highly_relevant.length})
            </button>
            <button
              onClick={() => setActiveTab('relevant')}
              className={`btn ${activeTab === 'relevant' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ fontSize: '0.85rem' }}
            >
              ⚡ Relevant Jobs ({buckets.relevant.length})
            </button>
            <button
              onClick={() => setActiveTab('potential')}
              className={`btn ${activeTab === 'potential' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ fontSize: '0.85rem' }}
            >
              💡 Potential Jobs ({buckets.potential.length})
            </button>
          </div>

          {/* Error / Warning Alert */}
          {error && (
            <div className="alert alert-warning" style={{ marginBottom: '1.5rem' }}>
              ⚠️ {error}
            </div>
          )}

          {/* Main Results Grid */}
          {loading ? (
            <div className="glass-card" style={{ padding: '3.5rem 1.5rem', textAlign: 'center' }}>
              <LoadingSpinner text="Retrieving live vacancies and calculating 60/40 AI hybrid match scores from your resume..." />
            </div>
          ) : displayedJobs.length > 0 ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
              {displayedJobs.map(job => (
                <LiveJobCard
                  key={job.job_id || job._id}
                  job={job}
                  onViewMatch={handleViewMatch}
                  onSaveJob={handleSaveJob}
                  onOpenRoadmap={handleOpenRoadmap}
                  isSaved={savedJobIds.has(job.job_id || job._id)}
                />
              ))}
            </div>
          ) : (
            <div className="glass-card" style={{ textAlign: 'center', padding: '3rem 1.5rem' }}>
              <h3 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: '0.5rem' }}>No Matching Vacancies Found</h3>
              <p style={{ color: 'var(--text-muted)', maxWidth: '500px', margin: '0 auto 1.5rem' }}>
                No active live vacancies matched your selected refining filters. Try clearing your location or experience filters.
              </p>
              <button onClick={() => { setSelectedRole(''); setLocation(''); setRemote(''); setExperience(''); setMinMatch(''); setActiveTab('all'); }} className="btn btn-secondary">
                Reset Filters
              </button>
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
