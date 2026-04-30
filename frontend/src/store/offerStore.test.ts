/**
 * Tests for offer store.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useOfferStore } from './offerStore';

// Mock API
vi.mock('@/api/offerClient', () => ({
  listProducts: vi.fn().mockResolvedValue({ data: [
    { id: 'w1', name: 'Wino testowe', category: 'wine', base_price: 80, slot_size: 0, stock_quantity: 100 },
    { id: 's1', name: 'Piernik', category: 'sweet', base_price: 8.5, slot_size: 1, stock_quantity: 500 },
  ]}),
  listPackagings: vi.fn().mockResolvedValue({ data: [
    { id: 'p1', name: 'Pudełko testowe', packaging_type: 'test', bottles: 1, sweet_slots: 5, price: 26, stock_quantity: 400 },
  ]}),
  listColors: vi.fn().mockResolvedValue({ data: [
    { code: 'red', name: 'Czerwony', hex_value: '#DC2626' },
  ]}),
  listOccasions: vi.fn().mockResolvedValue({ data: [
    { code: 'christmas', name: 'Boże Narodzenie', allowed_colors_json: ['red', 'gold'] },
  ]}),
  listDiscounts: vi.fn().mockResolvedValue({ data: [
    { id: 'd1', rule_type: 'wine', min_quantity: 100, max_quantity: 199, discount_percent: 5 },
  ]}),
  createOffer: vi.fn().mockResolvedValue({ data: { id: 'offer1', offer_number: 'OF/2026/05/0001' }}),
  getOffer: vi.fn().mockResolvedValue({ data: {
    id: 'offer1', offer_number: 'OF/2026/05/0001', client_id: 'c1', status: 'draft',
    quantity: 100, sets: [],
  }}),
  addSet: vi.fn().mockResolvedValue({ data: { id: 'set1', name: 'Test', unit_price: 0 }}),
  removeSet: vi.fn().mockResolvedValue({ data: { ok: true }}),
  addItemToSet: vi.fn().mockResolvedValue({ data: { id: 'item1', unit_price: 76 }}),
  removeItemFromSet: vi.fn().mockResolvedValue({ data: { ok: true }}),
}));

describe('offerStore', () => {
  beforeEach(() => {
    useOfferStore.setState({
      products: [], packagings: [], colors: [], occasions: [], discountRules: [],
      catalogLoaded: false, offer: null, activeSetId: null, isLoading: false, error: null,
    });
  });

  it('loadCatalog loads all catalog data', async () => {
    await useOfferStore.getState().loadCatalog();
    const state = useOfferStore.getState();
    expect(state.catalogLoaded).toBe(true);
    expect(state.products).toHaveLength(2);
    expect(state.packagings).toHaveLength(1);
    expect(state.colors).toHaveLength(1);
    expect(state.occasions).toHaveLength(1);
    expect(state.discountRules).toHaveLength(1);
  });

  it('loadCatalog is idempotent', async () => {
    await useOfferStore.getState().loadCatalog();
    await useOfferStore.getState().loadCatalog(); // second call
    expect(useOfferStore.getState().catalogLoaded).toBe(true);
  });

  it('loadOffer sets offer and activeSetId', async () => {
    await useOfferStore.getState().loadOffer('offer1');
    const state = useOfferStore.getState();
    expect(state.offer?.id).toBe('offer1');
    expect(state.offer?.quantity).toBe(100);
  });

  it('setActiveSet changes activeSetId', () => {
    useOfferStore.getState().setActiveSet('set2');
    expect(useOfferStore.getState().activeSetId).toBe('set2');
  });

  it('setError sets and clears error', () => {
    useOfferStore.getState().setError('test error');
    expect(useOfferStore.getState().error).toBe('test error');
    useOfferStore.getState().setError(null);
    expect(useOfferStore.getState().error).toBeNull();
  });
});
