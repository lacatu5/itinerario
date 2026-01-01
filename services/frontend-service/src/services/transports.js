import api from './api';

export async function getItineraryTransports(itineraryId, page = 1, size = 50) {
  const res = await api.get(`/api/itineraries/${itineraryId}/transports`, { params: { page, size } });
  return res.data.items || res.data || [];
}

export async function createTransport(itineraryId, data) {
  const res = await api.post(`/api/itineraries/${itineraryId}/transports`, data);
  return res.data;
}

export async function updateTransport(transportId, data) {
  const res = await api.put(`/api/itineraries/transports/${transportId}`, data);
  return res.data;
}

export async function deleteTransport(transportId) {
  await api.delete(`/api/itineraries/transports/${transportId}`);
}
