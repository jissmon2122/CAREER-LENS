import React, { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react';
import { jobAPI } from '../services/api';
import { useAuth } from './AuthContext';

const JobContext = createContext(null);

const CACHE_TTL_MS = 15 * 60 * 1000; // 15 minutes stale time

export const JobProvider = ({ children }) => {
  const { user, isAuthenticated } = useAuth();
  const currentUserId = user?.id || user?._id || null;

  // Stored live recommendations
  const [liveJobsData, setLiveJobsData] = useState(null);
  const [lastUpdatedAt, setLastUpdatedAt] = useState('');
  const [candidateProfile, setCandidateProfile] = useState(null);
  const [buckets, setBuckets] = useState({
    highly_relevant: [],
    relevant: [],
    potential: [],
    all_recommendations: []
  });

  // Stored filters so they persist across page navigation
  const [filters, setFilters] = useState({
    selectedRole: '',
    location: '',
    remote: '',
    experience: '',
    minMatch: '',
    activeTab: 'all'
  });

  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [resumeRequired, setResumeRequired] = useState(false);
  const [savedJobIds, setSavedJobIds] = useState(new Set());

  // Cache metadata
  const cacheTimestampRef = useRef(0);
  const lastParamsRef = useRef('');
  const cachedUserRef = useRef(null);
  const inFlightPromiseRef = useRef(null);

  // Invalidate cache when user switches or logs out
  useEffect(() => {
    if (cachedUserRef.current !== currentUserId) {
      cachedUserRef.current = currentUserId;
      setLiveJobsData(null);
      setCandidateProfile(null);
      setLastUpdatedAt('');
      setBuckets({ highly_relevant: [], relevant: [], potential: [], all_recommendations: [] });
      setFilters({ selectedRole: '', location: '', remote: '', experience: '', minMatch: '', activeTab: 'all' });
      setError('');
      setResumeRequired(false);
      cacheTimestampRef.current = 0;
      lastParamsRef.current = '';
    }
  }, [currentUserId]);

  const updateFilters = useCallback((newFilters) => {
    setFilters(prev => {
      const next = typeof newFilters === 'function' ? newFilters(prev) : newFilters;
      const merged = { ...prev, ...next };

      // If target role changed, immediately purge stale recommendations from state
      if (next.selectedRole !== undefined && next.selectedRole !== prev.selectedRole) {
        setLiveJobsData(null);
        setBuckets({ highly_relevant: [], relevant: [], potential: [], all_recommendations: [] });
        lastParamsRef.current = '';
        cacheTimestampRef.current = 0;
      }
      return merged;
    });
  }, []);

  const invalidateJobCache = useCallback(() => {
    cacheTimestampRef.current = 0;
    lastParamsRef.current = '';
    setLiveJobsData(null);
    setCandidateProfile(null);
    setBuckets({ highly_relevant: [], relevant: [], potential: [], all_recommendations: [] });
  }, []);

  const fetchLiveJobs = useCallback(async (customParams = null, forceRefresh = false) => {
    if (!isAuthenticated) return;

    const activeParams = customParams || {
      role: filters.selectedRole || undefined,
      location: filters.location || undefined,
      remote: filters.remote ? filters.remote === 'true' : undefined,
      experience: filters.experience || undefined,
      min_match: filters.minMatch || undefined
    };

    const serializedParams = JSON.stringify(activeParams);
    const now = Date.now();
    const isCacheValid = (
      liveJobsData &&
      !forceRefresh &&
      lastParamsRef.current === serializedParams &&
      (now - cacheTimestampRef.current < CACHE_TTL_MS)
    );

    // Instant cache hit: already loaded and valid
    if (isCacheValid) {
      return liveJobsData;
    }

    // Deduplicate in-flight requests
    if (inFlightPromiseRef.current && lastParamsRef.current === serializedParams && !forceRefresh) {
      return inFlightPromiseRef.current;
    }

    // If we already have data, show subtle refreshing indicator rather than blanking screen
    if (liveJobsData) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    setError('');
    setResumeRequired(false);

    const requestPromise = (async () => {
      try {
        const queryParams = { ...activeParams };
        if (forceRefresh) queryParams.refresh = 'true';

        const response = await jobAPI.getLiveJobRecommendations(queryParams);

        if (response.success) {
          const profile = response.candidate_profile || null;
          const updatedTime = response.last_updated_at || new Date().toLocaleTimeString();
          const data = response.data || {};
          const newBuckets = {
            highly_relevant: data.highly_relevant || [],
            relevant: data.relevant || [],
            potential: data.potential || [],
            all_recommendations: data.all_recommendations || []
          };

          setCandidateProfile(profile);
          setLastUpdatedAt(updatedTime);
          setBuckets(newBuckets);
          setLiveJobsData(response);
          cacheTimestampRef.current = Date.now();
          lastParamsRef.current = serializedParams;
          return response;
        } else {
          if (response.status === 'RESUME_REQUIRED') {
            setResumeRequired(true);
          } else {
            setError(response.message || 'Live job data is currently unavailable.');
          }
          return null;
        }
      } catch (err) {
        console.error('Failed to fetch recommendations:', err);
        if (err.response?.data?.status === 'RESUME_REQUIRED') {
          setResumeRequired(true);
        } else {
          setError(err.response?.data?.message || 'Live job data is currently unavailable. Please try again later.');
        }
        return null;
      } finally {
        setLoading(false);
        setRefreshing(false);
        inFlightPromiseRef.current = null;
      }
    })();

    inFlightPromiseRef.current = requestPromise;
    return requestPromise;
  }, [isAuthenticated, filters, liveJobsData]);

  const refreshLiveJobs = useCallback((force = true) => {
    return fetchLiveJobs(null, force);
  }, [fetchLiveJobs]);

  const toggleSaveJob = useCallback(async (jobId, action) => {
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
      console.error('Failed to save job action:', err);
    }
  }, []);

  return (
    <JobContext.Provider
      value={{
        liveJobsData,
        candidateProfile,
        lastUpdatedAt,
        buckets,
        filters,
        setFilters: updateFilters,
        loading,
        refreshing,
        error,
        resumeRequired,
        savedJobIds,
        fetchLiveJobs,
        refreshLiveJobs,
        invalidateJobCache,
        toggleSaveJob
      }}
    >
      {children}
    </JobContext.Provider>
  );
};

export const useJobContext = () => {
  const context = useContext(JobContext);
  if (!context) {
    throw new Error('useJobContext must be used within a JobProvider');
  }
  return context;
};
