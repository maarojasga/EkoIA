// src/services/api.ts
import { fetch } from '@tauri-apps/api/http'; // Si usas tauri, si no, usa el fetch nativo del navegador

const API_URL = 'http://localhost:8000';

// Tipos para los filtros
export interface DashboardFilters {
  year?: string;
  region?: string;
  category?: string;
}

// Tipos de respuesta (Expandidos según tus endpoints)
export interface FilterOptions {
  years: number[];
  regions: string[];
  categories: string[];
}

// Helper para convertir objeto de filtros a query string
const buildQuery = (filters?: DashboardFilters) => {
  if (!filters) return '';
  const params = new URLSearchParams();
  if (filters.year && filters.year !== 'all') params.append('year', filters.year);
  if (filters.region && filters.region !== 'all') params.append('region', filters.region);
  if (filters.category && filters.category !== 'all') params.append('category', filters.category);
  const str = params.toString();
  return str ? `?${str}` : '';
};

// --- Endpoints Nuevos y Existentes ---

export const fetchAvailableOptions = async (): Promise<FilterOptions> => {
  // GET /stats/available-options
  const res = await window.fetch(`${API_URL}/stats/available-options`);
  if (!res.ok) {
    // Retorno fallback si el endpoint no está listo aún para evitar crash
    return { years: [2020, 2021, 2022, 2023], regions: [], categories: [] }; 
  }
  return res.json();
};

export const fetchGeneralStats = async (filters?: DashboardFilters) => {
  const query = buildQuery(filters);
  const res = await window.fetch(`${API_URL}/stats/general${query}`);
  if (!res.ok) throw new Error('Error fetching general stats');
  return res.json();
};

export const fetchRegionStats = async (filters?: DashboardFilters) => {
  const query = buildQuery(filters);
  const finalQuery = query 
    ? `${query}&by=REGION` 
    : '?by=REGION';
    
  const res = await window.fetch(`${API_URL}/stats/regions${finalQuery}`);
  if (!res.ok) throw new Error('Error fetching region stats');
  return res.json();
};

export const fetchTimeSeries = async (filters?: DashboardFilters) => {
  const query = buildQuery(filters);
  const res = await window.fetch(`${API_URL}/stats/time-series${query}`);
  if (!res.ok) throw new Error('Error fetching time series');
  return res.json();
};

export const fetchTopEmitters = async (n = 10, filters?: DashboardFilters) => {
  const query = buildQuery(filters);
  // Concatenamos el parámetro 'n' con los filtros existentes
  const separator = query ? '&' : '?';
  const res = await window.fetch(`${API_URL}/stats/top-emitters${query}${separator}n=${n}`);
  if (!res.ok) throw new Error('Error fetching top emitters');
  return res.json();
};

export const fetchCategoryStats = async (filters?: DashboardFilters) => {
  const query = buildQuery(filters);
  const res = await window.fetch(`${API_URL}/stats/categories${query}`);
  if (!res.ok) throw new Error('Error fetching category stats');
  return res.json();
};