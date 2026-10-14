import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useJobContext } from '../context/JobContext';
import { resumeAPI, userAPI, aiAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import RecommendedJobs from '../components/RecommendedJobs';

const Dashboard = () => {
  const { user, setUser } = useAuth();
  const { refreshLiveJobs } = useJobContext();
  const [resumes, setResumes] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [aiStatus, setAiStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState('');

  // Profile editing state
  const [editingProfile, setEditingProfile] = useState(false);
  const [savingProfile, setSavingProfile] = useState(false);
  const [profileForm, setProfileForm] = useState({
    education: user?.education || "Bachelor's Degree",
    degree: user?.degree || '',
    preferred_job_role: user?.preferred_job_role || '',
    preferred_location: user?.preferred_location || '',
    experience_level: user?.experience_level || 'Fresher',
  });

  const latestResume = resumes.length > 0 ? resumes[0] : null;

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const resResponse = await resumeAPI.getMyResumes();
        if (resResponse.success) {
          const list = resResponse.data.resumes || [];
          setResumes(list);

          if (list.length > 0) {
            const firstResumeId = list[0].id;
            try {
              const analysisRes = await resumeAPI.getResumeAnalysis(firstResumeId);
              if (analysisRes.success && analysisRes.data.analysis) {
                setAnalysis(analysisRes.data.analysis);
              }
            } catch (err) {
              // Analysis not yet generated for this resume
              setAnalysis(null);
            }
          }
        }

        // Fetch AI Semantic Model Status
        try {
          const aiRes = await aiAPI.getAIStatus();
          if (aiRes.success && aiRes.data) {
            setAiStatus(aiRes.data);
          }
        } catch (aiErr) {
          console.log("AI Status endpoint not ready yet or disabled");
        }
      } catch (err) {
        console.error("Failed to fetch resumes:", err);
        setError("Unable to load latest resume information.");
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const handleTriggerAnalysis = async () => {
    if (!latestResume) return;
    setAnalyzing(true);
    setError('');

    try {
      const response = await resumeAPI.analyzeResume(latestResume.id);
      if (response.data && response.data.analysis) {
        setAnalysis(response.data.analysis);
        refreshLiveJobs(true);
      } else {
        setError(response.message || "Failed to analyze resume.");
      }
    } catch (err) {
      console.error("Analysis error:", err);
      if (err.response?.data?.data?.analysis) {
        setAnalysis(err.response.data.data.analysis);
      } else {
        const msg = err.response?.data?.message || err.message || "Error during resume analysis.";
        setError(msg);
      }
    } finally {
      setAnalyzing(false);
    }
  };

  const handleProfileChange = (e) => {
    setProfileForm({
      ...profileForm,
      [e.target.name]: e.target.value,
    });
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setSavingProfile(true);
    try {
      const response = await userAPI.updateProfile(profileForm);
      if (response.success && response.data.user) {
        setUser(response.data.user);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        setEditingProfile(false);
      }
    } catch (err) {
      console.error("Failed to update profile:", err);
      alert("Failed to save profile changes. Please try again.");
    } finally {
      setSavingProfile(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'var(--accent-green)';
    if (score >= 65) return 'var(--primary)';
    if (score >= 50) return 'var(--accent-warning)';
    return 'var(--accent-pink)';
  };

  const getScoreTier = (score) => {
    if (score >= 85) return 'Excellent';
    if (score >= 70) return 'Good';
    if (score >= 50) return 'Average';
    return 'Needs Improvement';
  };

  if (loading) {
    return <LoadingSpinner text="Loading candidate dashboard..." />;
  }

  return (
    <div className="container" style={{ padding: '2.5rem 1.5rem 4rem' }}>
      {/* Welcome Banner */}
      <div className="dash-welcome glass-card" style={{ marginBottom: '1.75rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
            {user?.profile_picture ? (
              <img
                src={user.profile_picture}
                alt={user.name}
                style={{ width: '64px', height: '64px', borderRadius: '50%', border: '2px solid var(--primary)', objectFit: 'cover' }}
              />
            ) : (
              <div style={{ width: '64px', height: '64px', borderRadius: '50%', background: 'var(--primary-glow)', border: '2px solid var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem', color: 'var(--primary)' }}>
                {user?.name?.charAt(0).toUpperCase() || 'U'}
              </div>
            )}
            <div>
              <h1 style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '0.25rem' }}>
                Welcome back, {user?.name?.split(' ')[0] || 'Candidate'} 👋
              </h1>
              <p style={{ color: 'var(--text-muted)', fontSize: '1.05rem' }}>
                Signed in via <span className="badge badge-primary" style={{ textTransform: 'capitalize' }}>{user?.auth_provider || 'local'}</span> authentication
              </p>
            </div>
          </div>
          
          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            <Link to="/resume-upload" className="btn btn-secondary">
              Upload Resume
            </Link>
            {latestResume && !analysis && (
              <button onClick={handleTriggerAnalysis} className="btn btn-primary" disabled={analyzing}>
                {analyzing ? 'Analyzing...' : 'Analyze Resume'}
              </button>
            )}
          </div>
        </div>
      </div>

      {error && (
        <div className="alert alert-danger" style={{ marginBottom: '1.75rem' }}>
          {error}
        </div>
      )}

      {/* Main Layout Grid */}
      <div className="dashboard-grid" style={{ padding: 0 }}>
        {/* Profile Card */}
        <div className="dash-profile glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: 'var(--primary-glow)', color: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                  <circle cx="12" cy="7" r="4" />
                </svg>
              </div>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Profile Details</h3>
            </div>
            <button
              onClick={() => setEditingProfile(!editingProfile)}
              className="btn btn-secondary"
              style={{ padding: '0.35rem 0.8rem', fontSize: '0.8rem' }}
            >
              {editingProfile ? 'Cancel' : 'Edit Profile'}
            </button>
          </div>

          {editingProfile ? (
            <form onSubmit={handleSaveProfile} style={{ display: 'flex', flexDirection: 'column', gap: '0.9rem' }}>
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label" style={{ fontSize: '0.8rem' }}>Education</label>
                <select name="education" className="form-select" value={profileForm.education} onChange={handleProfileChange}>
                  <option value="Trade Certificate / ITI">Trade Certificate / ITI / Apprenticeship</option>
                  <option value="Vocational Diploma">Vocational / Technical Diploma</option>
                  <option value="Associate Degree">Associate Degree (AAS / AS)</option>
                  <option value="Bachelor's Degree">Bachelor's Degree (B.Sc / B.Tech / B.A / B.Com / BSN)</option>
                  <option value="Master's Degree">Master's Degree (M.Sc / M.Tech / M.A / MBA / MSN)</option>
                  <option value="High School / Secondary">High School / Secondary</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label" style={{ fontSize: '0.8rem' }}>Degree / Field of Study</label>
                <input type="text" name="degree" className="form-input" placeholder="e.g. Electrical, Nursing, Accounting, CS" value={profileForm.degree} onChange={handleProfileChange} />
              </div>

              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label" style={{ fontSize: '0.8rem' }}>Preferred Job Role</label>
                <input type="text" name="preferred_job_role" className="form-input" placeholder="e.g. Electrician, Staff Nurse, Accountant, Developer" value={profileForm.preferred_job_role} onChange={handleProfileChange} />
              </div>

              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label" style={{ fontSize: '0.8rem' }}>Preferred Location</label>
                <input type="text" name="preferred_location" className="form-input" value={profileForm.preferred_location} onChange={handleProfileChange} />
              </div>

              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label" style={{ fontSize: '0.8rem' }}>Experience Level</label>
                <select name="experience_level" className="form-select" value={profileForm.experience_level} onChange={handleProfileChange}>
                  <option value="Student">Student</option>
                  <option value="Fresher">Fresher</option>
                  <option value="0–2 Years">0–2 Years</option>
                  <option value="2–5 Years">2–5 Years</option>
                  <option value="5+ Years">5+ Years</option>
                </select>
              </div>

              <button type="submit" className="btn btn-primary" disabled={savingProfile} style={{ marginTop: '0.5rem', padding: '0.5rem' }}>
                {savingProfile ? 'Saving...' : 'Save Changes'}
              </button>
            </form>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', fontSize: '0.925rem' }}>
              <div>
                <div style={{ color: 'var(--text-subtle)', fontSize: '0.8rem', fontWeight: 600 }}>FULL NAME</div>
                <div style={{ fontWeight: 600 }}>{user?.name || '—'}</div>
              </div>
              <div>
                <div style={{ color: 'var(--text-subtle)', fontSize: '0.8rem', fontWeight: 600 }}>EMAIL ADDRESS</div>
                <div style={{ fontWeight: 600 }}>{user?.email || '—'}</div>
              </div>
              <div>
                <div style={{ color: 'var(--text-subtle)', fontSize: '0.8rem', fontWeight: 600 }}>EDUCATION</div>
                <div style={{ fontWeight: 600 }}>
                  {user?.education ? `${user.education}${user.degree ? ` (${user.degree})` : ''}` : <span style={{ color: 'var(--accent-pink)' }}>Not set — Click Edit Profile</span>}
                </div>
              </div>
              <div>
                <div style={{ color: 'var(--text-subtle)', fontSize: '0.8rem', fontWeight: 600 }}>PREFERRED ROLE</div>
                <div style={{ fontWeight: 600, color: 'var(--accent-cyan)' }}>
                  {user?.preferred_job_role || <span style={{ color: 'var(--accent-pink)' }}>Not set</span>}
                </div>
              </div>
              <div>
                <div style={{ color: 'var(--text-subtle)', fontSize: '0.8rem', fontWeight: 600 }}>PREFERRED LOCATION</div>
                <div style={{ fontWeight: 600 }}>{user?.preferred_location || 'Not set'}</div>
              </div>
              <div>
                <div style={{ color: 'var(--text-subtle)', fontSize: '0.8rem', fontWeight: 600 }}>EXPERIENCE LEVEL</div>
                <div><span className="badge badge-primary">{user?.experience_level || 'Fresher'}</span></div>
              </div>
            </div>
          )}
        </div>

        {/* Latest Resume Card & Analysis Action */}
        <div className="dash-resume glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <div style={{ width: '40px', height: '40px', borderRadius: 'var(--radius-md)', background: 'rgba(16, 185, 129, 0.15)', color: 'var(--accent-green)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                </svg>
              </div>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Resume Status</h3>
            </div>
            <Link to="/resume-upload" className="btn btn-secondary" style={{ padding: '0.45rem 1rem', fontSize: '0.85rem' }}>
              Upload New Resume
            </Link>
          </div>

          {latestResume ? (
            <div style={{ background: 'var(--bg-input)', borderRadius: 'var(--radius-md)', padding: '1.25rem', border: '1px solid var(--border-color)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
                <div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-subtle)', fontWeight: 600 }}>LATEST RESUME FILE</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff', marginTop: '0.2rem' }}>
                    {latestResume.original_filename}
                  </div>
                  <div style={{ fontSize: '0.825rem', color: 'var(--text-muted)', marginTop: '0.4rem' }}>
                    Uploaded on: {new Date(latestResume.uploaded_at).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })}
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <span className={`badge ${analysis ? 'badge-success' : 'badge-primary'}`} style={{ fontSize: '0.85rem', padding: '0.4rem 0.85rem', marginBottom: '0.5rem', display: 'inline-block' }}>
                    Status: {analysis ? 'Analyzed ✓' : 'Uploaded ✓'}
                  </span>
                  <div>
                    <button
                      onClick={handleTriggerAnalysis}
                      className="btn btn-primary"
                      disabled={analyzing}
                      style={{ padding: '0.45rem 1.1rem', fontSize: '0.85rem' }}
                    >
                      {analyzing ? 'Analyzing Resume...' : analysis ? 'Re-Analyze Resume' : 'Analyze Resume'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '2rem 1rem', background: 'var(--bg-input)', borderRadius: 'var(--radius-md)', border: '1px dashed var(--border-color)' }}>
              <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>
                No resume uploaded yet. Upload your PDF resume to initialize your candidate profile.
              </p>
              <Link to="/resume-upload" className="btn btn-primary" style={{ padding: '0.5rem 1.25rem', fontSize: '0.9rem' }}>
                Upload Resume Now
              </Link>
            </div>
          )}
        </div>

        {/* --- RESUME INTELLIGENCE ANALYTICS SECTION --- */}
        {analyzing ? (
          <div className="glass-card" style={{ gridColumn: 'span 12', padding: '3rem 1.5rem', textAlign: 'center' }}>
            <LoadingSpinner text="Extracting PDF text and validating resume structure..." />
          </div>
        ) : analysis && (analysis.validation_status !== "VALID_RESUME" || analysis.resume_score === null) ? (
          <div className="glass-card" style={{ gridColumn: 'span 12', padding: '2.5rem 1.5rem', textAlign: 'center', border: '1px solid var(--accent-pink)' }}>
            <div style={{ width: '60px', height: '60px', borderRadius: '50%', background: 'rgba(239, 68, 68, 0.15)', color: 'var(--accent-pink)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.25rem', fontSize: '1.75rem' }}>
              ⚠️
            </div>
            <h3 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--accent-pink)', marginBottom: '0.5rem' }}>
              Resume / CV Not Recognized
            </h3>
            <p style={{ color: 'var(--text-muted)', maxWidth: '600px', margin: '0 auto 1.25rem', fontSize: '1.025rem' }}>
              {analysis.validation_reason || "The uploaded document does not contain essential resume sections and cannot be analyzed or scored."}
            </p>
            <div style={{ background: 'var(--bg-input)', padding: '1rem', borderRadius: 'var(--radius-md)', maxWidth: '500px', margin: '0 auto 1.5rem', textAlign: 'left', border: '1px solid var(--border-color)' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-subtle)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '0.35rem' }}>
                DOCUMENT TYPE DETECTED
              </div>
              <div style={{ fontSize: '1rem', fontWeight: 700, color: '#fff', marginBottom: '0.5rem' }}>
                {analysis.document_type || 'NON_RESUME'}
              </div>
              {analysis.negative_signals && analysis.negative_signals.length > 0 && (
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--accent-warning)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '0.25rem' }}>
                    NON-RESUME SIGNALS DETECTED
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                    {analysis.negative_signals.map(sig => (
                      <span key={sig} className="badge badge-warning" style={{ fontSize: '0.75rem' }}>
                        {sig.replace(/_/g, ' ')}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
            <Link to="/resume-upload" className="btn btn-primary" style={{ padding: '0.65rem 1.75rem', fontSize: '0.95rem' }}>
              Upload Another Resume PDF
            </Link>
          </div>
        ) : analysis ? (
          <>
            {/* Resume Quality Score Card */}
            <div className="glass-card" style={{ gridColumn: 'span 6' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Resume Quality Score</h3>
                <span className="badge badge-primary">{getScoreTier(analysis.resume_score)}</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem', marginBottom: '1rem' }}>
                <span style={{ fontSize: '3rem', fontWeight: 800, color: getScoreColor(analysis.resume_score) }}>
                  {analysis.resume_score}
                </span>
                <span style={{ fontSize: '1.25rem', color: 'var(--text-subtle)', fontWeight: 600 }}>/ 100</span>
              </div>
              <div style={{ width: '100%', height: '8px', background: 'var(--bg-input)', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{ width: `${analysis.resume_score}%`, height: '100%', background: getScoreColor(analysis.resume_score), transition: 'width 0.8s ease' }}></div>
              </div>
            </div>

            {/* ATS Compatibility Score Card */}
            <div className="glass-card" style={{ gridColumn: 'span 6' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>ATS Compatibility Score</h3>
                <span className="badge badge-success">ATS Engine</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem', marginBottom: '1rem' }}>
                <span style={{ fontSize: '3rem', fontWeight: 800, color: getScoreColor(analysis.ats_score) }}>
                  {analysis.ats_score}
                </span>
                <span style={{ fontSize: '1.25rem', color: 'var(--text-subtle)', fontWeight: 600 }}>/ 100</span>
              </div>
              <div style={{ width: '100%', height: '8px', background: 'var(--bg-input)', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{ width: `${analysis.ats_score}%`, height: '100%', background: getScoreColor(analysis.ats_score), transition: 'width 0.8s ease' }}></div>
              </div>
            </div>

            {/* Score Breakdown Cards */}
            <div className="glass-card" style={{ gridColumn: 'span 12' }}>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '1.25rem' }}>Detailed Score Breakdown</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
                {analysis.score_breakdown && Object.entries({
                  'Contact Information': { val: analysis.score_breakdown.contact, max: 10 },
                  'Education': { val: analysis.score_breakdown.education, max: 10 },
                  'Technical Skills': { val: analysis.score_breakdown.technical_skills, max: 20 },
                  'Projects': { val: analysis.score_breakdown.projects, max: 20 },
                  'Certifications': { val: analysis.score_breakdown.certifications, max: 10 },
                  'Experience': { val: analysis.score_breakdown.experience, max: 15 },
                  'Structure': { val: analysis.score_breakdown.structure, max: 10 },
                  'Keywords': { val: analysis.score_breakdown.keywords, max: 5 }
                }).map(([label, item]) => (
                  <div key={label} style={{ background: 'var(--bg-input)', padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem', fontSize: '0.85rem' }}>
                      <span style={{ fontWeight: 600, color: 'var(--text-muted)' }}>{label}</span>
                      <span style={{ fontWeight: 700, color: '#fff' }}>{item.val} / {item.max}</span>
                    </div>
                    <div style={{ width: '100%', height: '6px', background: 'var(--bg-card)', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{ width: `${(item.val / item.max) * 100}%`, height: '100%', background: 'var(--primary)' }}></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Extracted Technical & Soft Skills */}
            <div className="glass-card" style={{ gridColumn: 'span 12' }}>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '1.25rem' }}>Extracted Skill Inventory</h3>
              {analysis.categorized_technical_skills && Object.keys(analysis.categorized_technical_skills).length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                  {Object.entries(analysis.categorized_technical_skills).map(([cat, skills]) => (
                    <div key={cat}>
                      <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--accent-cyan)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.5rem' }}>
                        {cat.replace(/_/g, ' ')}
                      </div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                        {skills.map((sk) => (
                          <span key={sk} className="badge badge-primary" style={{ fontSize: '0.85rem', padding: '0.35rem 0.75rem' }}>
                            {sk}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              ) : analysis.technical_skills && analysis.technical_skills.length > 0 ? (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                  {analysis.technical_skills.map((sk) => (
                    <span key={sk} className="badge badge-primary" style={{ fontSize: '0.85rem', padding: '0.35rem 0.75rem' }}>
                      {sk}
                    </span>
                  ))}
                </div>
              ) : (
                <p style={{ color: 'var(--text-muted)' }}>No technical skills detected in resume text.</p>
              )}

              {analysis.soft_skills && analysis.soft_skills.length > 0 && (
                <div style={{ marginTop: '1.5rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
                  <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--accent-purple)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.5rem' }}>
                    SOFT SKILLS
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {analysis.soft_skills.map((sk) => (
                      <span key={sk} className="badge badge-success" style={{ fontSize: '0.85rem', padding: '0.35rem 0.75rem' }}>
                        {sk}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Strengths & Recommendations */}
            <div className="glass-card" style={{ gridColumn: 'span 6' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--accent-green)" strokeWidth="2.5">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--accent-green)' }}>Profile Strengths</h3>
              </div>
              {analysis.strengths && analysis.strengths.length > 0 ? (
                <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {analysis.strengths.map((str, idx) => (
                    <li key={idx} style={{ background: 'rgba(16, 185, 129, 0.1)', padding: '0.75rem 1rem', borderRadius: 'var(--radius-md)', borderLeft: '3px solid var(--accent-green)', fontSize: '0.9rem' }}>
                      ✓ {str}
                    </li>
                  ))}
                </ul>
              ) : (
                <p style={{ color: 'var(--text-muted)' }}>No notable strengths generated yet.</p>
              )}
            </div>

            <div className="glass-card" style={{ gridColumn: 'span 6' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--accent-warning)" strokeWidth="2.5">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="8" x2="12" y2="12" />
                  <line x1="12" y1="16" x2="12.01" y2="16" />
                </svg>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--accent-warning)' }}>Actionable Recommendations</h3>
              </div>
              {analysis.improvements && analysis.improvements.length > 0 ? (
                <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {analysis.improvements.map((imp, idx) => (
                    <li key={idx} style={{ background: 'rgba(245, 158, 11, 0.1)', padding: '0.75rem 1rem', borderRadius: 'var(--radius-md)', borderLeft: '3px solid var(--accent-warning)', fontSize: '0.9rem' }}>
                      💡 {imp}
                    </li>
                  ))}
                </ul>
              ) : (
                <p style={{ color: 'var(--text-muted)' }}>Great job! No urgent recommendations found.</p>
              )}
            </div>
          </>
        ) : (
          /* Placeholder when resume uploaded but not yet analyzed */
          <div className="dash-metrics glass-card" style={{ gridColumn: 'span 12', textAlign: 'center', padding: '3rem 1.5rem' }}>
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" strokeWidth="1.5" style={{ marginBottom: '1rem' }}>
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
            </svg>
            <h3 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '0.5rem' }}>Ready for Resume Intelligence Analysis</h3>
            <p style={{ color: 'var(--text-muted)', maxWidth: '550px', margin: '0 auto 1.5rem' }}>
              Click <strong>Analyze Resume</strong> to trigger PDF text extraction, skill parsing, deterministic Quality & ATS scoring, and actionable recommendations.
            </p>
            {latestResume ? (
              <button onClick={handleTriggerAnalysis} className="btn btn-primary" disabled={analyzing} style={{ padding: '0.75rem 2rem', fontSize: '1rem' }}>
                {analyzing ? 'Analyzing Resume...' : 'Analyze Resume Now'}
              </button>
            ) : (
              <Link to="/resume-upload" className="btn btn-primary" style={{ padding: '0.75rem 2rem', fontSize: '1rem' }}>
                Upload Resume PDF
              </Link>
            )}
          </div>
        )}

        {/* AI Semantic Intelligence Layer Status Card */}
        {aiStatus && aiStatus.ai_available && (
          <div className="glass-card" style={{ gridColumn: 'span 12', background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(168, 85, 247, 0.08) 100%)', border: '1px solid rgba(168, 85, 247, 0.3)', padding: '1.5rem', marginBottom: '0.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div style={{ width: '44px', height: '44px', borderRadius: '12px', background: 'linear-gradient(135deg, #6366f1, #a855f7)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.25rem', fontWeight: 800 }}>
                  ✨
                </div>
                <div>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 800, margin: 0, background: 'linear-gradient(135deg, #818cf8, #c084fc)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                    AI/NLP Semantic Intelligence Layer Active
                  </h3>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', margin: '0.2rem 0 0' }}>
                    Using <strong>{aiStatus.model_name}</strong> on CPU for 384-dim vector embeddings and cosine similarity scoring.
                  </p>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', flexWrap: 'wrap' }}>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', fontWeight: 700 }}>COMBINED MATCH FORMULA</div>
                  <div style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>
                    0.60 × Deterministic + 0.40 × AI Semantic
                  </div>
                </div>
                <span className="badge badge-success" style={{ fontSize: '0.85rem', padding: '0.4rem 0.85rem' }}>
                  ✓ Model Online
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Recommended Jobs Section */}
        <RecommendedJobs resumeAnalyzed={analysis && analysis.validation_status === "VALID_RESUME" && analysis.resume_score !== null} />
      </div>
    </div>
  );
};

export default Dashboard;
