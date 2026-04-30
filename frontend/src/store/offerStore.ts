/**
 * Offer Zustand store — state management for offer configurator.
 */

import axios from 'axios';
import { create } from 'zustand';
import * as offerApi from '@/api/offerClient';
import type {
  Product, PackagingItem, ColorItem, OccasionItem,
  DiscountRuleItem, OfferData, OfferSetData, ClientData,
} from '@/types/offer';

function extractError(e: unknown, fallback = 'Wystąpił błąd'): string {
  if (axios.isAxiosError(e)) return e.response?.data?.detail || e.message || fallback;
  return e instanceof Error ? e.message : fallback;
}

interface OfferState {
  // Catalog (loaded once)
  products: Product[];
  packagings: PackagingItem[];
  colors: ColorItem[];
  occasions: OccasionItem[];
  discountRules: DiscountRuleItem[];
  catalogLoaded: boolean;

  // Current offer
  offer: OfferData | null;
  activeSetId: string | null;

  // UI
  isLoading: boolean;
  error: string | null;

  // Actions
  loadCatalog: () => Promise<void>;
  createOffer: (clientId: string, quantity: number, occasionCode?: string) => Promise<string>;
  loadOffer: (id: string) => Promise<void>;
  addSet: (name: string, packagingId: string, budget?: number) => Promise<void>;
  removeSet: (setId: string) => Promise<void>;
  addItem: (setId: string, productId: string, itemType: string, colorCode?: string) => Promise<void>;
  removeItem: (setId: string, itemId: string) => Promise<void>;
  setActiveSet: (setId: string) => void;
  setError: (e: string | null) => void;
}

export const useOfferStore = create<OfferState>((set, get) => ({
  products: [],
  packagings: [],
  colors: [],
  occasions: [],
  discountRules: [],
  catalogLoaded: false,
  offer: null,
  activeSetId: null,
  isLoading: false,
  error: null,

  loadCatalog: async () => {
    if (get().catalogLoaded) return;
    set({ isLoading: true });
    try {
      const [prods, pkgs, cols, occs, discs] = await Promise.all([
        offerApi.listProducts(),
        offerApi.listPackagings(),
        offerApi.listColors(),
        offerApi.listOccasions(),
        offerApi.listDiscounts(),
      ]);
      set({
        products: prods.data,
        packagings: pkgs.data,
        colors: cols.data,
        occasions: occs.data,
        discountRules: discs.data,
        catalogLoaded: true,
      });
    } catch (e) {
      set({ error: extractError(e, 'Błąd ładowania katalogu') });
    } finally {
      set({ isLoading: false });
    }
  },

  createOffer: async (clientId, quantity, occasionCode) => {
    set({ isLoading: true, error: null });
    try {
      const { data } = await offerApi.createOffer({
        client_id: clientId,
        quantity,
        occasion_code: occasionCode,
      });
      await get().loadOffer(data.id);
      return data.id;
    } catch (e) {
      set({ error: extractError(e, 'Błąd tworzenia oferty') });
      throw e;
    } finally {
      set({ isLoading: false });
    }
  },

  loadOffer: async (id) => {
    set({ isLoading: true });
    try {
      const { data } = await offerApi.getOffer(id);
      set({
        offer: data,
        activeSetId: data.sets?.[0]?.id || null,
      });
    } catch (e) {
      set({ error: extractError(e, 'Błąd ładowania oferty') });
    } finally {
      set({ isLoading: false });
    }
  },

  addSet: async (name, packagingId, budget) => {
    const offer = get().offer;
    if (!offer) return;
    set({ isLoading: true, error: null });
    try {
      const { data } = await offerApi.addSet(offer.id, {
        name,
        packaging_id: packagingId,
        budget_per_unit: budget,
      });
      await get().loadOffer(offer.id);
      set({ activeSetId: data.id });
    } catch (e) {
      set({ error: extractError(e, 'Błąd dodawania zestawu') });
    } finally {
      set({ isLoading: false });
    }
  },

  removeSet: async (setId) => {
    const offer = get().offer;
    if (!offer) return;
    try {
      await offerApi.removeSet(offer.id, setId);
      await get().loadOffer(offer.id);
    } catch (e) {
      set({ error: extractError(e, 'Błąd usuwania zestawu') });
    }
  },

  addItem: async (setId, productId, itemType, colorCode) => {
    const offer = get().offer;
    if (!offer) return;
    set({ error: null });
    try {
      await offerApi.addItemToSet(offer.id, setId, {
        product_id: productId,
        item_type: itemType,
        color_code: colorCode,
      });
      await get().loadOffer(offer.id);
    } catch (e) {
      set({ error: extractError(e) });
    }
  },

  removeItem: async (setId, itemId) => {
    const offer = get().offer;
    if (!offer) return;
    try {
      await offerApi.removeItemFromSet(offer.id, setId, itemId);
      await get().loadOffer(offer.id);
    } catch (e) {
      set({ error: extractError(e, 'Błąd usuwania pozycji') });
    }
  },

  setActiveSet: (setId) => set({ activeSetId: setId }),
  setError: (e) => set({ error: e }),
}));
