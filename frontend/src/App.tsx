import ForgotPasswordPage from './pages/ForgotPasswordPage';


import React, { useEffect, useMemo, useState } from 'react';
import './App.css';
import { BrowserRouter as Router, Route, Routes, useNavigate } from 'react-router-dom';
import { parseJwt } from './utils/jwt';

import LoginPage from './pages/LoginPage';
import Chat from './components/Chat';
import KnowledgeBase from './components/KnowledgeBase';
import DocumentUpload from './components/DocumentUpload';
import Profile from './components/Profile';
import AdminUserManagement from './components/AdminUserManagement';

const Home: React.FC = () => {
  const token = localStorage.getItem('jwt_token');
  const navigate = useNavigate();
  // Parse user info from JWT
  const user = useMemo(() => (token ? parseJwt(token) : null), [token]);
  const isAdmin = user && (user.role === 'admin' || (Array.isArray(user.roles) && user.roles.includes('admin')));

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!token || !user) {
      navigate('/login', { replace: true });
    }
  }, [token, user, navigate]);

  if (!token || !user) {
    return null; // Will redirect
  }

  return (
    <div className="dashboard-page">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-brand">
          <span className="brand-icon">🏢</span>
          <h1>Enterprise Assistant</h1>
        </div>
        <div className="header-user">
          <div className="user-info">
            <span className="user-name">{user.name || user.email || 'User'}</span>
            <span className="user-role">{user.role || (user.roles && user.roles.join(', ')) || 'Member'}</span>
          </div>
          <button className="profile-btn" onClick={() => navigate('/profile')} title="Profile">
            👤
          </button>
          <button className="logout-btn" onClick={() => { localStorage.removeItem('jwt_token'); navigate('/login'); }}>
            Logout
          </button>
        </div>
      </header>

      {/* Navigation */}
      <nav className="dashboard-nav">
        <button className="nav-btn active" onClick={() => navigate('/')}>
          <span>💬</span> Chat
        </button>
        <button className="nav-btn" onClick={() => navigate('/kb')}>
          <span>📚</span> Knowledge Base
        </button>
        {isAdmin && (
          <>
            <button className="nav-btn" onClick={() => navigate('/upload')}>
              <span>📤</span> Upload
            </button>
            <button className="nav-btn" onClick={() => navigate('/admin/users')}>
              <span>👥</span> Users
            </button>
          </>
        )}
      </nav>

      {/* Main Content */}
      <main className="dashboard-main">
        <Chat user={user} />
      </main>
    </div>
  );
};


function App() {
  const [tokenChecked, setTokenChecked] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');
    if (token) {
      localStorage.setItem('jwt_token', token);
      window.history.replaceState({}, document.title, '/'); // Clean URL
    }
    setTokenChecked(true);
  }, []);

  // Don't render routes until token check is complete
  if (!tokenChecked) {
    return null;
  }

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<Home />} />
        <Route path="/kb" element={<KnowledgeBase />} />
        <Route path="/upload" element={<DocumentUpload />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/admin/users" element={<AdminUserManagement />} />
      </Routes>
    </Router>
  );
}

export default App;
