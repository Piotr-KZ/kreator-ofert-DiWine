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

/** Monotonic counter — stale loads check this to bail out. */
let loadVersion = 0;

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
  currentOfferId: string | null;   // which offer we're working with
  activeSetId: string | null;

  // UI
  isLoading: boolean;
  busy: boolean;          // true while add/remove in flight — blocks clicks
  error: string | null;

  // Actions
  loadCatalog: () => Promise<void>;
  loadOffer: (id: string) => Promise<void>;
  resetOffer: () => void;
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
  currentOfferId: null,
  activeSetId: null,
  isLoading: false,
  busy: false,
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

  resetOffer: () => {
    loadVersion++;   // invalidate any in-flight loads
    set({ offer: null, currentOfferId: null, activeSetId: null, error: null, busy: false });
  },

  loadOffer: async (id: string) => {
    const myVersion = ++loadVersion;    // claim a version
    set({ isLoading: true, currentOfferId: id });
    try {
      const { data } = await offerApi.getOffer(id);
      // Only apply if this is still the latest load
      if (loadVersion !== myVersion) return;
      // Preserve activeSetId if it still exists in loaded sets
      const currentActive = get().activeSetId;
      const stillExists = currentActive && data.sets?.some((s: any) => s.id === currentActive);
      set({
        offer: data,
        activeSetId: stillExists ? currentActive : (data.sets?.[0]?.id || null),
      });
    } catch (e) {
      if (loadVersion !== myVersion) return;
      set({ error: extractError(e, 'Błąd ładowania oferty') });
    } finally {
      if (loadVersion === myVersion) {
        set({ isLoading: false });
      }
    }
  },

  addSet: async (name, packagingId, budget) => {
    const { offer, busy, currentOfferId } = get();
    if (!offer || busy) return;
    set({ busy: true, error: null });
    try {
      const { data } = await offerApi.addSet(offer.id, {
        name,
        packaging_id: packagingId,
        budget_per_unit: budget,
      });
      // Only reload if we're still on the same offer
      if (get().currentOfferId !== offer.id) return;
      await get().loadOffer(offer.id);
      set({ activeSetId: data.id });
    } catch (e) {
      set({ error: extractError(e, 'Błąd dodawania zestawu') });
    } finally {
      set({ busy: false });
    }
  },

  removeSet: async (setId) => {
    const { offer, busy } = get();
    if (!offer || busy) return;
    set({ busy: true });
    try {
      await offerApi.removeSet(offer.id, setId);
      if (get().currentOfferId !== offer.id) return;
      await get().loadOffer(offer.id);
    } catch (e) {
      set({ error: extractError(e, 'Błąd usuwania zestawu') });
    } finally {
      set({ busy: false });
    }
  },

  addItem: async (setId, productId, itemType, colorCode) => {
    const { offer, busy } = get();
    if (!offer || busy) return;
    set({ busy: true, error: null });
    try {
      await offerApi.addItemToSet(offer.id, setId, {
        product_id: productId,
        item_type: itemType,
        color_code: colorCode,
      });
      if (get().currentOfferId !== offer.id) return;
      await get().loadOffer(offer.id);
    } catch (e) {
      set({ error: extractError(e) });
    } finally {
      set({ busy: false });
    }
  },

  removeItem: async (setId, itemId) => {
    const { offer, busy } = get();
    if (!offer || busy) return;
    set({ busy: true });
    try {
      await offerApi.removeItemFromSet(offer.id, setId, itemId);
      if (get().currentOfferId !== offer.id) return;
      await get().loadOffer(offer.id);
    } catch (e) {
      set({ error: extractError(e, 'Błąd usuwania pozycji') });
    } finally {
      set({ busy: false });
    }
  },

  setActiveSet: (setId) => set({ activeSetId: setId }),
  setError: (e) => set({ error: e }),
}));
