import api from './api';

export async function createItinerary(data) {
  const res = await api.post('/api/itineraries/', data);
  return res.data;
}

export async function getUserItineraries(userId, page = 1, size = 20) {
  const res = await api.get(`/api/itineraries/user/${userId}`, { params: { page, size } });
  return res.data;
}

export async function getItinerary(itineraryId) {
  const res = await api.get(`/api/itineraries/${itineraryId}`);
  return res.data;
}

export async function updateItinerary(itineraryId, data) {
  const res = await api.put(`/api/itineraries/${itineraryId}`, data);
  return res.data;
}

export async function searchItineraries({ destination, startDate, endDate, searchText, page = 1, size = 20 } = {}) {
  const data = {};
  if (destination) data.destination = destination;
  if (startDate) data.start_date = startDate;
  if (endDate) data.end_date = endDate;
  if (searchText) data.search_text = searchText;
  data.page = page;
  data.size = size;
  const res = await api.post('/api/itineraries/search', data);
  return res.data;
}

export async function getFeed() {
  const res = await api.get('/api/itineraries/');
  return res.data;
}
