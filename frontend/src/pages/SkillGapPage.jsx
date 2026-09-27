import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { skillGapAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';

const SkillGapPage = () => {
  const { jobId } = useParams();
  const [gapData, setGapData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchGapAnalysis = async () => {
      setLoading(true);
      setError('');
      try {
        const response = await skillGapAPI.getSkillGap(jobId);
        if (response.success && response.data.skill_gap) {
          setGapData(response.data.skill_gap);
        } else {
          setError(response.message || "Unable to compute skill gap analysis.");
        }
      } catch (err) {
        console.error("Skill Gap Error:", err);
        const msg = err.response?.data?.message || err.message || "Failed to load skill gap analysis.";
        setError(msg);
      } finally {
        setLoading(false);
      }
    };

    if (jobId) {
      fetchGapAnalysis();
    }
  }, [jobId]);

  if (loading) {
    return (
      <div className="container" style={{ padding: '4rem 1rem', textAlign: 'center' }}>
        <LoadingSpinner text="Evaluating candidate skills against job requirements..." />
      </div>
    );
  }

  if (error || !gapData) {
    return (
      <div className="container" style={{ padding: '3rem 1rem' }}>
        <div className="glass-card" style={{ textAlign: 'center', padding: '2.5rem', border: '1px solid var(--accent-pink)' }}>
          <h3 style={{ color: 'var(--accent-pink)', marginBottom: '1rem' }}>⚠️ Skill Gap Analysis Notice</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>{error}</p>
          <Link to="/dashboard" className="btn btn-primary">Back to Dashboard</Link>
        </div>
      </div>
    );
  }

  const getPriorityBadgeClass = (priority) => {
    switch (priority) {
      case 'CRITICAL': return 'badge badge-pink';
      case 'HIGH': return 'badge badge-warning';
      case 'MEDIUM': return 'badge badge-primary';
      default: return 'badge badge-success';
    }
  };

  return (
    <div className="container" style={{ padding: '2.5rem 1rem' }}>
      {/* Header Banner */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <span className="badge badge-primary" style={{ marginBottom: '0.5rem' }}>Skill Intelligence</span>
          <h1 style={{ fontSize: '2rem', fontWeight: 800 }}>Skill Gap Analysis</h1>
          <p style={{ color: 'var(--text-subtle)' }}>
            Target Position: <strong style={{ color: '#fff' }}>{gapData.job_title}</strong> at {gapData.company}
          </p>
        </div>
        <Link to={`/dashboard/roadmap/${jobId}`} className="btn btn-primary" style={{ padding: '0.75rem 1.5rem', fontSize: '0.95rem' }}>
          🚀 Generate Personalized Roadmap
        </Link>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '1.5rem' }}>
        {/* Required Skill Coverage Card */}
        <div className="glass-card" style={{ gridColumn: 'span 6', padding: '1.75rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Required Skill Coverage</h3>
            <span className="badge badge-success">Target Match</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem', marginBottom: '0.75rem' }}>
            <span style={{ fontSize: '3rem', fontWeight: 800, color: 'var(--accent-green)' }}>
              {gapData.required_coverage_percent}%
            </span>
          </div>
          <div style={{ width: '100%', height: '8px', background: 'var(--bg-input)', borderRadius: '4px', overflow: 'hidden' }}>
            <div style={{ width: `${gapData.required_coverage_percent}%`, height: '100%', background: 'var(--accent-green)', transition: 'width 0.8s ease' }}></div>
          </div>
        </div>

        {/* Skill Gap Percentage Card */}
        <div className="glass-card" style={{ gridColumn: 'span 6', padding: '1.75rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Skill Gap Percentage</h3>
            <span className="badge badge-pink">Action Required</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem', marginBottom: '0.75rem' }}>
            <span style={{ fontSize: '3rem', fontWeight: 800, color: 'var(--accent-pink)' }}>
              {gapData.skill_gap_percent}%
            </span>
          </div>
          <div style={{ width: '100%', height: '8px', background: 'var(--bg-input)', borderRadius: '4px', overflow: 'hidden' }}>
            <div style={{ width: `${gapData.skill_gap_percent}%`, height: '100%', background: 'var(--accent-pink)', transition: 'width 0.8s ease' }}></div>
          </div>
        </div>

        {/* Matched Skills List */}
        <div className="glass-card" style={{ gridColumn: 'span 6', padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem', color: 'var(--accent-green)' }}>
            ✅ Matched Skills ({gapData.matched_required_skills.length})
          </h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {gapData.matched_required_skills.map((sk, idx) => (
              <span key={idx} className="badge badge-success" style={{ fontSize: '0.85rem', padding: '0.4rem 0.75rem' }}>
                ✓ {sk}
              </span>
            ))}
          </div>
        </div>

        {/* Missing Required Skills List */}
        <div className="glass-card" style={{ gridColumn: 'span 6', padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem', color: 'var(--accent-pink)' }}>
            ⚠️ Missing Required Skills ({gapData.missing_required_skills.length})
          </h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {gapData.missing_required_skills.length > 0 ? (
              gapData.missing_required_skills.map((sk, idx) => (
                <span key={idx} className="badge badge-pink" style={{ fontSize: '0.85rem', padding: '0.4rem 0.75rem' }}>
                  ✗ {sk}
                </span>
              ))
            ) : (
              <span style={{ color: 'var(--text-muted)' }}>None! You meet all required skills for this job.</span>
            )}
          </div>
        </div>

        {/* Prioritized Skill Gaps Table */}
        <div className="glass-card" style={{ gridColumn: 'span 12', padding: '1.75rem' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1.25rem' }}>
            🎯 Prioritized Skill Development List
          </h3>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-subtle)', fontSize: '0.85rem', textTransform: 'uppercase' }}>
                  <th style={{ padding: '0.75rem 1rem' }}>Missing Skill</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Category</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Priority</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Rationale</th>
                </tr>
              </thead>
              <tbody>
                {gapData.prioritized_gaps.map((item, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid var(--border-color)', fontSize: '0.95rem' }}>
                    <td style={{ padding: '1rem', fontWeight: 700, color: '#fff' }}>{item.skill}</td>
                    <td style={{ padding: '1rem', color: 'var(--text-muted)' }}>{item.category}</td>
                    <td style={{ padding: '1rem' }}>
                      <span className={getPriorityBadgeClass(item.priority)}>
                        {item.priority}
                      </span>
                    </td>
                    <td style={{ padding: '1rem', color: 'var(--text-muted)' }}>{item.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SkillGapPage;
