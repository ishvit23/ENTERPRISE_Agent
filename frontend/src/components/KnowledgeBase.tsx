
import React, { useEffect, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchDocuments, deleteDocument } from '../services/api';
import { parseJwt } from '../utils/jwt';

interface DocumentMeta {
  id: string;
  name: string;
  department: string;
  version: string;
}

const KnowledgeBase: React.FC = () => {
  const navigate = useNavigate();
  const [docs, setDocs] = useState<DocumentMeta[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selected, setSelected] = useState<string[]>([]);
  const [deleting, setDeleting] = useState(false);
  // Determine if user is admin
  const token = localStorage.getItem('jwt_token');
  const user = useMemo(() => (token ? parseJwt(token) : null), [token]);
  const isAdmin = user && (user.role === 'admin' || (Array.isArray(user.roles) && user.roles.includes('admin')));
  const handleSelect = (docId: string) => {
    setSelected((prev) => prev.includes(docId) ? prev.filter(id => id !== docId) : [...prev, docId]);
  };

  const handleSelectAll = () => {
    if (selected.length === docs.length) {
      setSelected([]);
    } else {
      setSelected(docs.map(d => d.id));
    }
  };

  const handleBulkDelete = async () => {
    if (selected.length === 0) return;
    if (!window.confirm(`Are you sure you want to delete ${selected.length} document(s)?`)) return;
    setDeleting(true);
    setError('');
    try {
      for (const docId of selected) {
        await deleteDocument(docId);
      }
      setDocs((prev) => prev.filter((d) => !selected.includes(d.id)));
      setSelected([]);
    } catch (err: any) {
      setError('Failed to delete selected documents.');
    } finally {
      setDeleting(false);
    }
  };

  useEffect(() => {
    setLoading(true);
    fetchDocuments()
      .then(data => {
        setDocs(data.documents || []);
        setLoading(false);
      })
      .catch(e => {
        setError(e.message);
        setLoading(false);
      });
  }, []);

  return (
    <div className="kb-container">
      <button onClick={() => navigate('/')} className="back-btn">← Back to Dashboard</button>
      <h2>📚 Knowledge Base</h2>
      {loading && <div className="loading"><div className="loading-spinner"></div>Loading documents...</div>}
      {error && <div className="error-msg">{error}</div>}
      {!loading && !error && docs.length === 0 && <div className="loading">No documents found.</div>}
      {!loading && !error && docs.length > 0 && (
        <>
          {isAdmin && (
            <div className="kb-actions">
              <button onClick={handleSelectAll} className="btn-secondary">
                {selected.length === docs.length ? 'Unselect All' : 'Select All'}
              </button>
              {selected.length > 0 && (
                <button
                  onClick={handleBulkDelete}
                  disabled={deleting}
                  className="delete-btn"
                >
                  {deleting ? 'Deleting...' : `Delete Selected (${selected.length})`}
                </button>
              )}
            </div>
          )}
          <table className="doc-table">
            <thead>
              <tr>
                {isAdmin && <th style={{ width: 40 }}></th>}
                <th>Name</th>
                <th>Department</th>
                <th>Version</th>
              </tr>
            </thead>
            <tbody>
              {docs.map(doc => (
                <tr key={doc.id}>
                  {isAdmin && (
                    <td style={{ textAlign: 'center' }}>
                      <input
                        type="checkbox"
                        checked={selected.includes(doc.id)}
                        onChange={() => handleSelect(doc.id)}
                        disabled={deleting}
                      />
                    </td>
                  )}
                  <td>{doc.name}</td>
                  <td>{doc.department}</td>
                  <td>{doc.version}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
};

export default KnowledgeBase;
