import axios from 'axios';

const getBaseURL = () => {
  const envUrl = import.meta.env.VITE_API_BASE_URL;
  if (!envUrl) return '/api';
  const trimmed = envUrl.trim().replace(/\/+$/, '');
  return trimmed.endsWith('/api') ? trimmed : `${trimmed}/api`;
};

const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Attach JWT Bearer Token & Request Correlation ID
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    // Attach client trace ID if not already present
    if (!config.headers['X-Request-ID']) {
      config.headers['X-Request-ID'] = `cl_${Math.random().toString(36).substring(2, 10)}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Global Error Handling & Safe Bounded Retries for GET Requests
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config;

    // Helper: Determine if error is a transient failure
    const status = error.response?.status;
    const isTimeout = error.code === 'ECONNABORTED' || (error.message && error.message.includes('timeout'));
    const isNetworkError = !error.response && Boolean(error.request);
    const isTransientStatus = status === 502 || status === 503 || status === 504 || status === 429;
    const isTransient = isTimeout || isNetworkError || isTransientStatus;

    // Only retry safe, idempotent GET requests to prevent duplicate side-effects
    const isGetRequest = config && config.method && config.method.toLowerCase() === 'get';
    const maxRetries = 2; // Bounded: maximum 2 retries (3 total attempts)

    if (config && isGetRequest && isTransient) {
      config._retryCount = config._retryCount || 0;

      if (config._retryCount < maxRetries) {
        config._retryCount += 1;

        // Exponential backoff with jitter: 1s, 2s + 0-500ms jitter
        let backoffDelay = Math.min(1000 * Math.pow(2, config._retryCount - 1) + Math.floor(Math.random() * 500), 5000);

        // Respect standard Retry-After header on 429 Rate Limiting
        if (status === 429) {
          const retryAfterHeader = error.response?.headers?.['retry-after'];
          if (retryAfterHeader) {
            const parsed = parseInt(retryAfterHeader, 10);
            if (!isNaN(parsed) && parsed > 0) {
              backoffDelay = Math.min(parsed * 1000, 6000);
            }
          }
        }

        await new Promise((resolve) => setTimeout(resolve, backoffDelay));
        return api(config);
      }
    }

    // Standardize error message payloads for clean UI rendering
    if (isTimeout) {
      if (!error.response) {
        const reqUrl = config?.url || '';
        let timeoutMsg = 'Request timed out. The server is taking longer than expected to respond. Please try again.';
        if (reqUrl.includes('/jobs/')) {
          timeoutMsg = 'Request timed out. Live search is taking longer than expected. Please retry or adjust filters.';
        } else if (reqUrl.includes('/auth/')) {
          timeoutMsg = 'Authentication request timed out. Please check your connection and retry.';
        }
        error.response = {
          status: 408,
          data: {
            success: false,
            message: timeoutMsg,
            error: 'TIMEOUT'
          }
        };
      }
    } else if (status === 429 && (!error.response.data || !error.response.data.message)) {
      error.response.data = {
        success: false,
        message: 'Too many requests. Please wait a moment before trying again.',
        error: 'RATE_LIMITED'
      };
    } else if (status === 503 && (!error.response.data || !error.response.data.message)) {
      error.response.data = {
        success: false,
        message: 'The service is temporarily unavailable. Please try again shortly.',
        error: 'SERVICE_UNAVAILABLE'
      };
    }

    // Token invalidation: Only on genuine HTTP 401 on protected (non-auth) routes
    if (error.response && error.response.status === 401) {
      const isAuthRoute = config?.url?.includes('/auth/login') || 
                          config?.url?.includes('/auth/register') || 
                          config?.url?.includes('/auth/google');
      if (!isAuthRoute) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    }

    return Promise.reject(error);
  }
);

export const authAPI = {
  register: async (payload) => {
    const response = await api.post('/auth/register', payload);
    return response.data;
  },
  login: async (payload) => {
    const response = await api.post('/auth/login', payload);
    return response.data;
  },
  googleLogin: async (credential) => {
    const response = await api.post('/auth/google', { credential });
    return response.data;
  },
  getMe: async (options = {}) => {
    const response = await api.get('/auth/me', { timeout: 35000, ...options });
    return response.data;
  },
};

export const resumeAPI = {
  uploadResume: async (formData) => {
    const response = await api.post('/resume/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  getMyResumes: async () => {
    const response = await api.get('/resume/my-resumes');
    return response.data;
  },
  getResumeById: async (resumeId) => {
    const response = await api.get(`/resume/${resumeId}`);
    return response.data;
  },
  analyzeResume: async (resumeId) => {
    const response = await api.post(`/resume/analyze/${resumeId}`);
    return response.data;
  },
  getResumeAnalysis: async (resumeId) => {
    const response = await api.get(`/resume/analysis/${resumeId}`);
    return response.data;
  },
};

export const userAPI = {
  getProfile: async () => {
    const response = await api.get('/user/profile');
    return response.data;
  },
  updateProfile: async (profileData) => {
    const response = await api.put('/user/profile', profileData);
    return response.data;
  },
};

export const jobAPI = {
  getRecommendedJobs: async (params, options = {}) => {
    const response = await api.get('/jobs/recommended', { params, ...options });
    return response.data;
  },
  getLiveJobRecommendations: async (params, options = {}) => {
    const response = await api.get('/jobs/recommended', { params, ...options });
    return response.data;
  },
  getJobMatch: async (jobId) => {
    const response = await api.get(`/jobs/${jobId}/match`);
    return response.data;
  },
  getAllJobs: async () => {
    const response = await api.get('/jobs/all');
    return response.data;
  },
  searchLiveJobs: async (params) => {
    const response = await api.get('/jobs/search', { params });
    return response.data;
  },
  saveJobAction: async (jobId, action, notes = '') => {
    const response = await api.post('/jobs/action', { job_id: jobId, action, notes });
    return response.data;
  },
  getSavedJobs: async () => {
    const response = await api.get('/jobs/saved');
    return response.data;
  },
};

export const skillGapAPI = {
  getSkillGap: async (jobId) => {
    const response = await api.get(`/skills/gap/${jobId}`);
    return response.data;
  },
  getRoadmap: async (jobId) => {
    const response = await api.get(`/skills/roadmap/${jobId}`);
    return response.data;
  },
  acquireSkill: async (skillName) => {
    const response = await api.post('/skills/acquire', { skill_name: skillName });
    return response.data;
  },
};

export const forecastingAPI = {
  getTopSkills: async () => {
    const response = await api.get('/forecasting/top-skills');
    return response.data;
  },
  getSkillForecast: async (skillName) => {
    const response = await api.get(`/forecasting/skill/${encodeURIComponent(skillName)}`);
    return response.data;
  },
  getRecommendations: async () => {
    const response = await api.get('/forecasting/recommendations');
    return response.data;
  },
};

export const aiAPI = {
  getAIStatus: async () => {
    const response = await api.get('/ai/status');
    return response.data;
  },
  computeSemanticMatch: async (payload) => {
    const response = await api.post('/ai/semantic-match', payload);
    return response.data;
  },
};

export default api;
