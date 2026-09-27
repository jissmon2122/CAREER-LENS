import React, { useState } from 'react';
import { useGoogleLogin } from '@react-oauth/google';

const GoogleAuthButton = ({ onSuccess, onError, disabled }) => {
  const [loading, setLoading] = useState(false);

  // Official Google OAuth Trigger via @react-oauth/google credential/code flow
  const handleGoogleSuccess = async (tokenResponse) => {
    setLoading(true);
    try {
      // Pass credential ID token or access token to parent handler
      const credential = tokenResponse.credential || tokenResponse.access_token;
      if (credential) {
        await onSuccess(credential);
      } else {
        onError && onError('Failed to retrieve credential from Google authentication.');
      }
    } catch (err) {
      onError && onError(err.message || 'Google authentication error');
    } finally {
      setLoading(false);
    }
  };

  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || "your_google_oauth_client_id.apps.googleusercontent.com";
  const isPlaceholder = !googleClientId || googleClientId.includes('your_google_oauth_client_id');

  const loginWithGoogle = useGoogleLogin({
    onSuccess: handleGoogleSuccess,
    onError: (err) => {
      console.error("Google Auth Error:", err);
      onError && onError('Google OAuth Error 401 (invalid_client): OAuth client not found. Please use Email & Password sign-in below or set a valid VITE_GOOGLE_CLIENT_ID in frontend/.env.');
    },
  });

  const handleClick = () => {
    if (isPlaceholder) {
      onError && onError('Google OAuth Client ID is set to placeholder in .env. Please sign in using Email & Password below, or set your real Google Client ID in frontend/.env.');
      return;
    }
    try {
      loginWithGoogle();
    } catch (err) {
      console.error("Google Auth trigger error:", err);
      onError && onError('Google OAuth Client ID error. Please use Email & Password sign-in below.');
    }
  };

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={disabled || loading}
      className="btn btn-secondary btn-block"
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '0.75rem',
        padding: '0.8rem 1.25rem',
        fontSize: '0.95rem',
        fontWeight: '600',
        background: '#ffffff',
        color: '#1f2937',
        border: '1px solid #e5e7eb',
        borderRadius: 'var(--radius-md)',
        boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
        cursor: 'pointer',
        transition: 'all 0.2s ease',
        marginBottom: '1.25rem',
      }}
    >
      {loading ? (
        <div className="spinner" style={{ width: '20px', height: '20px', borderWidth: '2px', borderColor: 'rgba(0,0,0,0.2)', borderTopColor: '#4285F4' }}></div>
      ) : (
        <svg width="20" height="20" viewBox="0 0 24 24">
          <path
            fill="#4285F4"
            d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
          />
          <path
            fill="#34A853"
            d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
          />
          <path
            fill="#FBBC05"
            d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
          />
          <path
            fill="#EA4335"
            d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
          />
        </svg>
      )}
      <span>{loading ? 'Connecting to Google...' : 'Continue with Google'}</span>
    </button>
  );
};

export default GoogleAuthButton;
