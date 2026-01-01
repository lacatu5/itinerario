import axios from 'axios';
import { getCurrentUserToken } from './authStore';

const isDev = import.meta.env.DEV;
const baseURL = isDev ? '/' : import.meta.env.VITE_API_URL || 'https://api.your-domain.com';

if (!isDev && !baseURL) {
  throw new Error('VITE_API_URL environment variable is required in production');
}

const api = axios.create( {
  baseURL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
});

api.interceptors.request.use(
  async (config) => {
    console.log('[Request] Starting request:', {
      method: config.method,
      url: config.url,
      baseURL: config.baseURL,
      fullURL: `${config.baseURL}${config.url}`,
      hasData: !!config.data,
      dataType: config.data?.constructor?.name,
    });

    try {
      const token = await getCurrentUserToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
        console.log('[Auth] Token added to request:', config.url);
      } else {
        console.warn('[Auth] No auth token available for request:', config.url);
      }
    } catch (error) {
      console.error('[Auth] Failed to get auth token:', error);
    }

    if (config.data instanceof FormData) {
      console.log('[FormData] Detected FormData, deleting Content-Type');
      console.log('[FormData] FormData entries:', Array.from(config.data.entries()));
      delete config.headers['Content-Type'];
    }

    console.log('[Request] Final config:', {
      url: config.url,
      method: config.method,
      headers: config.headers,
      timeout: config.timeout,
    });

    return config;
  },
  (error) => {
    console.error('[Request] Error in request interceptor:', error);
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    console.log('[Response] Success:', {
      status: response.status,
      url: response.config?.url,
    });
    return response;
  },
  (error) => {
    console.error('[Response] Error:', {
      message: error.message,
      code: error.code,
      status: error?.response?.status,
      url: error?.config?.url,
      timeout: error.code === 'ECONNABORTED',
    });

    const status = error?.response?.status;
    let message = error?.response?.data?.detail || error.message || 'Request failed';

    if (typeof message === 'object') {
      message = JSON.stringify(message);
    }

    const normalized = {
      message,
      status,
      response: error?.response,
    };
    return Promise.reject(normalized);
  }
);

export default api;
