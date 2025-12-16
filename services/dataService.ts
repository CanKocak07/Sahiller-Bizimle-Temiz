import { BeachData, EnvironmentalData } from '../types';
import { BEACHES } from '../constants';

const RAW_API_BASE = (import.meta as any)?.env?.VITE_API_BASE_URL;
// Default to same-origin (Vite proxy handles /api) to avoid CORS issues.
const API_BASE =
  typeof RAW_API_BASE === 'string' && RAW_API_BASE.trim() !== ''
    ? RAW_API_BASE.replace(/\/$/, '')
    : '';

type Json = any;

async function fetchJSON<T = Json>(path: string): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url);
  if (!res.ok) {
    const txt = await res.text().catch(() => '');
    throw new Error(`HTTP ${res.status} ${res.statusText} - ${url} - ${txt}`);
  }
  return res.json() as Promise<T>;
}

function clamp(n: number, min: number, max: number) {
  return Math.max(min, Math.min(max, n));
}

// Turbidity gibi “ham” değerleri UI’daki 0–100 kirlilik yüzdesine map’lemek için basit bir ölçek.
// İleride gerçek bir modele bağlayabiliriz; şimdilik UI’ı beslemek için stabil.
function turbidityToPollutionPercent(t: number | null | undefined): number {
  if (t == null || Number.isNaN(t)) return 0;

  // Backend tarafında turbidity proxy'si NDTI olarak hesaplanıyor ve aralık yaklaşık [-1, 1].
  // UI'daki "kirlilik" yüzdesi için bunu 0–100 ölçeğine normalize ediyoruz.
  // -1 -> 0%, 0 -> 50%, +1 -> 100%
  const pct = ((t + 1) / 2) * 100;
  return Math.round(clamp(pct, 0, 100));
}

function no2ToRelativeIndex(no2: number | null | undefined): number {
  if (no2 == null || Number.isNaN(no2)) return 0;

  // classify_no2 eşiklerini “relative index”e çeviriyoruz.
  // good ~ 20, moderate ~ 50, poor ~ 80 gibi okunabilir bir ölçek.
  if (no2 < 0.00003) return 20;
  if (no2 < 0.00006) return 50;
  return 80;
}

// “Trend endpoint” yazana kadar UI’daki chart’ı boş bırakmamak için:
// gerçek güncel değerin etrafında küçük oynamalarla 7 günlük seri üretiyoruz.
function generateHistoryFromCurrent(days: number, current: Omit<EnvironmentalData, 'date'>): EnvironmentalData[] {
  const data: EnvironmentalData[] = [];
  const today = new Date();

  let occ = current.occupancy;
  let wqi = current.waterQuality;
  let air = current.airQuality;
  let temp = current.temperature;
  let pol = current.pollutionLevel;

  const rand = (min: number, max: number) => Math.floor(Math.random() * (max - min + 1)) + min;

  const smooth = (prev: number, min: number, max: number, vol: number) => {
    const next = prev + rand(-vol, vol);
    return clamp(next, min, max);
  };

  for (let i = days; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(today.getDate() - i);

    const yyyy = d.getFullYear();
    const mm = String(d.getMonth() + 1).padStart(2, '0');
    const dd = String(d.getDate()).padStart(2, '0');
    const isoDate = `${yyyy}-${mm}-${dd}`;

    // Küçük volatilite (göze “gerçek” görünen trend için)
    occ = smooth(occ, 0, 100, 6);
    wqi = smooth(wqi, 0, 100, 2);
    air = smooth(air, 0, 100, 3);
    temp = smooth(temp, -5, 45, 1);
    pol = smooth(pol, 0, 100, 4);

    data.push({
      date: isoDate,
      occupancy: Math.round(occ),
      waterQuality: Math.round(wqi),
      airQuality: Math.round(air),
      temperature: Math.round(temp),
      pollutionLevel: Math.round(pol),
    });
  }

  return data;
}

async function getCurrentStatsForBeach(beachId: string): Promise<{
  occupancy: number;
  waterQuality: number;
  temperature: number;
  pollutionLevel: number;
  airQuality: number;
}> {
  // hepsini paralel çekiyoruz
  const [sstRes, wqiRes, turbRes, airRes, crowdRes] = await Promise.allSettled([
    fetchJSON(`/api/metrics/sst?beach_id=${encodeURIComponent(beachId)}&days=7`),
    fetchJSON(`/api/metrics/wqi?beach_id=${encodeURIComponent(beachId)}&days=7`),
    fetchJSON(`/api/metrics/turbidity?beach_id=${encodeURIComponent(beachId)}&days=7`),
    fetchJSON(`/api/metrics/air-quality?beach_id=${encodeURIComponent(beachId)}&days=14`),
    fetchJSON(`/api/metrics/crowdedness?beach_id=${encodeURIComponent(beachId)}`),
  ]);

  const sstC = (sstRes.status === 'fulfilled' ? sstRes.value?.data?.sst_celsius : null) as number | null;
  const wqi = (wqiRes.status === 'fulfilled' ? wqiRes.value?.data?.wqi : null) as number | null;

  const turbidity = (turbRes.status === 'fulfilled' ? turbRes.value?.data?.turbidity : null) as number | null;

  const no2 = (airRes.status === 'fulfilled' ? airRes.value?.data?.no2_mol_m2 : null) as number | null;

  const occupancyPct = (crowdRes.status === 'fulfilled'
    ? crowdRes.value?.data?.crowdedness_percent ?? crowdRes.value?.data?.occupancy_percent
    : null) as number | null;

  return {
    occupancy: occupancyPct == null ? 0 : Math.round(clamp(occupancyPct, 0, 100)),
    waterQuality: wqi == null ? 0 : Math.round(clamp(wqi, 0, 100)),
    temperature: sstC == null ? 0 : Math.round(sstC),
    pollutionLevel: turbidityToPollutionPercent(turbidity),
    airQuality: no2ToRelativeIndex(no2),
  };
}

export const getBeachData = async (beachId: string, historyDays: number = 7): Promise<BeachData | null> => {
  const beach = BEACHES.find((b: any) => b.id === beachId);
  if (!beach) return null;

  const currentStats = await getCurrentStatsForBeach(beachId);

  const history = generateHistoryFromCurrent(historyDays, {
    occupancy: currentStats.occupancy,
    waterQuality: currentStats.waterQuality,
    airQuality: currentStats.airQuality,
    temperature: currentStats.temperature,
    pollutionLevel: currentStats.pollutionLevel,
  });

  return {
    ...(beach as any),
    history,
    currentStats,
  };
};

export const getAllBeachesData = async (historyDays: number = 7): Promise<BeachData[]> => {
  const results = await Promise.all(
    BEACHES.map(async (beach: any) => {
      const currentStats = await getCurrentStatsForBeach(beach.id);

      const history = generateHistoryFromCurrent(historyDays, {
        occupancy: currentStats.occupancy,
        waterQuality: currentStats.waterQuality,
        airQuality: currentStats.airQuality,
        temperature: currentStats.temperature,
        pollutionLevel: currentStats.pollutionLevel,
      });

      return {
        ...(beach as any),
        history,
        currentStats,
      };
    })
  );

  return results;
};
