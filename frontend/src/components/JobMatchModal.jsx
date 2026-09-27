import React from 'react';

const JobMatchModal = ({ matchData, onClose }) => {
  if (!matchData) return null;

  const { match, job } = matchData;
  const breakdown = match.breakdown || {};

  const getScoreColor = (score) => {
    if (score >= 85) return 'var(--accent-green)';
    if (score >= 70) return 'var(--primary)';
    if (score >= 60) return 'var(--accent-warning)';
    return 'var(--accent-pink)';
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(10, 15, 30, 0.85)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999,
      padding: '1.5rem'
    }}>
      <div className="glass-card" style={{
        maxWidth: '750px',
        width: '100%',
        maxHeight: '90vh',
        overflowY: 'auto',
        position: 'relative',
        border: '1px solid var(--border-color)',
        padding: '2rem'
      }}>
        {/* Close Button */}
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '1.25rem',
            right: '1.25rem',
            background: 'var(--bg-input)',
            border: '1px solid var(--border-color)',
            color: 'var(--text-subtle)',
            width: '36px',
            height: '36px',
            borderRadius: '50%',
            cursor: 'pointer',
            fontSize: '1.2rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >
          ✕
        </button>

        {/* Modal Header */}
        <div style={{ marginBottom: '1.5rem', paddingRight: '2rem' }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--accent-cyan)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            EXPLAINABLE MATCH ANALYSIS
          </div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800, marginTop: '0.2rem', marginBottom: '0.25rem' }}>
            {job.job_title}
          </h2>
          <div style={{ color: 'var(--text-muted)', fontSize: '1rem' }}>
            {job.company} • {job.location} • <span style={{ color: 'var(--accent-green)' }}>₹{(job.salary_min / 100000).toFixed(1)}L - {(job.salary_max / 100000).toFixed(1)}L PA</span>
          </div>
        </div>

        {/* Main Match Gauge Card */}
        <div style={{
          background: 'var(--bg-input)',
          padding: '1.5rem',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-color)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1.5rem',
          flexWrap: 'wrap',
          gap: '1rem'
        }}>
          <div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-subtle)', fontWeight: 600 }}>FINAL COMBINED MATCH SCORE</div>
            <div style={{ fontSize: '3rem', fontWeight: 800, color: getScoreColor(match.match_score), lineHeight: 1, marginTop: '0.4rem' }}>
              {match.match_score}%
            </div>
            {match.ai_enabled && match.ai_semantic_score !== undefined && (
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
                Formula: 0.60 × Deterministic ({match.deterministic_match_score || match.match_score}%) + 0.40 × AI Semantic ({match.ai_semantic_score}%)
              </div>
            )}
          </div>
          <div style={{ textAlign: 'right' }}>
            <span className="badge badge-primary" style={{ fontSize: '0.95rem', padding: '0.4rem 1rem', background: getScoreColor(match.match_score), color: '#000', fontWeight: 700 }}>
              {match.match_category}
            </span>
            {match.ai_enabled && (
              <div style={{ marginTop: '0.5rem' }}>
                <span style={{
                  background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
                  color: '#fff',
                  padding: '0.25rem 0.65rem',
                  borderRadius: '12px',
                  fontSize: '0.78rem',
                  fontWeight: 700,
                  display: 'inline-block'
                }}>
                  ✨ AI Semantic Match: {match.ai_semantic_score}%
                </span>
              </div>
            )}
            <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', marginTop: '0.4rem' }}>
              Model: sentence-transformers/all-MiniLM-L6-v2
            </div>
          </div>
        </div>

        {/* Semantic Skill Match Categorization (AI Powered) */}
        {match.semantic_skill_categorization && match.semantic_skill_categorization.length > 0 && (
          <div style={{ marginBottom: '1.75rem', background: 'rgba(99, 102, 241, 0.05)', padding: '1.25rem', borderRadius: 'var(--radius-md)', border: '1px solid rgba(99, 102, 241, 0.2)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, margin: 0, color: '#a855f7' }}>
                ✨ AI Skill Relationship Analysis
              </h3>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Cosine Similarity Threshold &ge; 70%</span>
            </div>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {match.semantic_skill_categorization.map((item, idx) => {
                if (item.match_type === 'EXACT_MATCH') {
                  return (
                    <span key={idx} style={{ background: 'rgba(16, 185, 129, 0.15)', color: 'var(--accent-green)', padding: '0.35rem 0.65rem', borderRadius: '6px', fontSize: '0.8rem', border: '1px solid var(--accent-green)', fontWeight: 600 }}>
                      ✓ {item.skill} (Exact)
                    </span>
                  );
                } else if (item.match_type === 'NORMALIZED_MATCH') {
                  return (
                    <span key={idx} style={{ background: 'rgba(6, 182, 212, 0.15)', color: 'var(--accent-cyan)', padding: '0.35rem 0.65rem', borderRadius: '6px', fontSize: '0.8rem', border: '1px solid var(--accent-cyan)', fontWeight: 600 }}>
                      ✓ {item.skill} ↔ {item.matched_with} (Normalized)
                    </span>
                  );
                } else if (item.match_type === 'SEMANTIC_MATCH') {
                  return (
                    <span key={idx} style={{ background: 'linear-gradient(135deg, rgba(99,102,241,0.2), rgba(168,85,247,0.2))', color: '#c084fc', padding: '0.35rem 0.65rem', borderRadius: '6px', fontSize: '0.8rem', border: '1px solid #a855f7', fontWeight: 700 }}>
                      ✨ {item.skill} ↔ {item.matched_with} ({Math.round(item.similarity * 100)}% Sim)
                    </span>
                  );
                } else {
                  return (
                    <span key={idx} style={{ background: 'rgba(239, 68, 68, 0.1)', color: '#f87171', padding: '0.35rem 0.65rem', borderRadius: '6px', fontSize: '0.8rem', border: '1px solid rgba(239,68,68,0.3)' }}>
                      ✗ {item.skill} (Missing)
                    </span>
                  );
                }
              })}
            </div>
          </div>
        )}

        {/* Weighted Component Match Breakdown */}
        <div style={{ marginBottom: '1.75rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem' }}>Deterministic Match Components (60% Weight)</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.85rem' }}>
            {[
              { label: 'Required Skills', pts: breakdown.required_skills, max: 40 },
              { label: 'Preferred Skills', pts: breakdown.preferred_skills, max: 10 },
              { label: 'Experience', pts: breakdown.experience, max: 15 },
              { label: 'Education', pts: breakdown.education, max: 10 },
              { label: 'Role Match', pts: breakdown.role, max: 15 },
              { label: 'Location', pts: breakdown.location, max: 10 }
            ].map(item => (
              <div key={item.label} style={{ background: 'var(--bg-input)', padding: '0.85rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.825rem', marginBottom: '0.35rem' }}>
                  <span style={{ color: 'var(--text-muted)', fontWeight: 600 }}>{item.label}</span>
                  <span style={{ fontWeight: 700, color: '#fff' }}>{item.pts} / {item.max} pts</span>
                </div>
                <div style={{ width: '100%', height: '6px', background: 'var(--bg-card)', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{ width: `${((item.pts || 0) / item.max) * 100}%`, height: '100%', background: 'var(--primary)' }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Explainable Match Reasons */}
        {match.explainable_reasons && match.explainable_reasons.length > 0 && (
          <div style={{ marginBottom: '1.75rem' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.75rem', color: 'var(--accent-green)' }}>
              ✓ Why This Job Matches You
            </h3>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {match.explainable_reasons.map((reason, idx) => (
                <li key={idx} style={{ background: 'rgba(16, 185, 129, 0.1)', padding: '0.65rem 1rem', borderRadius: 'var(--radius-md)', borderLeft: '3px solid var(--accent-green)', fontSize: '0.9rem' }}>
                  ✓ {reason}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Matched Skills */}
        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.6rem' }}>Matched Skills</h3>
          {match.matched_skills && match.matched_skills.length > 0 ? (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {match.matched_skills.map(sk => (
                <span key={sk} className="badge badge-success" style={{ fontSize: '0.85rem', padding: '0.35rem 0.75rem' }}>
                  ✓ {sk}
                </span>
              ))}
            </div>
          ) : (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No direct skill overlap detected.</p>
          )}
        </div>

        {/* Missing Required Skills */}
        {match.missing_required_skills && match.missing_required_skills.length > 0 && (
          <div style={{ marginBottom: '1.5rem' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.6rem', color: 'var(--accent-warning)' }}>
              Missing Required Skills
            </h3>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {match.missing_required_skills.map(sk => (
                <span key={sk} className="badge badge-warning" style={{ fontSize: '0.85rem', padding: '0.35rem 0.75rem' }}>
                  ✗ {sk}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Action Button */}
        <div style={{ textAlign: 'right', marginTop: '2rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
          <button onClick={onClose} className="btn btn-primary" style={{ padding: '0.5rem 1.5rem' }}>
            Close Match Analysis
          </button>
        </div>
      </div>
    </div>
  );
};

export default JobMatchModal;
