import React, { useState } from 'react';

const ForgotPasswordPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [step, setStep] = useState<'request' | 'reset'>('request');
  const [resetToken, setResetToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setMessage('');
    try {
      const res = await fetch('http://localhost:8000/auth/request-password-reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });
      if (!res.ok) {
        const data = await res.json();
        setError(data.detail || 'Request failed.');
        return;
      }
      const data = await res.json();
      setResetToken(data.reset_token);
      setStep('reset');
      setMessage('A reset token has been generated (demo: shown below).');
    } catch {
      setError('Request failed.');
    }
  };

  const handleReset = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setMessage('');
    try {
      const res = await fetch('http://localhost:8000/auth/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, token: resetToken, new_password: newPassword }),
      });
      if (!res.ok) {
        const data = await res.json();
        setError(data.detail || 'Reset failed.');
        return;
      }
      setMessage('Password reset successful! You can now log in.');
      setStep('request');
      setEmail('');
      setResetToken('');
      setNewPassword('');
    } catch {
      setError('Reset failed.');
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

      <div className="landing-hero" style={{ justifyContent: 'center' }}>
        <div className="glass-card">
          <div className="glass-card-header">
            <div className="glass-icon">🔐</div>
            <h2>Reset Password</h2>
            <p>{step === 'request' ? 'Enter your email to receive a reset token' : 'Enter your new password'}</p>
          </div>

          {step === 'request' ? (
            <form onSubmit={handleRequest} className="glass-form">
              <div className="glass-input-group">
                <span className="input-icon">📧</span>
                <input
                  type="email"
                  placeholder="you@company.com"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  required
                />
              </div>
              <button type="submit" className="glass-btn-primary">
                Request Reset Token
              </button>
            </form>
          ) : (
            <form onSubmit={handleReset} className="glass-form">
              <div className="glass-input-group">
                <span className="input-icon">🎫</span>
                <input
                  type="text"
                  placeholder="Enter token from email"
                  value={resetToken}
                  onChange={e => setResetToken(e.target.value)}
                  required
                />
              </div>
              <div className="glass-input-group">
                <span className="input-icon">🔑</span>
                <input
                  type="password"
                  placeholder="Enter new password"
                  value={newPassword}
                  onChange={e => setNewPassword(e.target.value)}
                  required
                />
              </div>
              <button type="submit" className="glass-btn-primary">
                Reset Password
              </button>
            </form>
          )}

          {message && <div className="glass-success">{message}</div>}
          {error && <div className="glass-error">{error}</div>}

          <div className="glass-footer">
            <a href="/login">← Back to Login</a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ForgotPasswordPage;
