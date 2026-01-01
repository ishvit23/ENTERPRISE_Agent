import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchProfile } from '../services/api';

const Profile: React.FC = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    setLoading(true);
    fetchProfile()
      .then(data => {
        setProfile(data);
        setLoading(false);
      })
      .catch(e => {
        setError(e.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="loading"><div className="loading-spinner"></div>Loading profile...</div>;
  if (error) return <div className="error-msg">{error}</div>;
  if (!profile) return <div className="loading">No profile data.</div>;

  const initials = (profile.name || profile.email || 'U').charAt(0).toUpperCase();

  return (
    <div className="profile-container">
      <button onClick={() => navigate('/')} className="back-btn">← Back to Dashboard</button>
      <div className="profile-avatar">{initials}</div>
      <h2>👤 User Profile</h2>
      <table className="profile-table">
        <tbody>
          <tr><td>Email</td><td>{profile.email}</td></tr>
          <tr><td>Name</td><td>{profile.name}</td></tr>
          <tr><td>Department</td><td>{profile.department}</td></tr>
          <tr><td>Role</td><td>{profile.role}</td></tr>
        </tbody>
      </table>
    </div>
  );
};

export default Profile;
