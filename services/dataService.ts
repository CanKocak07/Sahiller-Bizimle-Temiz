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
    chlorophyll: number | null;
    no2_mol_m2: number | null;
    air_quality: string | null;
    wqi: number | null;
  }>;
  averages: {
    sst_celsius: number | null;
    turbidity_ndti: number | null;
    chlorophyll: number | null;
    no2_mol_m2: number | null;
    wqi: number | null;
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

function randBetween(min: number, max: number): number {
  return min + Math.random() * (max - min);
}

function hashStringToUint32(s: string): number {
  // Simple, stable 32-bit hash (FNV-1a).
  let h = 0x811c9dc5;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  return h >>> 0;
}

function mulberry32(seed: number): () => number {
  // Deterministic PRNG in [0,1).
  return () => {
    let t = (seed += 0x6d2b79f5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function makeSeededRng(seedText: string): () => number {
  return mulberry32(hashStringToUint32(seedText));
}

function randBetweenSeeded(rng: () => number, min: number, max: number): number {
  return min + rng() * (max - min);
}

function jitterAroundSeeded(
  rng: () => number,
  base: number,
  plusMinus: number,
  min: number,
  max: number,
): number {
  return clamp(base + randBetweenSeeded(rng, -plusMinus, plusMinus), min, max);
}

function jitterAround(base: number, plusMinus: number, min: number, max: number): number {
  return clamp(base + randBetween(-plusMinus, plusMinus), min, max);
}

function roundTo(n: number, digits: number): number {
  const p = 10 ** digits;
  return Math.round(n * p) / p;
}

function roundToIntOrNull(n: number | null | undefined): number | null {
  if (n == null || Number.isNaN(n)) return null;
  return Math.round(n);
}

function toTemperature2dpOrNull(n: number | null | undefined): number | null {
  if (n == null || Number.isNaN(n)) return null;
  // Always add a small jitter (±0.05) so flat lines still move slightly.
  const j = jitterAround(n, 0.05, -50, 80);
  return roundTo(j, 2);
}

function toTemperature2dpOrNullSeeded(rng: () => number, n: number | null | undefined): number | null {
  if (n == null || Number.isNaN(n)) return null;
  const j = jitterAroundSeeded(rng, n, 0.05, -50, 80);
  return roundTo(j, 2);
}

function wqiToIndexOrNull(wqi: number | null | undefined): number | null {
  if (wqi == null || Number.isNaN(wqi)) return null;
  return Math.round(clamp(wqi, 0, 100));
}

type AirClass = 'good' | 'moderate' | 'poor';

function classifyNo2(no2: number | null | undefined): AirClass | null {
  if (no2 == null || Number.isNaN(no2)) return null;
  // Same thresholds as backend classify_no2.
  if (no2 < 0.00003) return 'good';
  if (no2 < 0.00006) return 'moderate';
  return 'poor';
}

function fluctuateWqi(base: number | null): number | null {
  if (base == null) return null;
  // WQI: spread within ±5
  return Math.round(jitterAround(base, 5, 0, 100));
}

function fluctuateWqiSeeded(rng: () => number, base: number | null): number | null {
  if (base == null) return null;
  return Math.round(jitterAroundSeeded(rng, base, 5, 0, 100));
}

function fluctuateAirQualityFromClass(cls: AirClass | null): number | null {
  if (cls == null) return null;
  // good -> 90-100, moderate -> 80-90, poor -> 70-80
  if (cls === 'good') return Math.round(randBetween(90, 100));
  if (cls === 'moderate') return Math.round(randBetween(80, 90));
  return Math.round(randBetween(70, 80));
}

function fluctuateAirQualityFromClassSeeded(rng: () => number, cls: AirClass | null): number | null {
  if (cls == null) return null;
  if (cls === 'good') return Math.round(randBetweenSeeded(rng, 90, 100));
  if (cls === 'moderate') return Math.round(randBetweenSeeded(rng, 80, 90));
  return Math.round(randBetweenSeeded(rng, 70, 80));
}

function meanOrNull(values: Array<number | null | undefined>): number | null {
  const xs = values.filter((v): v is number => typeof v === 'number' && !Number.isNaN(v));
  if (xs.length === 0) return null;
  const sum = xs.reduce((a, b) => a + b, 0);
  return sum / xs.length;
}

function seriesToEnvironmentalData(series: BeachSummaryResponse['series'], seedBase: string): EnvironmentalData[] {
  return (series || []).map((r) => {
    const wqiBase = wqiToIndexOrNull(r.wqi);
    const airClass = classifyNo2(r.no2_mol_m2);

    // Deterministic per window + day + metric so values don't change on page refresh.
    const seedPrefix = `${seedBase}|${r.date}|`;
    const wqiRng = makeSeededRng(`${seedPrefix}wqi`);
    const airRng = makeSeededRng(`${seedPrefix}air`);
    const tempRng = makeSeededRng(`${seedPrefix}temp`);

    return {
      date: r.date,
      waterQuality: fluctuateWqiSeeded(wqiRng, wqiBase),
      airQuality: fluctuateAirQualityFromClassSeeded(airRng, airClass),
      temperature: toTemperature2dpOrNullSeeded(tempRng, r.sst_celsius),
    };
  });
}

async function getBeachSummary(beachId: string, days: number): Promise<BeachSummaryResponse> {
  return fetchJSON(`/api/metrics/beach-summary?beach_id=${encodeURIComponent(beachId)}&days=${days}`);
}

export const getBeachData = async (beachId: string, historyDays: number = 7): Promise<BeachData | null> => {
  const beach = BEACHES.find((b: any) => b.id === beachId);
  if (!beach) return null;

  const summary = await getBeachSummary(beachId, historyDays);

  // Prefer cache window_start so jitter changes only when the 5-day window changes.
  const seedBase = summary.cache?.window_start ?? summary.cache?.generated_at ?? summary.series?.[0]?.date ?? '';
  const history = seriesToEnvironmentalData(summary.series, seedBase);

  // Summary cards: compute "average" stats from the (fluctuated) series.
  const currentStats = {
    date: history.length ? history[history.length - 1].date : '',
    waterQuality: (() => {
      const m = meanOrNull(history.map((h) => h.waterQuality));
      return m == null ? null : Math.round(clamp(m, 0, 100));
    })(),
    airQuality: (() => {
      const m = meanOrNull(history.map((h) => h.airQuality));
      return m == null ? null : Math.round(clamp(m, 0, 100));
    })(),
    temperature: (() => {
      const m = meanOrNull(history.map((h) => h.temperature));
      return m == null ? null : roundTo(m, 2);
    })(),
  };

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

      const seedBase = summary.cache?.window_start ?? summary.cache?.generated_at ?? summary.series?.[0]?.date ?? '';
      const history = seriesToEnvironmentalData(summary.series, seedBase);

      const currentStats = {
        date: history.length ? history[history.length - 1].date : '',
        waterQuality: (() => {
          const m = meanOrNull(history.map((h) => h.waterQuality));
          return m == null ? null : Math.round(clamp(m, 0, 100));
        })(),
        airQuality: (() => {
          const m = meanOrNull(history.map((h) => h.airQuality));
          return m == null ? null : Math.round(clamp(m, 0, 100));
        })(),
        temperature: (() => {
          const m = meanOrNull(history.map((h) => h.temperature));
          return m == null ? null : roundTo(m, 2);
        })(),
      };

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
