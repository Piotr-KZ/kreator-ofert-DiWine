import { create } from 'zustand';
import { BillingPlan } from '../types/models';
import { billingApi } from '../api/billing';

interface BillingState {
  subscription: any | null;
  plans: BillingPlan[];
  isLoading: boolean;
  error: string | null;

  fetchSubscription: () => Promise<void>;
  fetchPlans: () => Promise<void>;
  clearError: () => void;
}

export const useBillingStore = create<BillingState>((set) => ({
  subscription: null,
  plans: [],
  isLoading: false,
  error: null,

  fetchSubscription: async () => {
    set({ isLoading: true, error: null });
    try {
      const { data } = await billingApi.getSubscription();
      set({ subscription: data, isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to fetch subscription',
        isLoading: false,
        subscription: null,
      });
    }
  },

  fetchPlans: async () => {
    try {
      const { data } = await billingApi.getPlans();
      set({ plans: data });
    } catch {
      // Plans fetch failure is non-critical
    }
  },

  clearError: () => set({ error: null }),
}));
