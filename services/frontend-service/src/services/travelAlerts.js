import api from './api';

export async function getWeather({ latitude, longitude, location }) {
  const params = {};
  if (location) {
    params.location = location;
  } else if (latitude !== undefined && longitude !== undefined) {
    params.latitude = latitude;
    params.longitude = longitude;
  }
  const res = await api.get('/api/travel-alerts/weather', { params });
  return res.data;
}

export async function getTravelWarnings(countryCode = null, skip = 0, limit = 50) {
  const params = { skip, limit };
  if (countryCode) {
    params.country_code = countryCode;
  }
  const res = await api.get('/api/travel-alerts/warnings', { params });
  return res.data;
}

export async function getMyFlightTrackings() {
  const res = await api.get('/api/travel-alerts/flights');
  return res.data;
}

export async function createFlightTracking(data) {
  const res = await api.post('/api/travel-alerts/flights', data);
  return res.data;
}

export async function deleteFlightTracking(trackingId) {
  await api.delete(`/api/travel-alerts/flights/${trackingId}`);
}


export async function lookupFlightInfo(flightNumber) {
  const res = await api.get(`/api/travel-alerts/flights/lookup/${encodeURIComponent(flightNumber)}`);
  return res.data;
}
