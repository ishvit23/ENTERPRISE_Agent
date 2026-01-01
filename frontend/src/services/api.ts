// Admin user management
export async function fetchUsers() {
  const res = await fetch(`${API_BASE}/admin/users/list`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error('Failed to fetch users');
  return res.json();
}

export async function addUser({ email, name, department, role }: { email: string; name: string; department: string; role: string; }) {
  const res = await fetch(`${API_BASE}/admin/users/add`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, name, department, role }),
  });
  if (!res.ok) throw new Error('Failed to add user');
  return res.json();
}

export async function deleteUser(userId: number) {
  const res = await fetch(`${API_BASE}/admin/users/delete/${userId}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error('Failed to delete user');
  return res.json();
}

export async function editUser(userId: number, { department, role }: { department?: string; role?: string; }) {
  const res = await fetch(`${API_BASE}/admin/users/edit/${userId}`, {
    method: 'PUT',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ department, role }),
  });
  if (!res.ok) throw new Error('Failed to edit user');
  return res.json();
}
export async function deleteDocument(docId: string) {
  const res = await fetch(`${API_BASE}/documents/delete/${docId}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error('Failed to delete document');
  return res.json();
}
// src/services/api.ts

const API_BASE = 'http://localhost:8000';

function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem('jwt_token');
  if (token) {
    return { Authorization: `Bearer ${token}` };
  }
  return {};
}

export async function fetchDocuments() {
  const res = await fetch(`${API_BASE}/documents/list`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error('Failed to fetch documents');
  return res.json();
}

export async function uploadDocument({ file, department, name, version, category }: { file: File; department: string; name: string; version: string; category: 'common' | 'department'; }) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('department', department);
  formData.append('name', name);
  formData.append('version', version);
  formData.append('category', category);
  const res = await fetch(`${API_BASE}/documents/ingest`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: formData,
  });
  if (!res.ok) throw new Error('Upload failed');
  return res.json();
}

export async function fetchProfile() {
  const res = await fetch(`${API_BASE}/profile`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error('Failed to fetch profile');
  return res.json();
}

export async function askQuestion({ question, department, top_k }: { question: string; department: string; top_k?: number; }) {
  const res = await fetch(`${API_BASE}/qa/ask`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question, department, top_k }),
  });
  if (!res.ok) throw new Error('Failed to get answer');
  return res.json();
}
