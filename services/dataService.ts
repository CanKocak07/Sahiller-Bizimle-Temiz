import { BeachData, EnvironmentalData } from '../types';
import { BEACHES } from '../constants';

const RAW_API_BASE = (import.meta as any)?.env?.VITE_API_BASE_URL;
// Default to same-origin (Vite proxy handles /api) to avoid CORS issues.
const API_BASE =
  typeof RAW_API_BASE === 'string' && RAW_API_BASE.trim() !== ''
    ? RAW_API_BASE.replace(/\/$/, '')
    : '';

type Json = any;

type BeachSummaryResponse = {
  beach: { id: string; name: string; lat?: number; lon?: number };
  days: number;
  series: Array<{
    date: string;
    sst_celsius: number | null;
    turbidity_ndti: number | null;
    pollution_percent: number | null;
    chlorophyll: number | null;
    no2_mol_m2: number | null;
    air_quality: string | null;
    wqi: number | null;
    crowdedness_percent: number | null;
  }>;
  averages: {
    sst_celsius: number | null;
    turbidity_ndti: number | null;
    pollution_percent: number | null;
    chlorophyll: number | null;
    no2_mol_m2: number | null;
    wqi: number | null;
    crowdedness_percent: number | null;
  };
  cache?: {
    window_start?: string;
    window_end?: string;
    generated_at?: string;
    hit?: boolean;
  };
};

async function fetchJSON<T = Json>(path: string): Promise<T> {
  const url = `${API_BASE}${path}`;

  const maxAttempts = 3;
  let lastError: unknown;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      const res = await fetch(url);
      if (!res.ok) {
        const txt = await res.text().catch(() => '');
        // Retry only on transient server errors.
        if (res.status >= 500 && attempt < maxAttempts) {
          await new Promise((r) => setTimeout(r, 250 * attempt));
          continue;
        }
        throw new Error(`HTTP ${res.status} ${res.statusText} - ${url} - ${txt}`);
      }
      return res.json() as Promise<T>;
    } catch (e) {
      lastError = e;
      // Retry on network/proxy failures.
      if (attempt < maxAttempts) {
        await new Promise((r) => setTimeout(r, 250 * attempt));
        continue;
      }
    }
  }

  throw lastError instanceof Error ? lastError : new Error(`Request failed: ${url}`);
}

function clamp(n: number, min: number, max: number) {
  return Math.max(min, Math.min(max, n));
}

function toPercentOrNull(n: number | null | undefined): number | null {
  if (n == null || Number.isNaN(n)) return null;
  return Math.round(clamp(n, 0, 100));
}

function roundToIntOrNull(n: number | null | undefined): number | null {
  if (n == null || Number.isNaN(n)) return null;
  return Math.round(n);
}

function wqiToIndexOrNull(wqi: number | null | undefined): number | null {
  if (wqi == null || Number.isNaN(wqi)) return null;
  return Math.round(clamp(wqi, 0, 100));
}

function no2ToRelativeIndex(no2: number | null | undefined): number | null {
  if (no2 == null || Number.isNaN(no2)) return null;

  // classify_no2 eşiklerini “relative index”e çeviriyoruz.
  // good ~ 20, moderate ~ 50, poor ~ 80 gibi okunabilir bir ölçek.
  if (no2 < 0.00003) return 20;
  if (no2 < 0.00006) return 50;
  return 80;
}

function seriesToEnvironmentalData(series: BeachSummaryResponse['series']): EnvironmentalData[] {
  return (series || []).map((r) => ({
    date: r.date,
    occupancy: toPercentOrNull(r.crowdedness_percent),
    waterQuality: wqiToIndexOrNull(r.wqi),
    airQuality: no2ToRelativeIndex(r.no2_mol_m2),
    temperature: roundToIntOrNull(r.sst_celsius),
    pollutionLevel: toPercentOrNull(r.pollution_percent),
  }));
}

async function getBeachSummary(beachId: string, days: number): Promise<BeachSummaryResponse> {
  return fetchJSON(`/api/metrics/beach-summary?beach_id=${encodeURIComponent(beachId)}&days=${days}`);
}

export const getBeachData = async (beachId: string, historyDays: number = 7): Promise<BeachData | null> => {
  const beach = BEACHES.find((b: any) => b.id === beachId);
  if (!beach) return null;

  const summary = await getBeachSummary(beachId, historyDays);
  const avg = summary.averages;

  const currentStats = {
    occupancy: toPercentOrNull(avg.crowdedness_percent),
    waterQuality: wqiToIndexOrNull(avg.wqi),
    temperature: roundToIntOrNull(avg.sst_celsius),
    pollutionLevel: toPercentOrNull(avg.pollution_percent),
    airQuality: no2ToRelativeIndex(avg.no2_mol_m2),
  };

  const history = seriesToEnvironmentalData(summary.series);

  return {
    ...(beach as any),
    history,
    currentStats,
  };
};

export const getAllBeachesData = async (historyDays: number = 7): Promise<BeachData[]> => {
  const settled = await Promise.allSettled(
    BEACHES.map(async (beach: any) => {
      const summary = await getBeachSummary(beach.id, historyDays);
      const avg = summary.averages;

      const currentStats = {
        occupancy: toPercentOrNull(avg.crowdedness_percent),
        waterQuality: wqiToIndexOrNull(avg.wqi),
        temperature: roundToIntOrNull(avg.sst_celsius),
        pollutionLevel: toPercentOrNull(avg.pollution_percent),
        airQuality: no2ToRelativeIndex(avg.no2_mol_m2),
      };

      const history = seriesToEnvironmentalData(summary.series);

      return {
        ...(beach as any),
        history,
        currentStats,
      } as BeachData;
    })
  );

  const results: BeachData[] = [];
  for (const r of settled) {
    if (r.status === 'fulfilled') results.push(r.value);
    else console.error('getAllBeachesData failed:', r.reason);
  }
  return results;
};
