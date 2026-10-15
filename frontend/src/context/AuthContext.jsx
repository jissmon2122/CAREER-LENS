import React, { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    try {
      const savedUser = localStorage.getItem('user');
      return savedUser ? JSON.parse(savedUser) : null;
    } catch {
      return null;
    }
  });
  const [token, setToken] = useState(() => localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);
  const [authError, setAuthError] = useState(null);
  const [isOffline, setIsOffline] = useState(false);

  // Singleton ref to deduplicate simultaneous authentication requests
  const inFlightAuthRef = useRef(null);

  const verifyAuth = useCallback(async (currentToken) => {
    if (!currentToken) {
      setLoading(false);
      return null;
    }

    // Reuse existing in-flight promise if an auth verification is already running
    if (inFlightAuthRef.current) {
      return inFlightAuthRef.current;
    }

    inFlightAuthRef.current = (async () => {
      try {
        setLoading(true);
        const res = await authAPI.getMe();
        if (res.success && res.data?.user) {
          setUser(res.data.user);
          localStorage.setItem('user', JSON.stringify(res.data.user));
          setAuthError(null);
          setIsOffline(false);
          return res.data.user;
        }
        return null;
      } catch (err) {
        const status = err.response?.status;
        if (status === 401) {
          // Token is genuinely invalid or expired
          console.warn("Authentication token invalid or expired. Logging out.");
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          setToken(null);
          setUser(null);
          setAuthError("Your session has expired. Please log in again.");
          setIsOffline(false);
        } else {
          // Cold-start timeout, network partition, or 5xx: preserve cached user session
          const msg = err.response?.data?.message || err.message || "Connection to authentication service unavailable.";
          console.warn("Auth check encountered network/temporary issue; retaining offline session:", msg);
          setAuthError(msg);
          setIsOffline(true);
        }
        return null;
      } finally {
        setLoading(false);
        inFlightAuthRef.current = null;
      }
    })();

    return inFlightAuthRef.current;
  }, []);

  useEffect(() => {
    verifyAuth(token);
  }, [token, verifyAuth]);

  const login = (newToken, userData) => {
    inFlightAuthRef.current = null;
    localStorage.setItem('token', newToken);
    localStorage.setItem('user', JSON.stringify(userData));
    setToken(newToken);
    setUser(userData);
    setAuthError(null);
    setIsOffline(false);
  };

  const logout = () => {
    inFlightAuthRef.current = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
    setAuthError(null);
    setIsOffline(false);
  };

  const retryAuth = () => {
    return verifyAuth(token);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token && !!user,
        loading,
        authError,
        isOffline,
        login,
        logout,
        retryAuth,
        setUser
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
