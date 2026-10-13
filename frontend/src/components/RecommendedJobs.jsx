import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { jobAPI } from '../services/api';
import { useJobContext } from '../context/JobContext';
import JobMatchModal from './JobMatchModal';
import LoadingSpinner from './LoadingSpinner';

const RecommendedJobs = ({ resumeAnalyzed }) => {
  const {
    buckets,
    liveJobsData,
    loading: contextLoading,
    refreshing,
    error: contextError,
    fetchLiveJobs,
    refreshLiveJobs
  } = useJobContext();

  const [selectedMatch, setSelectedMatch] = useState(null);
  const [loadingMatchId, setLoadingMatchId] = useState(null);

  // Recommendations from shared context
  const recommendations = buckets?.all_recommendations?.length
    ? buckets.all_recommendations
    : (liveJobsData?.data?.recommendations || []);

  useEffect(() => {
    if (!resumeAnalyzed) return;

    // If already loaded in context, don't refetch
    if (recommendations.length > 0) return;

    fetchLiveJobs();
  }, [resumeAnalyzed, recommendations.length, fetchLiveJobs]);

  const handleViewMatch = async (jobId) => {
    setLoadingMatchId(jobId);
    try {
      const response = await jobAPI.getJobMatch(jobId);
      if (response.success && response.data) {
        setSelectedMatch(response.data);
      }
    } catch (err) {
      console.error("Failed to fetch match analysis:", err);
      alert("Unable to fetch job match details.");
    } finally {
      setLoadingMatchId(null);
    }
  };

  const getScoreBadgeClass = (score) => {
    if (score >= 80) return 'badge-success';
    if (score >= 65) return 'badge-primary';
    if (score >= 50) return 'badge-warning';
    return 'badge-pink';
  };

  if (!resumeAnalyzed) return null;

  if (recommendations.length === 0 && contextLoading) {
    return (
      <div className="glass-card" style={{ gridColumn: 'span 12', padding: '2rem', textAlign: 'center' }}>
        <LoadingSpinner text="Computing 6-component weighted job match scores across live dataset..." />
      </div>
    );
  }

  if (recommendations.length === 0 && contextError) {
    return (
      <div className="glass-card" style={{ gridColumn: 'span 12', padding: '2rem', textAlign: 'center' }}>
        <p style={{ color: 'var(--accent-pink)' }}>{contextError}</p>
        <button
          onClick={() => refreshLiveJobs(true)}
          className="btn btn-secondary"
          style={{ marginTop: '0.75rem', fontSize: '0.85rem' }}
        >
          Retry
        </button>
      </div>
    );
  }

  if (recommendations.length === 0) {
    return null;
  }

  return (
    <div style={{ gridColumn: 'span 12', marginTop: '1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 800 }}>Recommended Jobs For You</h2>
            {refreshing && (
              <span className="badge badge-purple" style={{ fontSize: '0.72rem', animation: 'pulse 1.5s infinite' }}>
                Updating in background...
              </span>
            )}
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.2rem' }}>
            Calculated dynamically from your extracted resume profile and target dataset jobs.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <span className="badge badge-primary" style={{ fontSize: '0.85rem' }}>
            Top {recommendations.length} Matches
          </span>

          <button
            onClick={() => refreshLiveJobs(true)}
            disabled={contextLoading || refreshing}
            className="btn btn-secondary"
            title="Refresh Recommendations"
            style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}
          >
            <span style={{ display: 'inline-block', transform: refreshing ? 'rotate(360deg)' : 'none', transition: 'transform 0.8s ease' }}>
              🔄
            </span>
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </button>

          <Link
            to="/dashboard/jobs"
            className="btn btn-outline"
            style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}
          >
            View Live Search →
          </Link>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
        {recommendations.map(job => (
          <div key={job.job_id} style={{
            background: 'var(--bg-input)',
            borderRadius: 'var(--radius-md)',
            padding: '1.25rem',
            border: '1px solid var(--border-color)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between'
          }}>
            <div>
              {/* Header */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.5rem', marginBottom: '0.75rem' }}>
                <div>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#fff' }}>
                    {job.job_title}
                  </h3>
                  <div style={{ color: 'var(--accent-cyan)', fontSize: '0.9rem', fontWeight: 600 }}>
                    {job.company} • {job.location}
                  </div>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.35rem' }}>
                  <span className={`badge ${getScoreBadgeClass(job.match_score)}`} style={{ fontSize: '0.9rem', padding: '0.35rem 0.75rem', fontWeight: 800 }}>
                    {job.match_score}% Match
                  </span>
                  {job.ai_semantic_score !== undefined && job.ai_semantic_score !== null && (
                    <span style={{
                      background: 'linear-gradient(135deg, #6366f1, #a855f7)',
                      color: '#fff',
                      fontSize: '0.72rem',
                      padding: '0.15rem 0.5rem',
                      borderRadius: '10px',
                      fontWeight: 700
                    }}>
                      ✨ AI: {job.ai_semantic_score}%
                    </span>
                  )}
                </div>
              </div>

              {/* Matched Skills */}
              <div style={{ marginBottom: '0.85rem' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '0.35rem' }}>
                  MATCHED SKILLS ({job.matched_skills.length})
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                  {job.matched_skills.slice(0, 4).map(sk => (
                    <span key={sk} className="badge badge-success" style={{ fontSize: '0.75rem', padding: '0.2rem 0.5rem' }}>
                      ✓ {sk}
                    </span>
                  ))}
                  {job.matched_skills.length > 4 && (
                    <span className="badge badge-primary" style={{ fontSize: '0.75rem', padding: '0.2rem 0.5rem' }}>
                      +{job.matched_skills.length - 4} more
                    </span>
                  )}
                </div>
              </div>

              {/* Missing Skills */}
              {job.missing_required_skills && job.missing_required_skills.length > 0 && (
                <div style={{ marginBottom: '1rem' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--accent-warning)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '0.35rem' }}>
                    MISSING ({job.missing_required_skills.length})
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                    {job.missing_required_skills.slice(0, 3).map(sk => (
                      <span key={sk} className="badge badge-warning" style={{ fontSize: '0.75rem', padding: '0.2rem 0.5rem' }}>
                        ✗ {sk}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div style={{ marginTop: '0.5rem', paddingTop: '0.75rem', borderTop: '1px solid var(--border-color)', display: 'flex', gap: '0.5rem', justifyContent: 'space-between', alignItems: 'center' }}>
              <Link to={`/dashboard/skill-gap/${job.job_id}`} className="btn btn-secondary" style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}>
                🎯 Skill Gap
              </Link>

              <button
                onClick={() => handleViewMatch(job.job_id)}
                className="btn btn-primary"
                disabled={loadingMatchId === job.job_id}
                style={{ padding: '0.35rem 0.85rem', fontSize: '0.8rem' }}
              >
                {loadingMatchId === job.job_id ? 'Loading...' : 'Match Reasons'}
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Modal Popup */}
      {selectedMatch && (
        <JobMatchModal
          matchData={selectedMatch}
          onClose={() => setSelectedMatch(null)}
        />
      )}
    </div>
  );
};

export default RecommendedJobs;
