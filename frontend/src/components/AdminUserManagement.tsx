import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchUsers, addUser, deleteUser, editUser } from '../services/api';

const AdminUserManagement: React.FC = () => {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const departments = [
    'HR', 'Finance', 'Engineering', 'Sales', 'Marketing', 'IT', 'Operations', 'Legal', 'Support', 'Admin'
  ];
  const [form, setForm] = useState({ email: '', name: '', department: departments[0], role: 'user' });
  const [generatedPassword, setGeneratedPassword] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editForm, setEditForm] = useState({ department: '', role: '' });

  const loadUsers = async () => {
    setLoading(true);
    try {
      const data = await fetchUsers();
      setUsers(data);
      setLoading(false);
    } catch (e: any) {
      setError(e.message);
      setLoading(false);
    }
  };

  useEffect(() => { loadUsers(); }, []);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    setGeneratedPassword(null);
    try {
      const res = await addUser(form);
      setGeneratedPassword(res.password);
      setForm({ email: '', name: '', department: '', role: 'user' });
      loadUsers();
    } catch (e: any) {
      setError(e.message);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Delete user?')) return;
    try {
      await deleteUser(id);
      loadUsers();
    } catch (e: any) {
      setError(e.message);
    }
  };

  const handleEdit = async (id: number) => {
    try {
      await editUser(id, editForm);
      setEditingId(null);
      setEditForm({ department: '', role: '' });
      loadUsers();
    } catch (e: any) {
      setError(e.message);
    }
  };

  const navigate = useNavigate();

  return (
    <div className="admin-user-management">
      <button onClick={() => navigate('/')} className="back-btn">← Back to Dashboard</button>
      <h2>👥 Admin User Management</h2>
      {error && <p className="error-msg">{error}</p>}
      <form className="user-form" onSubmit={handleAdd}>
        <input required placeholder="Email" value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))} />
        <input required placeholder="Name" value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} />
        <select required value={form.department} onChange={e => setForm(f => ({ ...f, department: e.target.value }))}>
          {departments.map(dep => <option key={dep} value={dep}>{dep}</option>)}
        </select>
        <select value={form.role} onChange={e => setForm(f => ({ ...f, role: e.target.value }))}>
          <option value="user">User</option>
          <option value="admin">Admin</option>
        </select>
        <button type="submit" className="add-btn">Add User</button>
      </form>
      {generatedPassword && (
        <div className="password-popup">
          <b>Generated Password:</b>
          <span className="password-value">{generatedPassword}</span>
          <button className="copy-btn" onClick={() => {
            navigator.clipboard.writeText(generatedPassword);
            setTimeout(() => setGeneratedPassword(null), 500);
          }}>Copy & Hide</button>
        </div>
      )}
      {loading ? <p>Loading users...</p> : (
        <table className="user-table">
          <thead>
            <tr>
              <th>Email</th><th>Name</th><th>Department</th><th>Role</th><th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map(u => (
              <tr key={u.id}>
                <td>{u.email}</td>
                <td>{u.name}</td>
                <td>{editingId === u.id ? (
                  <select value={editForm.department} onChange={e => setEditForm(f => ({ ...f, department: e.target.value }))}>
                    {departments.map(dep => <option key={dep} value={dep}>{dep}</option>)}
                  </select>
                ) : u.department}</td>
                <td>{editingId === u.id ? (
                  <select value={editForm.role} onChange={e => setEditForm(f => ({ ...f, role: e.target.value }))}>
                    <option value="user">User</option>
                    <option value="admin">Admin</option>
                  </select>
                ) : u.role}</td>
                <td>
                  {editingId === u.id ? (
                    <>
                      <button className="save-btn" onClick={() => handleEdit(u.id)}>Save</button>
                      <button className="cancel-btn" onClick={() => { setEditingId(null); setEditForm({ department: '', role: '' }); }}>Cancel</button>
                    </>
                  ) : (
                    <>
                      <button className="edit-btn" onClick={() => { setEditingId(u.id); setEditForm({ department: u.department, role: u.role }); }}>Edit</button>
                      <button className="delete-btn" onClick={() => handleDelete(u.id)}>Delete</button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default AdminUserManagement;
