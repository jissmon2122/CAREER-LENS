import React from 'react';

const LiveJobCard = ({ job, onViewMatch, onSaveJob, isSaved, onOpenRoadmap }) => {
  if (!job) return null;

  const getScoreBadgeClass = (score) => {
    if (!score) return 'badge-secondary';
    if (score >= 75) return 'badge-success';
    if (score >= 60) return 'badge-primary';
    if (score >= 45) return 'badge-warning';
    return 'badge-pink';
  };

  const formatSalary = () => {
    if (job.salary_min || job.salary_max) {
      const minL = job.salary_min ? (job.salary_min / 100000).toFixed(1) : null;
      const maxL = job.salary_max ? (job.salary_max / 100000).toFixed(1) : null;
      if (minL && maxL) return `₹${minL}L - ₹${maxL}L PA`;
      if (minL) return `From ₹${minL}L PA`;
      if (maxL) return `Up to ₹${maxL}L PA`;
    }
    return 'Salary Not Disclosed';
  };

  return (
    <div style={{
      background: 'var(--bg-input)',
      borderRadius: 'var(--radius-md)',
      padding: '1.25rem',
      border: '1px solid var(--border-color)',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
      position: 'relative'
    }}>
      <div>
        {/* Card Top Meta: Source & Verified Freshness */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.6rem', fontSize: '0.75rem' }}>
          <span style={{ color: 'var(--accent-cyan)', fontWeight: 700 }}>
            Source: {job.source_name || job.provider || 'Live Feed Provider'}
          </span>
          <span className="badge badge-success" style={{ fontSize: '0.7rem', padding: '0.2rem 0.5rem' }}>
            ✓ Verified Live
          </span>
        </div>

        {/* Title & Company */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.5rem', marginBottom: '0.5rem' }}>
          <div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#fff', margin: 0 }}>
              {job.title}
            </h3>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.2rem', fontWeight: 600 }}>
              {job.company} • {job.display_location || job.location}
            </div>
          </div>
          
          {/* Match Score Badge */}
          {job.match_score !== undefined && job.match_score !== null ? (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.25rem' }}>
              <span className={`badge ${getScoreBadgeClass(job.match_score)}`} style={{ fontSize: '0.85rem', padding: '0.3rem 0.65rem', fontWeight: 800 }}>
                {job.match_score}% Match
              </span>
              {job.ai_semantic_score !== undefined && job.ai_semantic_score !== null && (
                <span style={{
                  background: 'linear-gradient(135deg, #6366f1, #a855f7)',
                  color: '#fff',
                  fontSize: '0.7rem',
                  padding: '0.15rem 0.45rem',
                  borderRadius: '10px',
                  fontWeight: 700
                }}>
                  ✨ AI: {job.ai_semantic_score}%
                </span>
              )}
            </div>
          ) : (
            <span className="badge badge-primary" style={{ fontSize: '0.75rem' }}>
              {job.experience_level || 'Open'}
            </span>
          )}
        </div>

        {/* Meta Pills: Remote/Onsite, Experience, Salary */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', margin: '0.6rem 0 0.85rem' }}>
          {(job.workplace_type || job.remote_type) && (
            <span style={{
              background: (job.workplace_type === 'REMOTE' || job.remote_type === 'REMOTE')
                ? 'rgba(99,102,241,0.15)'
                : (job.workplace_type === 'HYBRID' || job.remote_type === 'HYBRID')
                ? 'rgba(168,85,247,0.15)'
                : 'rgba(255,255,255,0.08)',
              color: (job.workplace_type === 'REMOTE' || job.remote_type === 'REMOTE')
                ? '#a5b4fc'
                : (job.workplace_type === 'HYBRID' || job.remote_type === 'HYBRID')
                ? '#c084fc'
                : 'var(--text-muted)',
              padding: '0.2rem 0.5rem',
              borderRadius: '4px',
              fontSize: '0.75rem',
              fontWeight: 600
            }}>
              {(job.workplace_type === 'REMOTE' || job.remote_type === 'REMOTE')
                ? '🌐 Remote'
                : (job.workplace_type === 'HYBRID' || job.remote_type === 'HYBRID')
                ? '🏢 Hybrid'
                : '📍 On-Site'}
            </span>
          )}
          <span style={{ background: 'var(--bg-card)', color: 'var(--text-muted)', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem' }}>
            Exp: {job.experience_level || 'Fresher'}
          </span>
          <span style={{ background: 'rgba(16, 185, 129, 0.1)', color: 'var(--accent-green)', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600 }}>
            {formatSalary()}
          </span>
        </div>

        {/* Matched Skills */}
        {job.matched_skills && job.matched_skills.length > 0 && (
          <div style={{ marginBottom: '0.65rem' }}>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-subtle)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '0.25rem' }}>
              MATCHED SKILLS ({job.matched_skills.length})
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.3rem' }}>
              {job.matched_skills.slice(0, 4).map(sk => (
                <span key={sk} className="badge badge-success" style={{ fontSize: '0.72rem', padding: '0.15rem 0.45rem' }}>
                  ✓ {sk}
                </span>
              ))}
              {job.matched_skills.length > 4 && (
                <span className="badge badge-primary" style={{ fontSize: '0.72rem', padding: '0.15rem 0.45rem' }}>
                  +{job.matched_skills.length - 4} more
                </span>
              )}
            </div>
          </div>
        )}

        {/* Missing Required Skills with Roadmap Integration */}
        {job.missing_required_skills && job.missing_required_skills.length > 0 && (
          <div style={{ marginBottom: '0.85rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--accent-warning)', fontWeight: 700, textTransform: 'uppercase' }}>
                MISSING ({job.missing_required_skills.length})
              </div>
              {onOpenRoadmap && (
                <button
                  onClick={() => onOpenRoadmap(job)}
                  style={{ background: 'none', border: 'none', color: 'var(--accent-cyan)', fontSize: '0.72rem', fontWeight: 700, cursor: 'pointer', padding: 0 }}
                >
                  Learn on Roadmap 📚
                </button>
              )}
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.3rem' }}>
              {job.missing_required_skills.slice(0, 3).map(sk => (
                <span key={sk} className="badge badge-warning" style={{ fontSize: '0.72rem', padding: '0.15rem 0.45rem' }}>
                  ✗ {sk}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Why This Job Matches Your Resume */}
        {job.why_recommended && job.why_recommended.length > 0 && (
          <div style={{ background: 'rgba(99,102,241,0.06)', borderRadius: '6px', padding: '0.5rem 0.65rem', marginBottom: '0.85rem', border: '1px solid rgba(99,102,241,0.12)' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--accent-cyan)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '0.25rem' }}>
              WHY THIS JOB MATCHES YOUR RESUME
            </div>
            {job.why_recommended.map((reason, idx) => (
              <div key={idx} style={{ fontSize: '0.73rem', color: reason.startsWith('✓') ? '#a7f3d0' : '#fde047', lineHeight: '1.4' }}>
                {reason}
              </div>
            ))}
          </div>
        )}

      </div>

      {/* Action Footer */}
      <div style={{ marginTop: '0.5rem', paddingTop: '0.75rem', borderTop: '1px solid var(--border-color)', display: 'flex', gap: '0.5rem', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap' }}>
        <button
          onClick={() => onSaveJob(job.job_id || job._id, isSaved ? 'UNSAVE' : 'SAVED')}
          className="btn btn-secondary"
          style={{ padding: '0.35rem 0.65rem', fontSize: '0.78rem' }}
        >
          {isSaved ? '★ Saved' : '☆ Save Job'}
        </button>

        <div style={{ display: 'flex', gap: '0.4rem' }}>
          {onViewMatch && (
            <button
              onClick={() => onViewMatch(job.job_id || job._id)}
              className="btn btn-secondary"
              style={{ padding: '0.35rem 0.65rem', fontSize: '0.78rem' }}
            >
              Match Analysis
            </button>
          )}

          {job.application_url ? (
            <a
              href={job.application_url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-primary"
              style={{ padding: '0.35rem 0.75rem', fontSize: '0.78rem', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '0.25rem', fontWeight: 700 }}
            >
              Apply Now 🔗
            </a>
          ) : (
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Application URL Not Provided</span>
          )}
        </div>
      </div>
    </div>
  );
};

export default LiveJobCard;
