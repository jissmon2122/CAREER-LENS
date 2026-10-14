import axios from 'axios';

const getBaseURL = () => {
  const envUrl = import.meta.env.VITE_API_BASE_URL;
  if (!envUrl) return '/api';
  const trimmed = envUrl.trim().replace(/\/+$/, '');
  return trimmed.endsWith('/api') ? trimmed : `${trimmed}/api`;
};

const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 20000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Attach JWT Bearer Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Global Error Extraction
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNABORTED' || (error.message && error.message.includes('timeout'))) {
      if (!error.response) {
        const reqUrl = error.config?.url || '';
        let timeoutMsg = 'Request timed out. The server is taking longer than expected to respond. Please try again.';
        if (reqUrl.includes('/jobs/')) {
          timeoutMsg = 'Request timed out. Live search is taking longer than expected. Please retry or adjust filters.';
        } else if (reqUrl.includes('/auth/')) {
          timeoutMsg = 'Authentication request timed out. Please check your connection and try again.';
        }
        error.response = {
          data: {
            success: false,
            message: timeoutMsg
          }
        };
      }
    }
    if (error.response && error.response.status === 401) {
      const isAuthRoute = error.config?.url?.includes('/auth/login') || 
                          error.config?.url?.includes('/auth/register') || 
                          error.config?.url?.includes('/auth/google');
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
  getMe: async () => {
    const response = await api.get('/auth/me');
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
