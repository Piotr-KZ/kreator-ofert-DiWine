/**
 * TypeScript types for Offer module.
 */

export interface Product {
  id: string;
  name: string;
  category: 'wine' | 'sweet' | 'decoration' | 'personalization';
  base_price: number;
  wine_color?: string | null;
  wine_type?: string | null;
  slot_size: number;
  available_colors_json?: string[] | null;
  stock_quantity: number;
  restock_days?: number;
  supplier_id?: string | null;
  image_url?: string | null;
  description?: string | null;
}

export interface PackagingItem {
  id: string;
  name: string;
  packaging_type: string;
  bottles: number;
  sweet_slots: number;
  price: number;
  stock_quantity: number;
}

export interface ColorItem {
  code: string;
  name: string;
  hex_value: string;
}

export interface OccasionItem {
  code: string;
  name: string;
  allowed_colors_json: string[] | null;
}

export interface DiscountRuleItem {
  id: string;
  rule_type: string;
  product_id?: string | null;
  min_quantity: number;
  max_quantity: number;
  discount_percent?: number | null;
  fixed_price?: number | null;
}

export interface SetItemData {
  id?: string;
  product_id: string;
  item_type: string;
  color_code?: string | null;
  quantity: number;
  unit_price: number;
}

export interface OfferSetData {
  id?: string;
  name: string;
  position: number;
  budget_per_unit?: number | null;
  packaging_id?: string | null;
  unit_price: number;
  total_price: number;
  items: SetItemData[];
}

export interface OfferData {
  id: string;
  offer_number: string;
  client_id: string;
  client_name?: string;
  status: string;
  occasion_code?: string;
  quantity: number;
  deadline?: string;
  delivery_address?: string;
  sets: OfferSetData[];
  created_at?: string;
}

export interface ClientData {
  id: string;
  company_name: string;
  nip?: string;
  contact_person?: string;
  contact_role?: string;
  email?: string;
  phone?: string;
}

// Wine color mapping for visual display
export const WINE_COLORS: Record<string, { bg: string; text: string }> = {
  'czerwone': { bg: '#DC2626', text: '#fff' },
  'białe': { bg: '#FEF9E7', text: '#78350F' },
  'różowe': { bg: '#FBCFE8', text: '#831843' },
  'pomarańczowe': { bg: '#EA580C', text: '#fff' },
};

export interface CalcResult {
  packaging: number;
  wines: number;
  sweets: number;
  personalization: number;
  unit_total: number;
  grand_total: number;
  wine_discount_percent: number;
  warnings: string[];
}
