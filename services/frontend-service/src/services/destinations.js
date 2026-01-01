import api from './api';

export async function createDestination(data) {
  const res = await api.post('/api/destinations/', data);
  return res.data;
}

export async function getDestinations(skip = 0, limit = 50) {
  const res = await api.get('/api/destinations/', { params: { skip, limit } });
  return res.data.destinations || res.data || [];
}

export async function getDestination(destinationId) {
  const res = await api.get(`/api/destinations/${destinationId}`);
  return res.data;
}

export async function updateDestination(destinationId, data) {
  const res = await api.put(`/api/destinations/${destinationId}`, data);
  return res.data;
}

export async function deleteDestination(destinationId) {
  await api.delete(`/api/destinations/${destinationId}`);
}

export async function uploadDestinationImage(destinationId, file) {
  console.log('[uploadDestinationImage] Received file:', file);
  console.log('[uploadDestinationImage] File type:', typeof file);
  console.log('[uploadDestinationImage] Is File?', file instanceof File);
  console.log('[uploadDestinationImage] Is Blob?', file instanceof Blob);
  const formData = new FormData();
  formData.append('file', file);
  console.log('[uploadDestinationImage] FormData after append:', Array.from(formData.entries()));
  const res = await api.post(`/api/destinations/${destinationId}/upload-image`, formData);
  return res.data;
}

export async function deleteDestinationImage(destinationId) {
  await api.delete(`/api/destinations/${destinationId}/image`);
}

export async function createAdvertisement(destinationId, data) {
  const res = await api.post(`/api/destinations/${destinationId}/advertisements`, data);
  return res.data;
}

async function getAdvertisements(destinationId, activeOnly = false) {
  const res = await api.get(`/api/destinations/${destinationId}/advertisements`, { params: { active_only: activeOnly } });
  return res.data.advertisements || res.data || [];
}

export async function updateAdvertisement(destinationId, resourceId, data) {
  const res = await api.put(`/api/destinations/${destinationId}/advertisements/${resourceId}`, data);
  return res.data;
}

export async function deleteAdvertisement(destinationId, resourceId) {
  await api.delete(`/api/destinations/${destinationId}/advertisements/${resourceId}`);
}

export async function createOffer(destinationId, data) {
  const res = await api.post(`/api/destinations/${destinationId}/offers`, data);
  return res.data;
}

async function getOffers(destinationId, activeOnly = false) {
  const res = await api.get(`/api/destinations/${destinationId}/offers`, { params: { active_only: activeOnly } });
  return res.data.offers || res.data || [];
}

export async function updateOffer(destinationId, resourceId, data) {
  const res = await api.put(`/api/destinations/${destinationId}/offers/${resourceId}`, data);
  return res.data;
}

export async function deleteOffer(destinationId, resourceId) {
  await api.delete(`/api/destinations/${destinationId}/offers/${resourceId}`);
}

export async function createDiscount(destinationId, data) {
  const res = await api.post(`/api/destinations/${destinationId}/discounts`, data);
  return res.data;
}

async function getDiscounts(destinationId, activeOnly = false) {
  const res = await api.get(`/api/destinations/${destinationId}/discounts`, { params: { active_only: activeOnly } });
  return res.data.discounts || res.data || [];
}

export async function updateDiscount(destinationId, resourceId, data) {
  const res = await api.put(`/api/destinations/${destinationId}/discounts/${resourceId}`, data);
  return res.data;
}

export async function deleteDiscount(destinationId, resourceId) {
  await api.delete(`/api/destinations/${destinationId}/discounts/${resourceId}`);
}
