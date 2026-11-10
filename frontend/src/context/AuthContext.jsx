import React, { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

// Synchronously parse and check JWT expiration without blocking UI
export const isTokenExpired = (jwtToken) => {
  if (!jwtToken || typeof jwtToken !== 'string') return true;
  try {
    const parts = jwtToken.split('.');
    if (parts.length !== 3) return true;
    const base64Url = parts[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    const payload = JSON.parse(jsonPayload);
    if (!payload.exp) return false;
    // Expired if current time + 15s buffer is past exp timestamp
    return payload.exp * 1000 <= (Date.now() + 15000);
  } catch {
    return true;
  }
};

// 3-minute throttle for background revalidation
const REVALIDATION_THROTTLE_MS = 180000;

export const AuthProvider = ({ children }) => {
  // Synchronous initialization from localStorage with instant JWT validation
  const [token, setToken] = useState(() => {
    try {
      const storedToken = localStorage.getItem('token');
      if (storedToken && !isTokenExpired(storedToken)) {
        return storedToken;
      }
      // Token missing or expired: clean up immediately
      if (storedToken) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
      return null;
    } catch {
      return null;
    }
  });

  const [user, setUser] = useState(() => {
    try {
      const storedToken = localStorage.getItem('token');
      if (!storedToken || isTokenExpired(storedToken)) {
        return null;
      }
      const savedUser = localStorage.getItem('user');
      return savedUser ? JSON.parse(savedUser) : null;
    } catch {
      return null;
    }
  });

  // Loading is only true if we have a valid token but NO cached user profile yet
  const [loading, setLoading] = useState(() => {
    const storedToken = localStorage.getItem('token');
    const hasValidToken = Boolean(storedToken && !isTokenExpired(storedToken));
    const hasCachedUser = Boolean(localStorage.getItem('user'));
    return hasValidToken && !hasCachedUser;
  });

  const [authError, setAuthError] = useState(null);
  const [isOffline, setIsOffline] = useState(false);
  const [isRevalidating, setIsRevalidating] = useState(false);

  // In-flight promise ref to deduplicate concurrent verifyAuth calls
  const inFlightAuthRef = useRef(null);
  // Timestamp ref to throttle redundant verification requests within 3 minutes
  const lastVerifiedAtRef = useRef(0);

  const verifyAuth = useCallback(async (currentToken, force = false) => {
    if (!currentToken || isTokenExpired(currentToken)) {
      if (currentToken) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setToken(null);
        setUser(null);
      }
      setLoading(false);
      return null;
    }

    // Skip redundant network requests if verified recently within this session
    const now = Date.now();
    if (!force && (now - lastVerifiedAtRef.current < REVALIDATION_THROTTLE_MS) && user) {
      setLoading(false);
      return user;
    }

    // Reuse existing in-flight verification if already executing
    if (inFlightAuthRef.current) {
      return inFlightAuthRef.current;
    }

    inFlightAuthRef.current = (async () => {
      // Only set loading if there is NO cached user displayed
      if (!user) {
        setLoading(true);
      }
      setIsRevalidating(true);

      try {
        const res = await authAPI.getMe();
        if (res.success && res.data?.user) {
          setUser(res.data.user);
          localStorage.setItem('user', JSON.stringify(res.data.user));
          setAuthError(null);
          setIsOffline(false);
          lastVerifiedAtRef.current = Date.now();
          return res.data.user;
        }
        return null;
      } catch (err) {
        const status = err.response?.status;
        if (status === 401) {
          // Token is genuinely invalid or revoked
          console.warn("Authentication token invalid or revoked. Clearing session.");
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          setToken(null);
          setUser(null);
          setAuthError("Your session has expired. Please log in again.");
          setIsOffline(false);
        } else {
          // Cold-start timeout, network partition, or 5xx: preserve cached session safely
          const msg = err.response?.data?.message || err.message || "Connection to authentication service unavailable.";
          console.warn("Auth check encountered network/temporary issue; retaining offline session:", msg);
          setAuthError(msg);
          setIsOffline(true);
        }
        return null;
      } finally {
        setLoading(false);
        setIsRevalidating(false);
        inFlightAuthRef.current = null;
      }
    })();

    return inFlightAuthRef.current;
  }, [user]);

  // Initial mount verification: runs silently in background if user already cached
  useEffect(() => {
    if (token) {
      verifyAuth(token);
    } else {
      setLoading(false);
    }
  }, [token, verifyAuth]);

  const login = (newToken, userData) => {
    inFlightAuthRef.current = null;
    lastVerifiedAtRef.current = Date.now();
    localStorage.setItem('token', newToken);
    localStorage.setItem('user', JSON.stringify(userData));
    setToken(newToken);
    setUser(userData);
    setLoading(false);
    setAuthError(null);
    setIsOffline(false);
  };

  const logout = () => {
    inFlightAuthRef.current = null;
    lastVerifiedAtRef.current = 0;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
    setLoading(false);
    setAuthError(null);
    setIsOffline(false);
  };

  const retryAuth = () => {
    return verifyAuth(token, true);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token && !!user,
        loading,
        isRevalidating,
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
