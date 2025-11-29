// src/services/api.ts
const API_URL = 'http://localhost:8000';

export interface GeneralStats {
  total_emissions: number;
  avg_emissions: number;
  count: number;
}

export interface RegionStats {
  REGION: string;
  count: number;
  mean: number;
  median: number;
  min: number;
  max: number;
  std: number;
}

export interface TimeSeriesPoint {
  year: number;
  value: number;
}

export interface TopEmitter {
  name: string;
  value: number;
  region: string;
}

export const fetchGeneralStats = async (): Promise<GeneralStats> => {
  const res = await fetch(`${API_URL}/stats/general`);
  if (!res.ok) throw new Error('Error fetching general stats');
  return res.json();
};

export const fetchRegionStats = async (): Promise<{ stats: RegionStats[] }> => {
  const res = await fetch(`${API_URL}/stats/regions`);
  if (!res.ok) throw new Error('Error fetching region stats');
  return res.json();
};

export const fetchTimeSeries = async (): Promise<TimeSeriesPoint[]> => {
  const res = await fetch(`${API_URL}/stats/time-series`);
  if (!res.ok) throw new Error('Error fetching time series');
  return res.json();
};

export const fetchTopEmitters = async (n = 10, by = 'REGION'): Promise<TopEmitter[]> => {
  const res = await fetch(`${API_URL}/stats/top-emitters?n=${n}&by=${by}`);
  if (!res.ok) throw new Error('Error fetching top emitters');
  return res.json();
};