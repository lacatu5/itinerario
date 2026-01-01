import api from './api';

export async function createUser(data) {
  const res = await api.post('/api/users/', data);
  return res.data;
}

async function listUsers(page = 1, size = 20) {
  const res = await api.get('/api/users/', { params: { page, size } });
  return res.data;
}

export async function getUser(userId) {
  try {
    const res = await api.get(`/api/users/${userId}/public`);
    return res.data;
  } catch (err) {
    console.error(`Error fetching public user ${userId}:`, err);
    throw err;
  }
}

export async function getUserByEmail(email) {
  const res = await api.get(`/api/users/email/${encodeURIComponent(email)}`);
  return res.data;
}

export async function searchUsers(query) {
  const res = await api.get('/api/users/search', { params: { query } });
  return res.data.users || res.data || [];
}

export async function updateUser(userId, updateData) {
  const res = await api.put(`/api/users/${userId}`, updateData);
  return res.data;
}

export async function uploadProfileImage(userId, file) {
  console.log('[uploadProfileImage] Starting upload for userId:', userId);
  console.log('[uploadProfileImage] File:', file);
  const formData = new FormData();
  formData.append('file', file);
  console.log('[uploadProfileImage] FormData created, entries:', Array.from(formData.entries()));
  console.log('[uploadProfileImage] Sending request to:', `/api/users/${userId}/upload-image`);
  const res = await api.post(`/api/users/${userId}/upload-image`, formData);
  console.log('[uploadProfileImage] Response received:', res);
  return res.data;
}

export async function deleteProfileImage(userId) {
  await api.delete(`/api/users/${userId}/image`);
}
