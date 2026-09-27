import React, { useState, useEffect } from 'react';
import { forecastingAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';

const SkillDemandPage = () => {
  const [horizon, setHorizon] = useState('6M');
  const [topSkills, setTopSkills] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [searchSkill, setSearchSkill] = useState('Python');
  const [skillForecast, setSkillForecast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchTopData = async () => {
      setLoading(true);
      setError('');
      try {
        const [topRes, recRes] = await Promise.all([
          forecastingAPI.getTopSkills(),
          forecastingAPI.getRecommendations().catch(() => null)
        ]);

        if (topRes.success) {
          setTopSkills(topRes.data);
        }
        if (recRes && recRes.success) {
          setRecommendations(recRes.data.recommendations || []);
        }

        // Fetch initial skill forecast for Python
        const pyRes = await forecastingAPI.getSkillForecast('Python');
        if (pyRes.success && pyRes.data.forecast) {
          setSkillForecast(pyRes.data.forecast);
        }
      } catch (err) {
        console.error("Forecasting Error:", err);
        setError("Failed to load skill demand forecasts.");
      } finally {
        setLoading(false);
      }
    };

    fetchTopData();
  }, []);

  const handleSearchSkill = async (e) => {
    e.preventDefault();
    if (!searchSkill.trim()) return;
    setSearching(true);
    try {
      const res = await forecastingAPI.getSkillForecast(searchSkill.trim());
      if (res.success && res.data.forecast) {
        setSkillForecast(res.data.forecast);
      }
    } catch (err) {
      console.error("Skill Search Error:", err);
      alert("Unable to fetch forecast for the requested skill.");
    } finally {
      setSearching(false);
    }
  };

  if (loading) {
    return (
      <div className="container" style={{ padding: '4rem 1rem', textAlign: 'center' }}>
        <LoadingSpinner text="Computing time-series forecasting models, evaluating MAE/RMSE metrics, and classifying skill trends..." />
      </div>
    );
  }

  return (
    <div className="container" style={{ padding: '2.5rem 1rem' }}>
      {/* Page Header & Horizon Selector */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <span className="badge badge-purple" style={{ marginBottom: '0.5rem' }}>AI Research Module</span>
          <h1 style={{ fontSize: '2rem', fontWeight: 800 }}>Future Skill Demand Forecasting</h1>
          <p style={{ color: 'var(--text-subtle)' }}>
            Data-driven time-series trends and statistical demand forecasting (2024 – 2026)
          </p>
        </div>

        {/* Horizon Buttons */}
        <div style={{ background: 'var(--bg-input)', padding: '0.35rem', borderRadius: 'var(--radius-md)', display: 'flex', gap: '0.35rem' }}>
          {['3M', '6M', '12M'].map((h) => (
            <button
              key={h}
              onClick={() => setHorizon(h)}
              className={horizon === h ? 'btn btn-primary' : 'btn btn-secondary'}
              style={{ fontSize: '0.85rem', padding: '0.4rem 0.85rem' }}
            >
              {h} Forecast
            </button>
          ))}
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '1.5rem' }}>
        {/* Trend Overview Cards */}
        <div className="glass-card" style={{ gridColumn: 'span 3', padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--accent-pink)', marginBottom: '0.75rem' }}>
            🔥 Top Rising Skills
          </h3>
          {topSkills?.rising_skills?.map((item, idx) => (
            <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0', borderBottom: '1px solid var(--border-color)', fontSize: '0.9rem' }}>
              <span style={{ fontWeight: 700, color: '#fff' }}>{item.skill}</span>
              <span style={{ color: 'var(--accent-pink)', fontWeight: 800 }}>{item.growth_rate}</span>
            </div>
          ))}
        </div>

        <div className="glass-card" style={{ gridColumn: 'span 3', padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--accent-green)', marginBottom: '0.75rem' }}>
            🟢 Stable Core Skills
          </h3>
          {topSkills?.stable_skills?.map((item, idx) => (
            <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0', borderBottom: '1px solid var(--border-color)', fontSize: '0.9rem' }}>
              <span style={{ fontWeight: 700, color: '#fff' }}>{item.skill}</span>
              <span style={{ color: 'var(--accent-green)', fontWeight: 800 }}>~{item.current_demand}%</span>
            </div>
          ))}
        </div>

        <div className="glass-card" style={{ gridColumn: 'span 3', padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--accent-warning)', marginBottom: '0.75rem' }}>
            🚀 Emerging Skills
          </h3>
          {topSkills?.emerging_skills?.map((item, idx) => (
            <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0', borderBottom: '1px solid var(--border-color)', fontSize: '0.9rem' }}>
              <span style={{ fontWeight: 700, color: '#fff' }}>{item.skill}</span>
              <span style={{ color: 'var(--accent-warning)', fontWeight: 800 }}>{item.growth_rate}</span>
            </div>
          ))}
        </div>

        <div className="glass-card" style={{ gridColumn: 'span 3', padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-subtle)', marginBottom: '0.75rem' }}>
            📉 Declining Trends
          </h3>
          {topSkills?.declining_skills?.map((item, idx) => (
            <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0', borderBottom: '1px solid var(--border-color)', fontSize: '0.9rem' }}>
              <span style={{ fontWeight: 700, color: '#fff' }}>{item.skill}</span>
              <span style={{ color: 'var(--text-subtle)', fontWeight: 800 }}>{item.growth_rate}</span>
            </div>
          ))}
        </div>

        {/* Skill Search & Time Series Chart View */}
        <div className="glass-card" style={{ gridColumn: 'span 8', padding: '1.75rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700 }}>
              📈 Skill Demand Trend & Forecast: <span style={{ color: 'var(--accent-purple)' }}>{skillForecast?.skill}</span>
            </h3>

            <form onSubmit={handleSearchSkill} style={{ display: 'flex', gap: '0.5rem' }}>
              <input
                type="text"
                className="input-field"
                placeholder="Search Skill (e.g. React)..."
                value={searchSkill}
                onChange={(e) => setSearchSkill(e.target.value)}
                style={{ padding: '0.4rem 0.75rem', fontSize: '0.85rem', width: '180px' }}
              />
              <button type="submit" className="btn btn-primary" style={{ padding: '0.4rem 0.85rem', fontSize: '0.85rem' }} disabled={searching}>
                {searching ? '...' : 'Search'}
              </button>
            </form>
          </div>

          {skillForecast && (
            <div>
              {/* Stat Gauges */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
                <div style={{ background: 'var(--bg-input)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-subtle)', fontWeight: 700 }}>CURRENT DEMAND RATE</div>
                  <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#fff' }}>{skillForecast.current_demand}%</div>
                </div>

                <div style={{ background: 'var(--bg-input)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-subtle)', fontWeight: 700 }}>PROJECTED {horizon} DEMAND</div>
                  <div style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--accent-green)' }}>{skillForecast.predicted_demand}%</div>
                </div>

                <div style={{ background: 'var(--bg-input)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-subtle)', fontWeight: 700 }}>CONFIDENCE BOUNDS</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--accent-purple)' }}>
                    {skillForecast.confidence_label || `[${skillForecast.lower_bound}% – ${skillForecast.upper_bound}%]`}
                  </div>
                </div>
              </div>

              {/* Simplified Time Series Visualization Bars */}
              <div style={{ marginTop: '1.5rem' }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-subtle)', marginBottom: '0.75rem', textTransform: 'uppercase' }}>
                  Historical Monthly Demand Rates (2025 - 2026)
                </div>
                <div style={{ display: 'flex', alignItems: 'flex-end', gap: '0.5rem', height: '140px', padding: '0.5rem 0', borderBottom: '1px solid var(--border-color)' }}>
                  {skillForecast.historical_rates?.map((val, idx) => (
                    <div key={idx} style={{ flex: 1, textAlign: 'center' }}>
                      <div
                        style={{
                          height: `${Math.max(15, val * 1.8)}px`,
                          background: 'linear-gradient(to top, var(--accent-blue), var(--accent-purple))',
                          borderRadius: '4px 4px 0 0',
                          transition: 'height 0.5s ease'
                        }}
                        title={`Period: ${skillForecast.periods?.[idx]} | Demand Rate: ${val}%`}
                      ></div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-subtle)', marginTop: '0.35rem' }}>{val}%</div>
                    </div>
                  ))}
                  {/* Forecast Line Bars */}
                  {skillForecast.forecast_rates?.map((val, idx) => (
                    <div key={`f-${idx}`} style={{ flex: 1, textAlign: 'center' }}>
                      <div
                        style={{
                          height: `${Math.max(15, val * 1.8)}px`,
                          background: 'linear-gradient(to top, var(--accent-pink), #f43f5e)',
                          borderRadius: '4px 4px 0 0',
                          opacity: 0.85
                        }}
                        title={`Forecast Period: ${skillForecast.forecast_periods?.[idx]} | Predicted: ${val}%`}
                      ></div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--accent-pink)', marginTop: '0.35rem', fontWeight: 700 }}>{val}%</div>
                    </div>
                  ))}
                </div>

                <div style={{ fontSize: '0.8rem', color: 'var(--text-subtle)', marginTop: '0.75rem', fontStyle: 'italic' }}>
                  ℹ️ Blue/Purple bars indicate historical monthly observations; Pink bars represent model forecast with ±{skillForecast.mae}% MAE bound.
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Selected Model & Accuracy Metrics Card */}
        <div className="glass-card" style={{ gridColumn: 'span 4', padding: '1.75rem' }}>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '1.25rem', color: 'var(--accent-purple)' }}>
            🤖 Selected Model & Accuracy
          </h3>

          {skillForecast && (
            <div>
              <div style={{ background: 'var(--bg-input)', padding: '1rem', borderRadius: 'var(--radius-md)', marginBottom: '1rem' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-subtle)', fontWeight: 700 }}>SELECTED ALGORITHM</div>
                <div style={{ fontSize: '1.15rem', fontWeight: 800, color: '#fff', marginTop: '0.25rem' }}>
                  {skillForecast.model_name}
                </div>
                <span className="badge badge-success" style={{ fontSize: '0.75rem', marginTop: '0.35rem' }}>
                  Lowest Validation Error
                </span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1rem' }}>
                <div style={{ background: 'var(--bg-input)', padding: '0.85rem', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)' }}>MAE (Mean Abs Error)</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--accent-green)' }}>{skillForecast.mae}</div>
                </div>

                <div style={{ background: 'var(--bg-input)', padding: '0.85rem', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)' }}>RMSE Error</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--accent-blue)' }}>{skillForecast.rmse}</div>
                </div>
              </div>

              <div style={{ background: 'var(--bg-input)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-subtle)', fontWeight: 700 }}>DATA RELIABILITY</div>
                <div style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--accent-green)', marginTop: '0.25rem' }}>
                  🟢 {skillForecast.reliability} RELIABILITY
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Personalized Future Skill Recommendations */}
        <div className="glass-card" style={{ gridColumn: 'span 12', padding: '1.75rem' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1.25rem' }}>
            🌟 Personalized Future Skill Recommendations
          </h3>

          {recommendations.length > 0 ? (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-subtle)', fontSize: '0.85rem', textTransform: 'uppercase' }}>
                    <th style={{ padding: '0.75rem 1rem' }}>Skill Name</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Priority</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Gap Category</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Predicted Market Demand</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Recommendation Rationale</th>
                  </tr>
                </thead>
                <tbody>
                  {recommendations.map((rec, idx) => (
                    <tr key={idx} style={{ borderBottom: '1px solid var(--border-color)', fontSize: '0.95rem' }}>
                      <td style={{ padding: '1rem', fontWeight: 700, color: '#fff' }}>{rec.skill}</td>
                      <td style={{ padding: '1rem' }}>
                        <span className={rec.priority === 'HIGH PRIORITY' ? 'badge badge-pink' : 'badge badge-primary'}>
                          {rec.priority}
                        </span>
                      </td>
                      <td style={{ padding: '1rem', color: 'var(--text-muted)' }}>{rec.gap_type}</td>
                      <td style={{ padding: '1rem', fontWeight: 800, color: 'var(--accent-green)' }}>{rec.predicted_market_demand}</td>
                      <td style={{ padding: '1rem', color: 'var(--text-muted)' }}>{rec.recommendation_reason}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p style={{ color: 'var(--text-muted)' }}>Analyze your resume to receive personalized future skill recommendations.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default SkillDemandPage;
