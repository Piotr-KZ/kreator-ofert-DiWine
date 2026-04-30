/**
 * API client for Offer module — mirrors backend /api/v1/offers/*.
 */

import axios from 'axios';

const api = axios.create({ baseURL: '/api/v1/offers' });

// ─── Catalog (read-only) ───

export const listProducts = (category?: string) =>
  api.get('/catalog/products', { params: category ? { category } : {} });

export const listPackagings = (params?: { packaging_type?: string; bottles?: number }) =>
  api.get('/catalog/packagings', { params });

export const listColors = () =>
  api.get('/catalog/colors');

export const listOccasions = () =>
  api.get('/catalog/occasions');

export const listDiscounts = () =>
  api.get('/catalog/discounts');

export const listSuppliers = () =>
  api.get('/catalog/suppliers');

// ─── Clients ───

export const createClient = (data: {
  company_name: string;
  nip?: string;
  contact_person?: string;
  contact_role?: string;
  email?: string;
  phone?: string;
}) => api.post('/clients', data);

export const listClients = () =>
  api.get('/clients');

export const getClient = (id: string) =>
  api.get(`/clients/${id}`);

// ─── Offers ───

export const createOffer = (data: {
  client_id: string;
  occasion_code?: string;
  quantity: number;
  deadline?: string;
  delivery_address?: string;
  source_email?: string;
}) => api.post('', data);

export const listOffers = () =>
  api.get('');

export const getOffer = (id: string) =>
  api.get(`/${id}`);

export const deleteOffer = (id: string) =>
  api.delete(`/${id}`);

// ─── Sets ───

export const addSet = (offerId: string, data: {
  name: string;
  budget_per_unit?: number;
  packaging_id?: string;
  items?: Array<{ product_id: string; item_type: string; color_code?: string; unit_price: number }>;
}) => api.post(`/${offerId}/sets`, data);

export const removeSet = (offerId: string, setId: string) =>
  api.delete(`/${offerId}/sets/${setId}`);

// ─── Set Items ───

export const addItemToSet = (offerId: string, setId: string, data: {
  product_id: string;
  item_type: string;
  color_code?: string;
}) => api.post(`/${offerId}/sets/${setId}/items`, data);

export const removeItemFromSet = (offerId: string, setId: string, itemId: string) =>
  api.delete(`/${offerId}/sets/${setId}/items/${itemId}`);

// ─── Calculator ───

export const calculatePrice = (data: {
  quantity: number;
  packaging_id?: string;
  items: Array<{ product_id: string; item_type: string }>;
}) => api.post('/calculate', data);
