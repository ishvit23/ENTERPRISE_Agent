import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadDocument } from '../services/api';

const DocumentUpload: React.FC = () => {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const DEPARTMENTS = ['HR', 'Finance', 'Engineering', 'Sales', 'Marketing', 'IT', 'Operations', 'Legal', 'Support', 'Admin'];
  const CATEGORIES = ['common', 'department'] as const;
  const [category, setCategory] = useState<'common' | 'department'>('department');
  const [department, setDepartment] = useState(DEPARTMENTS[0]);
  const [name, setName] = useState('');
  const [version, setVersion] = useState('1.0');
  const [status, setStatus] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !name || !version) {
      setStatus('All fields are required.');
      return;
    }
    if (category === 'department' && !department) {
      setStatus('Please select a department.');
      return;
    }
    setStatus('Uploading...');
    try {
      await uploadDocument({ 
        file, 
        department: category === 'common' ? 'common' : department, 
        name, 
        version,
        category 
      });
      setStatus('Upload successful!');
    } catch (e) {
      setStatus('Upload failed.');
    }
  };

  return (
    <div className="upload-container">
      <button onClick={() => navigate('/')} className="back-btn">← Back to Dashboard</button>
      <h2>📄 Upload Document</h2>
      <form onSubmit={handleSubmit} className="upload-form">
        <div className="form-group">
          <label>File</label>
          <input type="file" onChange={e => setFile(e.target.files?.[0] || null)} />
        </div>
        <div className="form-group">
          <label>Document Name</label>
          <input type="text" value={name} onChange={e => setName(e.target.value)} placeholder="Enter document name" />
        </div>
        <div className="form-group">
          <label>Document Category</label>
          <select value={category} onChange={e => setCategory(e.target.value as 'common' | 'department')}>
            <option value="common">🌐 Common (All Departments)</option>
            <option value="department">🏢 Department Specific</option>
          </select>
        </div>
        {category === 'department' && (
          <div className="form-group">
            <label>Department</label>
            <select value={department} onChange={e => setDepartment(e.target.value)}>
              {DEPARTMENTS.map(dep => (
                <option key={dep} value={dep}>{dep}</option>
              ))}
            </select>
          </div>
        )}
        <div className="form-group">
          <label>Version</label>
          <input type="text" value={version} onChange={e => setVersion(e.target.value)} placeholder="e.g. 1.0" />
        </div>
        <button type="submit">Upload Document</button>
      </form>
      {status && (
        <div className={`upload-status ${status.includes('success') ? 'success' : 'error'}`}>
          {status}
        </div>
      )}
    </div>
  );
};

export default DocumentUpload;
