import { create } from 'zustand';
import { User } from '../types/models';
import { authApi } from '../api/auth';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => Promise<void>;
  fetchCurrentUser: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      const { data } = await authApi.login({ email, password });
      
      // Save tokens
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      
      // Fetch user data
      const { data: user } = await authApi.getCurrentUser();
      
      set({ 
        user, 
        isAuthenticated: true, 
        isLoading: false 
      });
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Login failed',
        isLoading: false 
      });
      throw error;
    }
  },

  register: async (data: any) => {
    set({ isLoading: true, error: null });
    try {
      const { data: response } = await authApi.register(data);
      
      // Save tokens
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      
      // Fetch user data
      const { data: user } = await authApi.getCurrentUser();
      
      set({ 
        user, 
        isAuthenticated: true, 
        isLoading: false 
      });
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Registration failed',
        isLoading: false 
      });
      throw error;
    }
  },

  logout: async () => {
    try {
      await authApi.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear tokens and state
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      set({ 
        user: null, 
        isAuthenticated: false 
      });
    }
  },

  fetchCurrentUser: async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      set({ isAuthenticated: false, isLoading: false });
      return;
    }

    set({ isLoading: true });
    try {
      const { data: user } = await authApi.getCurrentUser();
      const currentUser = get().user;
      
      // Only update if user actually changed (prevent unnecessary re-renders)
      if (!currentUser || currentUser.id !== user.id) {
        set({ 
          user, 
          isAuthenticated: true, 
          isLoading: false 
        });
      } else {
        set({ isLoading: false });
      }
    } catch (error) {
      // Token invalid, clear auth
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      set({ 
        user: null, 
        isAuthenticated: false, 
        isLoading: false 
      });
    }
  },

  clearError: () => set({ error: null }),
}));
