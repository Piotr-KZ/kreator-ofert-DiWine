import { create } from 'zustand';
import { Organization } from '../types/models';
import { organizationsApi } from '../api/organizations';

interface OrgState {
  organization: Organization | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  fetchOrganization: () => Promise<void>;
  updateOrganization: (data: Partial<Organization>) => Promise<void>;
  deleteOrganization: () => Promise<void>;
  clearError: () => void;
}

export const useOrgStore = create<OrgState>((set, get) => ({
  organization: null,
  isLoading: false,
  error: null,

  fetchOrganization: async () => {
    set({ isLoading: true, error: null });
    try {
      const { data } = await organizationsApi.getMe();
      // Persist org ID for API interceptor (X-Organization-Id header)
      if (data?.id) {
        localStorage.setItem('current_organization_id', data.id);
      }
      set({
        organization: data,
        isLoading: false
      });
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Failed to fetch organization',
        isLoading: false 
      });
    }
  },

  updateOrganization: async (data: Partial<Organization>) => {
    const { organization } = get();
    if (!organization) return;

    set({ isLoading: true, error: null });
    try {
      const { data: updated } = await organizationsApi.update(organization.id, data);
      set({ 
        organization: updated, 
        isLoading: false 
      });
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Failed to update organization',
        isLoading: false 
      });
      throw error;
    }
  },

  deleteOrganization: async () => {
    const { organization } = get();
    if (!organization) return;

    set({ isLoading: true, error: null });
    try {
      await organizationsApi.delete(organization.id);
      set({ 
        organization: null, 
        isLoading: false 
      });
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Failed to delete organization',
        isLoading: false 
      });
      throw error;
    }
  },

  clearError: () => set({ error: null }),
}));
