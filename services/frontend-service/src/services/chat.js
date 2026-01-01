import api from './api';

export async function getConversations(limit = null, cursor = null) {
  const params = {};
  if (limit) params.limit = limit;
  if (cursor) params.cursor = cursor;
  const res = await api.get('/api/chat/conversations', { params });
  return res.data.conversations || res.data || [];
}

export async function getMessages(conversationId, limit = 100, cursor = null) {
  const params = { limit };
  if (cursor) params.cursor = cursor;
  const res = await api.get(`/api/chat/conversations/${conversationId}/messages`, { params });
  return res.data.messages || res.data || [];
}

export async function createConversation(participants) {
  const res = await api.post('/api/chat/conversations', { participants: participants.map(String) });
  return res.data;
}

export async function sendMessage(conversationId, content) {
  const res = await api.post(`/api/chat/conversations/${conversationId}/messages`, { content });
  return res.data;
}

export async function getChatCentrifugoToken() {
  const res = await api.post('/api/chat/centrifugo-token');
  return res.data;
}
