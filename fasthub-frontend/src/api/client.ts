import axios from 'axios';
import { APP_CONFIG } from '@/config/app.config';

export const apiClient = axios.create({
  baseURL: APP_CONFIG.api.baseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(APP_CONFIG.auth.tokenKey) || sessionStorage.getItem(APP_CONFIG.auth.tokenKey);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle token refresh
let isRefreshing = false;
let failedQueue: any[] = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return apiClient(originalRequest);
        }).catch(err => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const refreshToken = localStorage.getItem(APP_CONFIG.auth.refreshTokenKey) || sessionStorage.getItem(APP_CONFIG.auth.refreshTokenKey);
        if (!refreshToken) {
          throw new Error('No refresh token');
        }

        const { data } = await axios.post(`${APP_CONFIG.api.baseUrl}/auth/refresh`, {
          refresh_token: refreshToken,
        });

        // Save new token to the same storage as refresh token
        if (localStorage.getItem(APP_CONFIG.auth.refreshTokenKey)) {
          localStorage.setItem(APP_CONFIG.auth.tokenKey, data.access_token);
        } else {
          sessionStorage.setItem(APP_CONFIG.auth.tokenKey, data.access_token);
        }

        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        processQueue(null, data.access_token);
        isRefreshing = false;

        return apiClient(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        isRefreshing = false;
        localStorage.removeItem(APP_CONFIG.auth.tokenKey);
        localStorage.removeItem(APP_CONFIG.auth.refreshTokenKey);
        sessionStorage.removeItem(APP_CONFIG.auth.tokenKey);
        sessionStorage.removeItem(APP_CONFIG.auth.refreshTokenKey);
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
