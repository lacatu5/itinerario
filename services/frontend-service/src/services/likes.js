import api from './api';

export async function likeItinerary(itineraryId, comment) {
  const data = comment ? { comment } : {};
  const res = await api.post(`/api/social/itineraries/${itineraryId}/like`, data);
  return res.data;
}

export async function unlikeItinerary(itineraryId) {
  await api.delete(`/api/social/itineraries/${itineraryId}/like`);
}

export async function updateLikeComment(itineraryId, comment) {
  const res = await api.put(`/api/social/itineraries/${itineraryId}/like`, { comment });
  return res.data;
}

export async function getItineraryLikes(itineraryId) {
  const res = await api.get(`/api/social/itineraries/${itineraryId}/likes`);
  return res.data.items || [];
}

export async function getItineraryStats(itineraryId) {
  const res = await api.get(`/api/social/itineraries/${itineraryId}/stats`);
  return res.data;
}

export async function checkLikeStatus(itineraryId) {
  const res = await api.get(`/api/social/itineraries/${itineraryId}/like-status`);
  return res.data;
}
