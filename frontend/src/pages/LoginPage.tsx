import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_BASE } from '../services/api';

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const navigate = useNavigate();
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // If already logged in, redirect to home
  useEffect(() => {
    const existingToken = localStorage.getItem('jwt_token');
    if (existingToken) {
      navigate('/', { replace: true });
      return;
    }

    // Handle Google OAuth callback
    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');
    const errorParam = params.get('error');
    if (token) {
      localStorage.setItem('jwt_token', token);
      window.history.replaceState({}, document.title, '/login');
      navigate('/', { replace: true });
    } else if (errorParam === 'not_registered') {
      setError('You are not registered with the enterprise. Please contact the admin.');
    }
  }, [navigate]);

  const handleGoogleLogin = () => {
    window.location.href = `${API_BASE}/auth/google/login`;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      if (!res.ok) {
        const data = await res.json();
        setError(data.detail || 'Login failed.');
        setLoading(false);
        return;
      }
      const data = await res.json();
      localStorage.setItem('jwt_token', data.access_token);
      navigate('/', { replace: true });
    } catch (err) {
      setError('Login failed.');
      setLoading(false);
    }
  };

  return (
    <div className="landing-page">
      {/* Animated background */}
      <div className="landing-bg">
        <div className="landing-blob blob-1"></div>
        <div className="landing-blob blob-2"></div>
        <div className="landing-blob blob-3"></div>
      </div>

      {/* Hero Section */}
      <div className="landing-hero">
        <div className="hero-content">
          <div className="hero-badge">Enterprise Solution</div>
          <h1 className="hero-title">
            Your Intelligent<br />
            <span className="gradient-text">Knowledge Assistant</span>
          </h1>
          <p className="hero-subtitle">
            AI-powered enterprise knowledge management. Get instant answers,
            manage documents, and streamline your workflow.
          </p>
          <div className="hero-features">
            <div className="feature-item">
              <span className="feature-icon">🤖</span>
              <span>AI-Powered Q&A</span>
            </div>
            <div className="feature-item">
              <span className="feature-icon">📄</span>
              <span>Document Management</span>
            </div>
            <div className="feature-item">
              <span className="feature-icon">🔒</span>
              <span>Role-Based Access</span>
            </div>
          </div>
        </div>

        {/* Glass Login Card */}
        <div className="glass-card">
          <div className="glass-card-header">
            <div className="glass-icon">🏢</div>
            <h2>Welcome Back</h2>
            <p>Sign in to your enterprise workspace</p>
          </div>

          <form onSubmit={handleSubmit} className="glass-form">
            <div className="glass-input-group">
              <span className="input-icon">📧</span>
              <input
                type="email"
                placeholder="Email address"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="glass-input-group">
              <span className="input-icon">🔑</span>
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
              />
            </div>
            <button type="submit" className="glass-btn-primary" disabled={loading}>
              {loading ? (
                <><span className="btn-spinner"></span>Signing in...</>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          <div className="glass-divider">
            <span>or continue with</span>
          </div>

          <button onClick={handleGoogleLogin} className="glass-btn-google">
            <svg viewBox="0 0 24 24" width="20" height="20">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Google
          </button>

          <div className="glass-footer">
            <button type="button" className="link-btn" onClick={() => navigate('/forgot-password')}>
              Forgot your password?
            </button>
          </div>

          {error && <div className="glass-error">{error}</div>}
        </div>
      </div>

      {/* Bottom Decoration */}
      <div className="landing-footer">
        <p>© 2026 Enterprise Knowledge Assistant. Powered by AI.</p>
      </div>
    </div>
  );
};

export default LoginPage;
