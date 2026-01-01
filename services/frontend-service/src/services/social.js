import api from './api';

export async function followUser(followerId, followingId) {
  const res = await api.post('/api/social/follow', { follower_id: String(followerId), following_id: String(followingId) });
  return res.data;
}

export async function getFollowers(userId) {
  const res = await api.get(`/api/social/followers/${userId}`);
  const result = res.data.items || res.data.followers || Array.isArray(res.data) ? res.data : [];
  console.log('[getFollowers] response structure:', {
    hasItems: !!res.data.items,
    hasFollowers: !!res.data.followers,
    isDataArray: Array.isArray(res.data),
    resultIsArray: Array.isArray(result),
    resultLength: Array.isArray(result) ? result.length : 'N/A'
  });
  return result;
}

export async function getFollowing(userId) {
  const res = await api.get(`/api/social/following/${userId}`);
  const result = res.data.items || res.data.following || Array.isArray(res.data) ? res.data : [];
  console.log('[getFollowing] response structure:', {
    hasItems: !!res.data.items,
    hasFollowing: !!res.data.following,
    isDataArray: Array.isArray(res.data),
    resultIsArray: Array.isArray(result),
    resultLength: Array.isArray(result) ? result.length : 'N/A'
  });
  return result;
}

export async function getSocialCentrifugoToken() {
  const res = await api.post('/api/social/centrifugo-token');
  return res.data;
}
