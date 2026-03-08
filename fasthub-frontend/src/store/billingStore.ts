import { create } from "zustand";
import { Subscription } from "../types/models";
import { billingApi } from "../api/billing";

interface BillingState {
  subscription: Subscription | null;
  isLoading: boolean;
  error: string | null;

  fetchSubscription: () => Promise<void>;
  clearError: () => void;
}

export const useBillingStore = create<BillingState>((set) => ({
  subscription: null,
  isLoading: false,
  error: null,

  fetchSubscription: async () => {
    set({ isLoading: true, error: null });
    try {
      const { data } = await billingApi.getSubscription();
      set({ subscription: data, isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || "Failed to fetch subscription",
        isLoading: false,
      });
    }
  },

  clearError: () => set({ error: null }),
}));
