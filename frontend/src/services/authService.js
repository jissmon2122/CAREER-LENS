import api, { authAPI, userAPI } from './api';

export const authService = {
  /**
   * Perform local user registration.
   */
  register: async (registerData) => {
    return await authAPI.register(registerData);
  },

  /**
   * Perform local user login.
   */
  login: async (credentials) => {
    return await authAPI.login(credentials);
  },

  /**
   * Authenticate via Google OAuth credential token.
   * Sends Google JWT credential to Flask backend POST /api/auth/google
   */
  googleLogin: async (credentialToken) => {
    const response = await api.post('/auth/google', {
      credential: credentialToken,
    });
    return response.data;
  },

  /**
   * Fetch current authenticated user.
   */
  getCurrentUser: async () => {
    return await authAPI.getMe();
  },

  /**
   * Update user profile information.
   */
  updateProfile: async (profileData) => {
    const response = await api.put('/user/profile', profileData);
    return response.data;
  },
};

export default authService;
