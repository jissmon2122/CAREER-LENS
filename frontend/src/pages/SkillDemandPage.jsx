import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { forecastingAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';

const FORECAST_CACHE_TTL = 15 * 60 * 1000;
let forecastMemoryCache = {
  topSkills: null,
  categories: [],
  recommendations: [],
  skillForecasts: {},
  timestamp: 0,
  horizon: 36,
  category: 'All Categories',
  algorithm: 'auto',
  lastSearchedSkill: 'Python',
  compareResults: null
};

const SkillDemandPage = () => {
  const isCacheValid = Boolean(
    forecastMemoryCache.topSkills &&
    (Date.now() - forecastMemoryCache.timestamp < FORECAST_CACHE_TTL)
  );

  const [horizon, setHorizon] = useState(forecastMemoryCache.horizon || 36);
  const [selectedCategory, setSelectedCategory] = useState(forecastMemoryCache.category || 'All Categories');
  const [selectedAlgorithm, setSelectedAlgorithm] = useState(forecastMemoryCache.algorithm || 'auto');
  const [categories, setCategories] = useState(forecastMemoryCache.categories || []);
  const [topSkills, setTopSkills] = useState(isCacheValid ? forecastMemoryCache.topSkills : null);
  const [recommendations, setRecommendations] = useState(isCacheValid ? forecastMemoryCache.recommendations : []);
  const [searchSkill, setSearchSkill] = useState(forecastMemoryCache.lastSearchedSkill || 'Python');
  const [skillForecast, setSkillForecast] = useState(
    isCacheValid && forecastMemoryCache.skillForecasts[forecastMemoryCache.lastSearchedSkill || 'Python']
      ? forecastMemoryCache.skillForecasts[forecastMemoryCache.lastSearchedSkill || 'Python']
      : null
  );

  // Multi-skill comparison state
  const [compareSkillsInput, setCompareSkillsInput] = useState('Python, SQL, React, AWS');
  const [compareData, setCompareData] = useState(forecastMemoryCache.compareResults || null);
  const [comparing, setComparing] = useState(false);
  const [compareError, setCompareError] = useState('');
  const [compareSuggestions, setCompareSuggestions] = useState([]);

  // Strict skill validation state
  const [validationError, setValidationError] = useState('');
  const [skillSuggestions, setSkillSuggestions] = useState([]);

  const [loading, setLoading] = useState(!isCacheValid);
  const [refreshing, setRefreshing] = useState(false);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState('');
  const [hoveredPoint, setHoveredPoint] = useState(null);

  // Fetch initial forecast data
  const fetchForecastData = useCallback(async (isManualRefresh = false) => {
    if (isManualRefresh) {
      setRefreshing(true);
    } else if (!isCacheValid) {
      setLoading(true);
    }
    setError('');

    try {
      const activeSkill = searchSkill.trim() || 'Python';
      const [topRes, catRes, recRes, pyRes, compRes] = await Promise.all([
        forecastingAPI.getTopSkills({ category: selectedCategory !== 'All Categories' ? selectedCategory : '', limit: 6 }),
        forecastingAPI.getCategories().catch(() => null),
        forecastingAPI.getRecommendations().catch(() => null),
        forecastingAPI.getSkillForecast(activeSkill, { horizon, model: selectedAlgorithm }).catch(() => null),
        forecastingAPI.compareSkills(compareSkillsInput, horizon).catch(() => null)
      ]);

      if (topRes?.success) {
        setTopSkills(topRes.data);
        forecastMemoryCache.topSkills = topRes.data;
      }
      if (catRes?.success && catRes.data?.categories) {
        setCategories(catRes.data.categories);
        forecastMemoryCache.categories = catRes.data.categories;
      }
      if (recRes?.success) {
        const recList = recRes.data.recommendations || [];
        setRecommendations(recList);
        forecastMemoryCache.recommendations = recList;
      }
      if (pyRes?.success && pyRes.data?.forecast) {
        setSkillForecast(pyRes.data.forecast);
        forecastMemoryCache.skillForecasts[activeSkill.toLowerCase()] = pyRes.data.forecast;
        forecastMemoryCache.lastSearchedSkill = activeSkill;
      }
      if (compRes?.success && compRes.data?.skills) {
        setCompareData(compRes.data);
        forecastMemoryCache.compareResults = compRes.data;
      }

      forecastMemoryCache.timestamp = Date.now();
    } catch (err) {
      console.error("Forecasting Error:", err);
      if (!isCacheValid) {
        setError("Failed to load skill demand forecasts.");
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [isCacheValid, searchSkill, horizon, selectedCategory, selectedAlgorithm, compareSkillsInput]);

  useEffect(() => {
    if (!isCacheValid) {
      fetchForecastData(false);
    }
  }, [isCacheValid, fetchForecastData]);

  // Handle Horizon Change
  const handleHorizonChange = async (h) => {
    setHorizon(h);
    forecastMemoryCache.horizon = h;
    if (skillForecast?.skill) {
      setSearching(true);
      try {
        const res = await forecastingAPI.getSkillForecast(skillForecast.skill, { horizon: h, model: selectedAlgorithm });
        if (res?.success && res.data?.forecast) {
          setSkillForecast(res.data.forecast);
        }
        const compRes = await forecastingAPI.compareSkills(compareSkillsInput, h);
        if (compRes?.success && compRes.data?.skills) {
          setCompareData(compRes.data);
        }
      } catch (err) {
        console.error("Horizon change error:", err);
      } finally {
        setSearching(false);
      }
    }
  };

  // Handle Category Filter Change
  const handleCategoryChange = async (cat) => {
    setSelectedCategory(cat);
    forecastMemoryCache.category = cat;
    try {
      const topRes = await forecastingAPI.getTopSkills({
        category: cat !== 'All Categories' ? cat : '',
        limit: 6
      });
      if (topRes?.success) {
        setTopSkills(topRes.data);
      }
    } catch (err) {
      console.error("Category change error:", err);
    }
  };

  // Handle Algorithm Switcher
  const handleAlgorithmChange = async (algo) => {
    setSelectedAlgorithm(algo);
    forecastMemoryCache.algorithm = algo;
    if (skillForecast?.skill) {
      setSearching(true);
      try {
        const res = await forecastingAPI.getSkillForecast(skillForecast.skill, { horizon, model: algo });
        if (res?.success && res.data?.forecast) {
          setSkillForecast(res.data.forecast);
        }
      } catch (err) {
        console.error("Algorithm change error:", err);
      } finally {
        setSearching(false);
      }
    }
  };

  // Search Single Skill
  const handleSearchSkill = async (e, directSkill = null) => {
    if (e) e.preventDefault();
    const query = (directSkill || searchSkill).trim();
    if (!query) return;

    setSearching(true);
    setValidationError('');
    setSkillSuggestions([]);

    try {
      const res = await forecastingAPI.getSkillForecast(query, { horizon, model: selectedAlgorithm });
      if (res?.success && res.data?.forecast) {
        setSkillForecast(res.data.forecast);
        setSearchSkill(res.data.forecast.skill);
        forecastMemoryCache.lastSearchedSkill = res.data.forecast.skill;
        forecastMemoryCache.skillForecasts[res.data.forecast.skill.toLowerCase()] = res.data.forecast;
        setValidationError('');
        setSkillSuggestions([]);
      }
    } catch (err) {
      console.error("Skill Search Error:", err);
      const apiErr = err.response?.data;
      if (apiErr?.error === 'INVALID_SKILL' || err.response?.status === 400) {
        // STRICT INVALID SKILL:
        // Do not display forecast chart, demand percentages, or trends
        setSkillForecast(null);
        setValidationError(apiErr?.message || `The entered term '${query}' is not a recognized technical skill.`);
        setSkillSuggestions(apiErr?.suggestions || ['Python', 'Java', 'JavaScript']);
      } else {
        setSkillForecast(null);
        setValidationError(`Unable to load forecast for '${query}'. Please select a recognized technical skill.`);
        setSkillSuggestions(['Python', 'Java', 'SQL', 'React', 'AWS', 'Docker']);
      }
    } finally {
      setSearching(false);
    }
  };

  // Run Multi-skill Comparison
  const handleRunComparison = async (e) => {
    e.preventDefault();
    if (!compareSkillsInput.trim()) return;
    setComparing(true);
    setCompareError('');
    setCompareSuggestions([]);
    try {
      const res = await forecastingAPI.compareSkills(compareSkillsInput, horizon);
      if (res?.success && res.data?.skills) {
        setCompareData(res.data);
      }
    } catch (err) {
      console.error("Comparison Error:", err);
      const apiErr = err.response?.data;
      if (apiErr?.error === 'INVALID_SKILL' || err.response?.status === 400) {
        setCompareError(apiErr?.message || "Invalid technical skills entered in comparison list.");
        setCompareSuggestions(apiErr?.suggestions || ['Python', 'Java', 'JavaScript']);
      } else {
        setCompareError("Unable to compare skills. Please ensure valid skills are entered.");
      }
    } finally {
      setComparing(false);
    }
  };

  // SVG Chart Dimensions & Coordinate Calculations
  const chartDimensions = { width: 850, height: 280, padL: 45, padR: 35, padT: 30, padB: 40 };

  const chartSeries = useMemo(() => {
    if (!skillForecast) return null;

    const histPeriods = skillForecast.periods || [];
    const histRates = skillForecast.historical_rates || [];
    const forePeriods = skillForecast.forecast_periods || [];
    const foreRates = skillForecast.forecast_rates || [];
    const lowerBounds = skillForecast.forecast_lower_bounds || [];
    const upperBounds = skillForecast.forecast_upper_bounds || [];

    // All distinct timeline periods
    const allLabels = [...histPeriods, ...forePeriods];
    const nHist = histPeriods.length;
    const nTotal = allLabels.length;

    if (nTotal === 0) return null;

    // Determine max value for vertical scaling
    const maxVal = Math.max(
      3.0,
      ...histRates,
      ...foreRates,
      ...upperBounds
    );
    const yMax = Math.ceil(maxVal * 1.25);

    const { width, height, padL, padR, padT, padB } = chartDimensions;
    const plotW = width - padL - padR;
    const plotH = height - padT - padB;

    const getX = (idx) => padL + (idx / Math.max(1, nTotal - 1)) * plotW;
    const getY = (val) => padT + plotH - (Math.max(0, val) / yMax) * plotH;

    // Historical Points
    const histPoints = histRates.map((r, i) => ({
      x: getX(i),
      y: getY(r),
      period: histPeriods[i],
      val: r,
      isForecast: false
    }));

    // Forecast Points (starts connecting from last historical point)
    const forePoints = [];
    if (histPoints.length > 0) {
      forePoints.push({
        ...histPoints[histPoints.length - 1],
        isForecast: true
      });
    }

    foreRates.forEach((r, i) => {
      const idx = nHist + i;
      forePoints.push({
        x: getX(idx),
        y: getY(r),
        period: forePeriods[i],
        val: r,
        lower: lowerBounds[i] ?? r,
        upper: upperBounds[i] ?? r,
        isForecast: true
      });
    });

    // SVG Path Strings
    const histPath = histPoints.length > 0
      ? `M ${histPoints.map((p) => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' L ')}`
      : '';

    const forePath = forePoints.length > 0
      ? `M ${forePoints.map((p) => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' L ')}`
      : '';

    // Area Path for Confidence Interval Band
    let ciAreaPath = '';
    if (forePoints.length > 1) {
      const upperCoords = [];
      const lowerCoords = [];
      for (let i = 1; i < forePoints.length; i++) {
        const pt = forePoints[i];
        upperCoords.push(`${pt.x.toFixed(1)},${getY(pt.upper).toFixed(1)}`);
        lowerCoords.unshift(`${pt.x.toFixed(1)},${getY(pt.lower).toFixed(1)}`);
      }
      ciAreaPath = `M ${upperCoords.join(' L ')} L ${lowerCoords.join(' L ')} Z`;
    }

    const splitX = getX(nHist - 1);

    return {
      allLabels,
      nHist,
      nTotal,
      yMax,
      histPoints,
      forePoints,
      histPath,
      forePath,
      ciAreaPath,
      splitX,
      getX,
      getY
    };
  }, [skillForecast]);

  if (loading) {
    return (
      <div className="container" style={{ padding: '4rem 1rem', textAlign: 'center' }}>
        <LoadingSpinner text="Ingesting 2023–2026 employer vacancy series, fitting 4 time-series models, and evaluating 36-month projections..." />
      </div>
    );
  }

  return (
    <div className="container" style={{ padding: '2.5rem 1rem 5rem' }}>
      {/* Page Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.5rem' }}>
            <span className="badge badge-purple">AI Core Engine</span>
            <span className="badge badge-blue">Continuous 2023–2026 Baseline</span>
            <span className="badge badge-pink">36-Month Forecasting Horizon</span>
          </div>
          <h1 style={{ fontSize: '2.25rem', fontWeight: 800 }}>Skill Demand Forecasting & Analytics</h1>
          <p style={{ color: 'var(--text-subtle)', maxWidth: '780px' }}>
            Rigorous mathematical time-series modeling evaluating Naive Baseline, Moving Average, Linear Regression, and Damped Exponential Smoothing across real employer vacancy data.
          </p>
        </div>

        {/* Global Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          {refreshing && (
            <span className="badge badge-purple" style={{ fontSize: '0.75rem', animation: 'pulse 1.5s infinite' }}>
              Re-evaluating models...
            </span>
          )}

          <button
            onClick={() => fetchForecastData(true)}
            disabled={loading || refreshing}
            className="btn btn-secondary"
            style={{ fontSize: '0.85rem', padding: '0.5rem 0.95rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
          >
            <span>🔄</span>
            {refreshing ? 'Updating...' : 'Re-run Evaluation'}
          </button>

          {/* Horizon Selector */}
          <div style={{ background: 'var(--bg-input)', padding: '0.3rem', borderRadius: 'var(--radius-md)', display: 'flex', gap: '0.3rem' }}>
            {[6, 12, 24, 36].map((h) => (
              <button
                key={h}
                onClick={() => handleHorizonChange(h)}
                className={horizon === h ? 'btn btn-primary' : 'btn btn-secondary'}
                style={{ fontSize: '0.82rem', padding: '0.4rem 0.75rem' }}
              >
                {h}M {h === 36 ? '(3 Yrs)' : ''}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Category Filter Pills */}
      <div style={{ marginBottom: '1.75rem' }}>
        <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-subtle)', textTransform: 'uppercase', marginBottom: '0.6rem' }}>
          Filter by Industry Domain / Skill Category:
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {['All Categories', 'Programming', 'AI & ML', 'Frontend Development', 'Backend Development', 'Database / Data Analytics', 'Cloud Computing', 'DevOps / Cloud', 'Security', 'Core Engineering / Operations', 'Finance & Accounting', 'Marketing & Sales'].map((cat) => (
            <button
              key={cat}
              onClick={() => handleCategoryChange(cat)}
              className={selectedCategory === cat ? 'btn btn-primary' : 'btn btn-secondary'}
              style={{
                fontSize: '0.78rem',
                padding: '0.35rem 0.75rem',
                borderRadius: '20px',
                border: selectedCategory === cat ? '1px solid var(--accent-purple)' : '1px solid var(--border-color)'
              }}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Top Trend Classification Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '1.25rem', marginBottom: '2rem' }}>
        <div className="glass-card" style={{ gridColumn: 'span 3', padding: '1.25rem' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--accent-pink)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            🔥 Top Rising Skills
          </h3>
          {topSkills?.rising_skills?.map((item, idx) => (
            <div
              key={idx}
              onClick={() => handleSearchSkill(null, item.skill)}
              style={{ display: 'flex', justifyContent: 'space-between', padding: '0.45rem 0', borderBottom: '1px solid var(--border-color)', fontSize: '0.88rem', cursor: 'pointer' }}
              title="Click to view full forecast"
            >
              <span style={{ fontWeight: 700, color: '#fff' }}>{item.skill}</span>
              <span style={{ color: 'var(--accent-pink)', fontWeight: 800 }}>{item.growth_rate}</span>
            </div>
          ))}
        </div>

        <div className="glass-card" style={{ gridColumn: 'span 3', padding: '1.25rem' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--accent-green)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            🟢 Stable Core Skills
          </h3>
          {topSkills?.stable_skills?.map((item, idx) => (
            <div
              key={idx}
              onClick={() => handleSearchSkill(null, item.skill)}
              style={{ display: 'flex', justifyContent: 'space-between', padding: '0.45rem 0', borderBottom: '1px solid var(--border-color)', fontSize: '0.88rem', cursor: 'pointer' }}
              title="Click to view full forecast"
            >
              <span style={{ fontWeight: 700, color: '#fff' }}>{item.skill}</span>
              <span style={{ color: 'var(--accent-green)', fontWeight: 800 }}>~{item.current_demand}%</span>
            </div>
          ))}
        </div>

        <div className="glass-card" style={{ gridColumn: 'span 3', padding: '1.25rem' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--accent-warning)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            🚀 Emerging Skills
          </h3>
          {topSkills?.emerging_skills?.map((item, idx) => (
            <div
              key={idx}
              onClick={() => handleSearchSkill(null, item.skill)}
              style={{ display: 'flex', justifyContent: 'space-between', padding: '0.45rem 0', borderBottom: '1px solid var(--border-color)', fontSize: '0.88rem', cursor: 'pointer' }}
              title="Click to view full forecast"
            >
              <span style={{ fontWeight: 700, color: '#fff' }}>{item.skill}</span>
              <span style={{ color: 'var(--accent-warning)', fontWeight: 800 }}>{item.growth_rate}</span>
            </div>
          ))}
        </div>

        <div className="glass-card" style={{ gridColumn: 'span 3', padding: '1.25rem' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-subtle)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            📉 Declining Trends
          </h3>
          {topSkills?.declining_skills?.map((item, idx) => (
            <div
              key={idx}
              onClick={() => handleSearchSkill(null, item.skill)}
              style={{ display: 'flex', justifyContent: 'space-between', padding: '0.45rem 0', borderBottom: '1px solid var(--border-color)', fontSize: '0.88rem', cursor: 'pointer' }}
              title="Click to view full forecast"
            >
              <span style={{ fontWeight: 700, color: '#fff' }}>{item.skill}</span>
              <span style={{ color: 'var(--text-subtle)', fontWeight: 800 }}>{item.growth_rate}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Main Focus: Individual Skill Demand & Interactive Forecast Chart */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '1.5rem', marginBottom: '2.5rem' }}>
        <div className="glass-card" style={{ gridColumn: 'span 8', padding: '1.75rem' }}>
          {/* Chart Header & Skill Search */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              {validationError ? (
                <div>
                  <h3 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#f87171', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <span>⚠️</span> Unrecognized Skill
                  </h3>
                  <div style={{ fontSize: '0.82rem', color: 'var(--text-subtle)', marginTop: '0.2rem' }}>
                    Skill Demand Forecasting is strictly restricted to verified industry technical skills.
                  </div>
                </div>
              ) : (
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <h3 style={{ fontSize: '1.35rem', fontWeight: 800 }}>
                      📈 {skillForecast?.skill || 'Python'}
                    </h3>
                    <span className="badge badge-purple">{skillForecast?.category || 'Programming'}</span>
                    <span className={skillForecast?.trend === 'RISING' ? 'badge badge-pink' : skillForecast?.trend === 'EMERGING' ? 'badge badge-warning' : 'badge badge-success'}>
                      {skillForecast?.trend_label || 'Stable'}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.82rem', color: 'var(--text-subtle)', marginTop: '0.2rem' }}>
                    Historical observations: <strong style={{ color: '#fff' }}>2023-01 to 2026-11 (47 mos)</strong> | Forecast horizon: <strong style={{ color: 'var(--accent-pink)' }}>Next {horizon} Months (to {skillForecast?.forecast_periods?.[skillForecast?.forecast_periods?.length - 1] || '2029-11'})</strong>
                  </div>
                </div>
              )}
            </div>

            <form onSubmit={handleSearchSkill} style={{ display: 'flex', gap: '0.4rem' }}>
              <input
                type="text"
                className="input-field"
                placeholder="Search skill (e.g. React, AWS)..."
                value={searchSkill}
                onChange={(e) => setSearchSkill(e.target.value)}
                style={{ padding: '0.4rem 0.75rem', fontSize: '0.85rem', width: '210px' }}
              />
              <button type="submit" className="btn btn-primary" style={{ padding: '0.4rem 0.85rem', fontSize: '0.85rem' }} disabled={searching}>
                {searching ? '...' : 'Forecast'}
              </button>
            </form>
          </div>

          {/* If Validation Error, display strict Invalid Skill Alert & Suggestions; hide charts, demand percentages & trends */}
          {validationError ? (
            <div style={{
              background: 'rgba(239, 68, 68, 0.08)',
              border: '1px solid rgba(239, 68, 68, 0.35)',
              borderRadius: 'var(--radius-lg)',
              padding: '2.5rem 1.5rem',
              textAlign: 'center',
              marginTop: '1rem',
              marginBottom: '1rem'
            }}>
              <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>❌</div>
              <h4 style={{ color: '#f87171', fontSize: '1.2rem', fontWeight: 800, marginBottom: '0.5rem' }}>
                Unrecognized Technical Skill
              </h4>
              <p style={{ color: '#fca5a5', fontSize: '0.92rem', maxWidth: '520px', margin: '0 auto 1.5rem auto', lineHeight: 1.5 }}>
                {validationError}
              </p>

              {skillSuggestions && skillSuggestions.length > 0 && (
                <div style={{ marginTop: '1rem', paddingTop: '1.25rem', borderTop: '1px solid rgba(239, 68, 68, 0.2)' }}>
                  <div style={{ fontSize: '0.82rem', color: 'var(--text-subtle)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '0.75rem' }}>
                    Suggested Technical Skills from Trusted Registry:
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                    {skillSuggestions.map((sug) => (
                      <button
                        key={sug}
                        onClick={() => handleSearchSkill(null, sug)}
                        className="btn btn-secondary"
                        style={{
                          fontSize: '0.82rem',
                          padding: '0.4rem 0.9rem',
                          borderRadius: '20px',
                          border: '1px solid rgba(255, 255, 255, 0.2)',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.35rem',
                          cursor: 'pointer'
                        }}
                      >
                        <span>⚡</span>
                        <strong>{sug}</strong>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <>
              {/* Insufficient Data Warning Banner if applicable */}
              {!skillForecast?.has_sufficient_data && (
                <div style={{ background: 'rgba(234, 179, 8, 0.12)', border: '1px solid var(--accent-warning)', borderRadius: 'var(--radius-md)', padding: '0.75rem 1rem', marginBottom: '1.25rem', fontSize: '0.85rem', color: '#fef08a' }}>
                  ⚠️ <strong>Limited Historical Observations:</strong> The technical skill &lsquo;{skillForecast?.skill}&rsquo; is recognized, but has limited vacancy postings in this dataset. Forecasts are shown with conservative bounds.
                </div>
              )}

              {/* Metric KPI Gauges */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.75rem', marginBottom: '1.5rem' }}>
                <div style={{ background: 'var(--bg-input)', padding: '0.85rem 1rem', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-subtle)', fontWeight: 700 }}>CURRENT DEMAND RATE</div>
                  <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#fff' }}>{skillForecast?.current_demand}%</div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-subtle)' }}>Market share as of Nov 2026</div>
                </div>

                <div style={{ background: 'var(--bg-input)', padding: '0.85rem 1rem', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-subtle)', fontWeight: 700 }}>{horizon}M PROJECTED DEMAND</div>
                  <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--accent-green)' }}>{skillForecast?.predicted_demand}%</div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--accent-green)', fontWeight: 700 }}>{skillForecast?.growth_rate} absolute growth</div>
                </div>

                <div style={{ background: 'var(--bg-input)', padding: '0.85rem 1rem', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-subtle)', fontWeight: 700 }}>RELATIVE GROWTH</div>
                  <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--accent-purple)' }}>{skillForecast?.relative_growth}</div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-subtle)' }}>Trend momentum rate</div>
                </div>

                <div style={{ background: 'var(--bg-input)', padding: '0.85rem 1rem', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-subtle)', fontWeight: 700 }}>95% CONFIDENCE INTERVAL</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--accent-pink)', marginTop: '0.2rem' }}>
                    [{skillForecast?.lower_bound}% – {skillForecast?.upper_bound}%]
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-subtle)' }}>±{skillForecast?.mae}% empirical error</div>
                </div>
              </div>

              {/* Interactive Time-Series SVG Chart */}
              <div style={{ background: 'rgba(15, 23, 42, 0.65)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)', padding: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', fontSize: '0.82rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                      <span style={{ width: '12px', height: '3px', background: '#38bdf8', display: 'inline-block' }}></span>
                      <span style={{ color: '#fff' }}>Historical Observations (2023–2026)</span>
                    </span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                      <span style={{ width: '12px', height: '3px', background: '#f43f5e', borderTop: '2px dashed #f43f5e', display: 'inline-block' }}></span>
                      <span style={{ color: 'var(--accent-pink)' }}>{skillForecast?.model_name || 'Selected'} Forecast (Next {horizon}M)</span>
                    </span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                      <span style={{ width: '12px', height: '8px', background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.4)', display: 'inline-block' }}></span>
                      <span style={{ color: 'var(--text-subtle)' }}>Confidence Interval Band</span>
                    </span>
                  </div>

                  {hoveredPoint && (
                    <div style={{ background: 'var(--bg-input)', padding: '0.25rem 0.6rem', borderRadius: '4px', border: '1px solid var(--border-color)', fontSize: '0.78rem' }}>
                      <strong>{hoveredPoint.period}</strong>: <span style={{ color: hoveredPoint.isForecast ? 'var(--accent-pink)' : '#38bdf8' }}>{hoveredPoint.val}%</span>
                      {hoveredPoint.isForecast && (
                        <span style={{ color: 'var(--text-subtle)', marginLeft: '0.35rem' }}>
                          (CI: [{hoveredPoint.lower}% – {hoveredPoint.upper}%])
                        </span>
                      )}
                    </div>
                  )}
                </div>

                {chartSeries ? (
                  <svg
                    viewBox={`0 0 ${chartDimensions.width} ${chartDimensions.height}`}
                    style={{ width: '100%', height: 'auto', display: 'block', overflow: 'visible' }}
                  >
                    <defs>
                      <linearGradient id="histGrad" x1="0" y1="0" x2="1" y2="0">
                        <stop offset="0%" stopColor="#0284c7" />
                        <stop offset="100%" stopColor="#38bdf8" />
                      </linearGradient>
                    </defs>

                    {/* Horizontal Grid Lines */}
                    {[0, 0.25, 0.5, 0.75, 1.0].map((frac, idx) => {
                      const yVal = frac * chartSeries.yMax;
                      const yPos = chartSeries.getY(yVal);
                      return (
                        <g key={idx}>
                          <line
                            x1={chartDimensions.padL}
                            y1={yPos}
                            x2={chartDimensions.width - chartDimensions.padR}
                            y2={yPos}
                            stroke="rgba(255, 255, 255, 0.08)"
                            strokeDasharray="3 3"
                          />
                          <text
                            x={chartDimensions.padL - 8}
                            y={yPos + 4}
                            fill="var(--text-subtle)"
                            fontSize="10"
                            textAnchor="end"
                          >
                            {yVal.toFixed(1)}%
                          </text>
                        </g>
                      );
                    })}

                    {/* Vertical Divider separating History from Future */}
                    <line
                      x1={chartSeries.splitX}
                      y1={chartDimensions.padT}
                      x2={chartSeries.splitX}
                      y2={chartDimensions.height - chartDimensions.padB}
                      stroke="#a855f7"
                      strokeWidth="1.5"
                      strokeDasharray="4 4"
                    />
                    <text
                      x={chartSeries.splitX}
                      y={chartDimensions.padT - 8}
                      fill="#c084fc"
                      fontSize="11"
                      fontWeight="700"
                      textAnchor="middle"
                    >
                      ◀ Actual Historical | Future Projected ▶
                    </text>

                    {/* Shaded Confidence Interval Band */}
                    {chartSeries.ciAreaPath && (
                      <path
                        d={chartSeries.ciAreaPath}
                        fill="rgba(244, 63, 94, 0.12)"
                        stroke="none"
                      />
                    )}

                    {/* Historical Observed Curve */}
                    <path
                      d={chartSeries.histPath}
                      fill="none"
                      stroke="url(#histGrad)"
                      strokeWidth="2.5"
                    />

                    {/* Forecast Projected Curve (Dashed) */}
                    <path
                      d={chartSeries.forePath}
                      fill="none"
                      stroke="#f43f5e"
                      strokeWidth="2.5"
                      strokeDasharray="5 4"
                    />

                    {/* Interactive Points on Historical Line */}
                    {chartSeries.histPoints.filter((_, idx) => idx % 3 === 0 || idx === chartSeries.histPoints.length - 1).map((pt, idx) => (
                      <circle
                        key={`hp-${idx}`}
                        cx={pt.x}
                        cy={pt.y}
                        r="3.5"
                        fill="#38bdf8"
                        stroke="#0f172a"
                        strokeWidth="1.5"
                        onMouseEnter={() => setHoveredPoint(pt)}
                        onMouseLeave={() => setHoveredPoint(null)}
                        style={{ cursor: 'pointer' }}
                      />
                    ))}

                    {/* Interactive Points on Forecast Line */}
                    {chartSeries.forePoints.map((pt, idx) => (
                      <circle
                        key={`fp-${idx}`}
                        cx={pt.x}
                        cy={pt.y}
                        r="3.5"
                        fill="#f43f5e"
                        stroke="#0f172a"
                        strokeWidth="1.5"
                        onMouseEnter={() => setHoveredPoint(pt)}
                        onMouseLeave={() => setHoveredPoint(null)}
                        style={{ cursor: 'pointer' }}
                      />
                    ))}

                    {/* X-Axis Date Labels (Every 6 months) */}
                    {chartSeries.allLabels.map((lbl, idx) => {
                      if (idx % 6 !== 0 && idx !== chartSeries.nHist - 1 && idx !== chartSeries.nTotal - 1) return null;
                      const x = chartSeries.getX(idx);
                      const isFuture = idx >= chartSeries.nHist;
                      return (
                        <text
                          key={`xl-${idx}`}
                          x={x}
                          y={chartDimensions.height - chartDimensions.padB + 18}
                          fill={isFuture ? 'var(--accent-pink)' : 'var(--text-subtle)'}
                          fontSize="9.5"
                          fontWeight={idx === chartSeries.nHist - 1 || idx === chartSeries.nTotal - 1 ? '700' : '400'}
                          textAnchor="middle"
                        >
                          {lbl}
                        </text>
                      );
                    })}
                  </svg>
                ) : (
                  <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                    No time-series data available for this skill.
                  </div>
                )}
              </div>
            </>
          )}
        </div>

        {/* Selected Model & 4-Algorithm Evaluation Panel */}
        <div className="glass-card" style={{ gridColumn: 'span 4', padding: '1.75rem' }}>
          {validationError ? (
            <div>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 800, marginBottom: '1.25rem', color: 'var(--accent-purple)' }}>
                🛡️ Trusted Skill Registry
              </h3>
              <p style={{ fontSize: '0.86rem', color: 'var(--text-subtle)', lineHeight: 1.5, marginBottom: '1rem' }}>
                Career Lens validates skills against an authoritative registry to guarantee high-confidence predictions. Random words, typos, and non-technical terms are blocked to prevent distorted forecasting.
              </p>
              <div style={{ background: 'var(--bg-input)', padding: '1rem', borderRadius: 'var(--radius-md)', marginBottom: '1.25rem' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '0.5rem' }}>
                  Supported Technical Domains:
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', fontSize: '0.82rem' }}>
                  <div>💻 <strong>Programming:</strong> Python, Java, C++, Go, Rust...</div>
                  <div>🧠 <strong>AI & ML:</strong> Machine Learning, PyTorch, NLP...</div>
                  <div>📊 <strong>Data & BI:</strong> SQL, MongoDB, Power BI, Spark...</div>
                  <div>☁️ <strong>Cloud & DevOps:</strong> AWS, Azure, Docker, K8s...</div>
                  <div>🌐 <strong>Web:</strong> React, Node.js, Next.js, Django...</div>
                  <div>🔒 <strong>Security:</strong> Cybersecurity, Ethical Hacking...</div>
                </div>
              </div>
              <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-subtle)', marginBottom: '0.6rem' }}>
                QUICK SELECT POPULAR SKILL:
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.4rem' }}>
                {['Python', 'SQL', 'React', 'AWS', 'Docker', 'Java'].map((quickSkill) => (
                  <button
                    key={quickSkill}
                    onClick={() => handleSearchSkill(null, quickSkill)}
                    className="btn btn-secondary"
                    style={{ fontSize: '0.78rem', padding: '0.4rem 0.5rem', textAlign: 'center' }}
                  >
                    📈 {quickSkill}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 800, marginBottom: '1.25rem', color: 'var(--accent-purple)' }}>
                🤖 Multi-Model Validation & Audit
              </h3>

              {/* Model Switcher Dropdown / Pills */}
              <div style={{ marginBottom: '1.25rem' }}>
                <div style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-subtle)', textTransform: 'uppercase', marginBottom: '0.4rem' }}>
                  Select Active Algorithm:
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.4rem' }}>
                  {[
                    { id: 'auto', label: 'Auto (Best MAE)' },
                    { id: 'exponential_smoothing', label: 'Exp Smoothing' },
                    { id: 'linear_regression', label: 'Linear Trend' },
                    { id: 'moving_average', label: 'Moving Avg' },
                    { id: 'naive', label: 'Naive Baseline' }
                  ].map((m) => (
                    <button
                      key={m.id}
                      onClick={() => handleAlgorithmChange(m.id)}
                      className={selectedAlgorithm === m.id ? 'btn btn-primary' : 'btn btn-secondary'}
                      style={{ fontSize: '0.78rem', padding: '0.4rem 0.5rem', textAlign: 'center' }}
                    >
                      {m.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Evaluation Metrics on Active Model */}
              <div style={{ background: 'var(--bg-input)', padding: '1rem', borderRadius: 'var(--radius-md)', marginBottom: '1.25rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', fontWeight: 700 }}>SELECTED ALGORITHM</div>
                  <span className="badge badge-success" style={{ fontSize: '0.7rem' }}>
                    {skillForecast?.reliability || 'HIGH'} RELIABILITY
                  </span>
                </div>
                <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#fff', marginTop: '0.25rem' }}>
                  {skillForecast?.model_name || 'Exponential Smoothing'}
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-subtle)', marginTop: '0.35rem' }}>
                  {skillForecast?.reason}
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.5rem', marginBottom: '1.25rem' }}>
                <div style={{ background: 'var(--bg-input)', padding: '0.75rem', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-subtle)' }}>MAE</div>
                  <div style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--accent-green)' }}>{skillForecast?.mae}</div>
                </div>

                <div style={{ background: 'var(--bg-input)', padding: '0.75rem', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-subtle)' }}>RMSE</div>
                  <div style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--accent-blue)' }}>{skillForecast?.rmse}</div>
                </div>

                <div style={{ background: 'var(--bg-input)', padding: '0.75rem', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-subtle)' }}>MAPE</div>
                  <div style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--accent-purple)' }}>
                    {skillForecast?.mape ? `${skillForecast.mape}%` : 'N/A'}
                  </div>
                </div>
              </div>

              {/* 4-Algorithm Benchmark Comparison Table */}
              <div style={{ marginTop: '1rem' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-subtle)', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
                  Candidate Algorithms Accuracy (Validation Split):
                </div>
                <table style={{ width: '100%', fontSize: '0.82rem', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-subtle)' }}>
                      <th style={{ textAlign: 'left', padding: '0.4rem 0' }}>Algorithm</th>
                      <th style={{ textAlign: 'right', padding: '0.4rem 0' }}>MAE</th>
                      <th style={{ textAlign: 'right', padding: '0.4rem 0' }}>RMSE</th>
                      <th style={{ textAlign: 'right', padding: '0.4rem 0' }}>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {skillForecast?.model_comparisons?.map((c, idx) => (
                      <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                        <td style={{ padding: '0.45rem 0', fontWeight: c.is_best ? '800' : '400', color: c.is_best ? 'var(--accent-green)' : '#cbd5e1' }}>
                          {c.name}
                        </td>
                        <td style={{ textAlign: 'right', padding: '0.45rem 0', color: c.is_best ? 'var(--accent-green)' : 'inherit' }}>
                          {c.mae}
                        </td>
                        <td style={{ textAlign: 'right', padding: '0.45rem 0' }}>
                          {c.rmse}
                        </td>
                        <td style={{ textAlign: 'right', padding: '0.45rem 0' }}>
                          {c.is_best ? (
                            <span className="badge badge-success" style={{ fontSize: '0.65rem' }}>Best Fit</span>
                          ) : (
                            <span style={{ color: 'var(--text-subtle)', fontSize: '0.72rem' }}>Candidate</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Multi-Skill Demand Comparison Section */}
      <div className="glass-card" style={{ padding: '1.75rem', marginBottom: '2.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 800 }}>
              📊 Multi-Skill Demand Comparison ({horizon} Months)
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-subtle)' }}>
              Compare projected market trajectories across different programming languages, cloud platforms, and data tools.
            </p>
          </div>

          <form onSubmit={handleRunComparison} style={{ display: 'flex', gap: '0.5rem' }}>
            <input
              type="text"
              className="input-field"
              value={compareSkillsInput}
              onChange={(e) => setCompareSkillsInput(e.target.value)}
              placeholder="e.g. Python, SQL, React, AWS, Docker"
              style={{ width: '280px', padding: '0.45rem 0.75rem', fontSize: '0.85rem' }}
            />
            <button type="submit" className="btn btn-primary" style={{ fontSize: '0.85rem', padding: '0.45rem 0.95rem' }} disabled={comparing}>
              {comparing ? 'Comparing...' : 'Compare Skills'}
            </button>
          </form>
        </div>

        {compareError && (
          <div style={{
            background: 'rgba(239, 68, 68, 0.08)',
            border: '1px solid rgba(239, 68, 68, 0.35)',
            borderRadius: 'var(--radius-md)',
            padding: '1.25rem 1.5rem',
            marginBottom: '1.5rem',
            color: '#fca5a5',
            fontSize: '0.9rem'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 800, color: '#f87171', marginBottom: '0.4rem' }}>
              <span>⚠️</span> Invalid Comparison Query
            </div>
            <div>{compareError}</div>
            {compareSuggestions && compareSuggestions.length > 0 && (
              <div style={{ marginTop: '0.75rem', display: 'flex', gap: '0.4rem', alignItems: 'center', flexWrap: 'wrap' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-subtle)', fontWeight: 700 }}>Try valid technical skills:</span>
                {compareSuggestions.map(s => (
                  <button
                    key={s}
                    type="button"
                    onClick={() => {
                      setCompareSkillsInput(prev => `${prev ? prev + ', ' : ''}${s}`);
                      setCompareError('');
                    }}
                    className="btn btn-secondary"
                    style={{ fontSize: '0.75rem', padding: '0.25rem 0.6rem', borderRadius: '15px' }}
                  >
                    + {s}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {compareData?.skills && compareData.skills.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-subtle)', fontSize: '0.8rem', textTransform: 'uppercase' }}>
                  <th style={{ padding: '0.75rem 1rem' }}>Skill</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Domain Category</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Current Rate</th>
                  <th style={{ padding: '0.75rem 1rem' }}>{horizon}M Projected</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Growth Trajectory</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Optimal Model</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {compareData.skills.map((item, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid var(--border-color)' }}>
                    <td style={{ padding: '0.85rem 1rem', fontWeight: 800, color: '#fff' }}>{item.skill}</td>
                    <td style={{ padding: '0.85rem 1rem' }}>
                      <span className="badge badge-purple" style={{ fontSize: '0.75rem' }}>{item.category}</span>
                    </td>
                    <td style={{ padding: '0.85rem 1rem', fontWeight: 700 }}>{item.current_demand}%</td>
                    <td style={{ padding: '0.85rem 1rem', fontWeight: 800, color: 'var(--accent-green)' }}>{item.predicted_demand}%</td>
                    <td style={{ padding: '0.85rem 1rem' }}>
                      <span className={item.trend === 'RISING' ? 'badge badge-pink' : item.trend === 'EMERGING' ? 'badge badge-warning' : 'badge badge-success'}>
                        {item.growth_rate} ({item.trend})
                      </span>
                    </td>
                    <td style={{ padding: '0.85rem 1rem', color: 'var(--text-muted)' }}>{item.model_name} (MAE: {item.mae})</td>
                    <td style={{ padding: '0.85rem 1rem' }}>
                      <button
                        onClick={() => handleSearchSkill(null, item.skill)}
                        className="btn btn-secondary"
                        style={{ fontSize: '0.75rem', padding: '0.3rem 0.65rem' }}
                      >
                        Inspect Chart 🔍
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p style={{ color: 'var(--text-muted)' }}>Enter comma-separated skills above to compare their demand trends.</p>
        )}
      </div>

      {/* Personalized Future Skill Recommendations (Resume Gap Integration) */}
      <div className="glass-card" style={{ padding: '1.75rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 800 }}>
              🌟 Personalized Strategic Upskilling Recommendations
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-subtle)' }}>
              Synthesizes your parsed resume gaps with predicted 36-month market momentum to prioritize high-ROI learning.
            </p>
          </div>
        </div>

        {recommendations.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-subtle)', fontSize: '0.8rem', textTransform: 'uppercase' }}>
                  <th style={{ padding: '0.75rem 1rem' }}>Recommended Skill</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Priority Tier</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Skill Gap Type</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Market Trajectory</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Strategic Rationale</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {recommendations.map((rec, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid var(--border-color)' }}>
                    <td style={{ padding: '1rem', fontWeight: 800, color: '#fff' }}>{rec.skill}</td>
                    <td style={{ padding: '1rem' }}>
                      <span className={rec.priority === 'HIGH PRIORITY' ? 'badge badge-pink' : 'badge badge-primary'}>
                        {rec.priority}
                      </span>
                    </td>
                    <td style={{ padding: '1rem', color: 'var(--text-muted)' }}>{rec.gap_type}</td>
                    <td style={{ padding: '1rem', fontWeight: 800, color: 'var(--accent-green)' }}>
                      {rec.predicted_market_demand}
                    </td>
                    <td style={{ padding: '1rem', color: 'var(--text-muted)', maxWidth: '320px' }}>
                      {rec.recommendation_reason}
                    </td>
                    <td style={{ padding: '1rem' }}>
                      <button
                        onClick={() => handleSearchSkill(null, rec.skill)}
                        className="btn btn-secondary"
                        style={{ fontSize: '0.75rem', padding: '0.35rem 0.7rem' }}
                      >
                        Forecast 📈
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p style={{ color: 'var(--text-muted)' }}>Upload and analyze your resume in the Resume module to see personalized skill gap forecasts.</p>
        )}
      </div>
    </div>
  );
};

export default SkillDemandPage;
