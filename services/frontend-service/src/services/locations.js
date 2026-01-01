import api from './api';

export async function createLocation(itineraryId, data) {
  const res = await api.post(`/api/itineraries/${itineraryId}/locations`, data);
  return res.data;
}

export async function getItineraryLocations(itineraryId, page = 1, size = 50) {
  const res = await api.get(`/api/itineraries/${itineraryId}/locations`, { params: { page, size } });
  return res.data.items || res.data || [];
}

export async function updateLocation(locationId, data) {
  const res = await api.put(`/api/itineraries/locations/${locationId}`, data);
  return res.data;
}

export async function deleteLocation(locationId) {
  await api.delete(`/api/itineraries/locations/${locationId}`);
}

export async function uploadLocationImage(locationId, file) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await api.post(`/api/itineraries/locations/${locationId}/upload-image`, formData);
  return res.data;
}

export async function deleteLocationImage(locationId) {
  await api.delete(`/api/itineraries/locations/${locationId}/image`);
}
