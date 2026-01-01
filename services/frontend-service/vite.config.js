import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    allowedHosts: ['.a.run.app'],
    proxy: {
      '/api/users': {
        target: 'http://user-service:8000',
        changeOrigin: true,
      },
      '/api/itineraries': {
        target: 'http://itinerary-service:8000',
        changeOrigin: true,
      },
      '/api/chat': {
        target: 'http://chat-service:8000',
        changeOrigin: true,
      },
      '/api/social': {
        target: 'http://social-service:8000',
        changeOrigin: true,
      },
      '/api/alerts': {
        target: 'http://travel-alerts-service:8000',
        changeOrigin: true,
      },
      '/api/destinations': {
        target: 'http://destinations-service:8000',
        changeOrigin: true,
      },
      '/api/auth': {
        target: 'http://social-service:8000',
        changeOrigin: true,
      }
    }
  },
});
