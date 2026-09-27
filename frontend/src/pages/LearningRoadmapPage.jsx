import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { skillGapAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';

const LearningRoadmapPage = () => {
  const { jobId } = useParams();
  const [roadmap, setRoadmap] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [acquiringSkill, setAcquiringSkill] = useState('');
  const [acquiredSet, setAcquiredSet] = useState(new Set());

  useEffect(() => {
    const fetchRoadmap = async () => {
      setLoading(true);
      setError('');
      try {
        const response = await skillGapAPI.getRoadmap(jobId);
        if (response.success && response.data.roadmap) {
          setRoadmap(response.data.roadmap);
        } else {
          setError(response.message || "Failed to generate learning roadmap.");
        }
      } catch (err) {
        console.error("Roadmap Error:", err);
        const msg = err.response?.data?.message || err.message || "Failed to load learning roadmap.";
        setError(msg);
      } finally {
        setLoading(false);
      }
    };

    if (jobId) {
      fetchRoadmap();
    }
  }, [jobId]);

  const handleAcquireSkill = async (skillName) => {
    setAcquiringSkill(skillName);
    try {
      const response = await skillGapAPI.acquireSkill(skillName);
      if (response.success) {
        setAcquiredSet(prev => new Set(prev).add(skillName));
        alert(`🎉 Great job! Skill '${skillName}' has been added to your profile. Your candidate profile and match score have been updated!`);
      }
    } catch (err) {
      console.error("Skill acquisition error:", err);
      alert("Failed to mark skill as acquired.");
    } finally {
      setAcquiringSkill('');
    }
  };

  if (loading) {
    return (
      <div className="container" style={{ padding: '4rem 1rem', textAlign: 'center' }}>
        <LoadingSpinner text="Building your personalized learning roadmap & certification recommendations..." />
      </div>
    );
  }

  if (error || !roadmap) {
    return (
      <div className="container" style={{ padding: '3rem 1rem' }}>
        <div className="glass-card" style={{ textAlign: 'center', padding: '2.5rem', border: '1px solid var(--accent-pink)' }}>
          <h3 style={{ color: 'var(--accent-pink)', marginBottom: '1rem' }}>⚠️ Learning Roadmap Notice</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>{error}</p>
          <Link to="/dashboard" className="btn btn-primary">Back to Dashboard</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container" style={{ padding: '2.5rem 1rem' }}>
      {/* Page Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <span className="badge badge-success" style={{ marginBottom: '0.5rem' }}>Personalized Career Growth</span>
          <h1 style={{ fontSize: '2rem', fontWeight: 800 }}>Learning Roadmap & Certifications</h1>
          <p style={{ color: 'var(--text-subtle)' }}>
            Target Role: <strong style={{ color: '#fff' }}>{roadmap.job_title}</strong> | Current Match: <strong style={{ color: 'var(--accent-purple)' }}>{roadmap.current_match_score}%</strong> ➔ Projected Max: <strong style={{ color: 'var(--accent-green)' }}>{roadmap.projected_max_match_score}%</strong>
          </p>
        </div>
        <Link to={`/dashboard/skill-gap/${jobId}`} className="btn btn-secondary">
          ⬅️ View Skill Gap
        </Link>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '1.5rem' }}>
        {/* Match Score Improvement Simulation Widget */}
        <div className="glass-card" style={{ gridColumn: 'span 12', padding: '1.75rem', background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.9))' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1rem', color: 'var(--accent-green)' }}>
            🚀 Match Improvement Simulation
          </h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: '1.25rem', fontSize: '0.95rem' }}>
            See how acquiring each missing skill boosts your job match score step-by-step:
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            {roadmap.match_improvement_simulation.map((step, idx) => (
              <div key={idx} style={{ background: 'var(--bg-input)', padding: '1rem', borderRadius: 'var(--radius-md)', border: acquiredSet.has(step.skill_acquired) ? '1px solid var(--accent-green)' : '1px solid var(--border-color)' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-subtle)', fontWeight: 700, textTransform: 'uppercase' }}>
                  {step.skill_type} Skill
                </div>
                <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#fff', margin: '0.25rem 0' }}>
                  {step.skill_acquired}
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.5rem' }}>
                  <span style={{ fontSize: '0.9rem', fontWeight: 800, color: 'var(--accent-green)' }}>
                    {step.score_gain} ➔ {step.projected_match_score}%
                  </span>
                  <button
                    onClick={() => handleAcquireSkill(step.skill_acquired)}
                    disabled={acquiredSet.has(step.skill_acquired) || acquiringSkill === step.skill_acquired}
                    className="btn btn-secondary"
                    style={{ fontSize: '0.75rem', padding: '0.25rem 0.6rem' }}
                  >
                    {acquiredSet.has(step.skill_acquired) ? '✓ Acquired' : acquiringSkill === step.skill_acquired ? 'Saving...' : '+ Mark Complete'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Step-by-Step Learning Roadmap Timeline */}
        <div className="glass-card" style={{ gridColumn: 'span 8', padding: '1.75rem' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1.5rem' }}>
            📅 Step-by-Step Learning Timeline
          </h3>

          {roadmap.roadmap_phases.map((phase) => (
            <div key={phase.phase} style={{ marginBottom: '2rem', paddingLeft: '1rem', borderLeft: '3px solid var(--accent-purple)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <h4 style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--accent-purple)' }}>{phase.title}</h4>
                <span className="badge badge-primary">{phase.estimated_duration}</span>
              </div>
              <p style={{ color: 'var(--text-subtle)', fontSize: '0.9rem', marginBottom: '1rem' }}>{phase.focus}</p>

              {phase.skills.map((skItem, idx) => (
                <div key={idx} style={{ background: 'var(--bg-input)', padding: '1.25rem', borderRadius: 'var(--radius-md)', marginBottom: '1rem', border: '1px solid var(--border-color)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                    <h5 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#fff' }}>{skItem.skill}</h5>
                    <span className="badge badge-warning" style={{ fontSize: '0.75rem' }}>{skItem.estimated_hours}</span>
                  </div>

                  <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
                    💡 <strong>Hands-on Project Idea:</strong> {skItem.project_idea}
                  </div>

                  <div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '0.35rem' }}>
                      RECOMMENDED COURSES & TUTORIALS
                    </div>
                    {skItem.courses.map((c, cIdx) => (
                      <a
                        key={cIdx}
                        href={c.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{ display: 'inline-block', marginRight: '0.75rem', marginBottom: '0.35rem', color: 'var(--accent-purple)', fontSize: '0.85rem', textDecoration: 'underline' }}
                      >
                        🔗 {c.title} ({c.type})
                      </a>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ))}
        </div>

        {/* Recommended Industry Certifications Sidebar */}
        <div className="glass-card" style={{ gridColumn: 'span 4', padding: '1.75rem' }}>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '1.25rem', color: 'var(--accent-purple)' }}>
            🏆 Recommended Certifications
          </h3>
          <p style={{ color: 'var(--text-subtle)', fontSize: '0.85rem', marginBottom: '1.25rem' }}>
            Enhance your resume credibility with top recognized industry certifications:
          </p>

          {roadmap.recommended_certifications.map((cert, idx) => (
            <div key={idx} style={{ background: 'var(--bg-input)', padding: '1rem', borderRadius: 'var(--radius-md)', marginBottom: '1rem', border: '1px solid var(--border-color)' }}>
              <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#fff', marginBottom: '0.25rem' }}>
                {cert.title}
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                Issuer: {cert.issuer}
              </div>
              <a
                href={cert.url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-secondary"
                style={{ fontSize: '0.75rem', padding: '0.3rem 0.65rem' }}
              >
                Learn More 🔗
              </a>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default LearningRoadmapPage;
