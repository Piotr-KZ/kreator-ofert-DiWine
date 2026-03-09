import { apiClient } from './client';

export interface GUSData {
  name: string;
  nip: string;
  regon?: string;
  krs?: string;
  legal_form?: string;
  street?: string;
  city?: string;
  postal_code?: string;
  country?: string;
  pkd_main?: string;
  pkd_main_name?: string;
  status?: string;
}

export const gusApi = {
  lookup: (nip: string) =>
    apiClient.get<GUSData>('/gus/lookup', { params: { nip } }),
};
