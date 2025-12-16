import { BeachData } from "../types";

const RAW_API_BASE = (import.meta as any)?.env?.VITE_API_BASE_URL;
// Default to same-origin (Vite proxy handles /api) to avoid CORS issues.
const API_BASE =
  typeof RAW_API_BASE === 'string' && RAW_API_BASE.trim() !== ''
    ? RAW_API_BASE.replace(/\/$/, '')
    : '';

export const generateBeachReport = async (beachData: BeachData): Promise<string> => {
  try {
    const res = await fetch(`${API_BASE}/api/ai/beach-report`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ beach: beachData }),
    });

    if (!res.ok) {
      const raw = await res.text().catch(() => '');
      let detail = '';
      try {
        const parsed = JSON.parse(raw) as { detail?: unknown };
        detail = typeof parsed?.detail === 'string' ? parsed.detail : '';
      } catch {
        detail = '';
      }

      console.error('AI API error:', res.status, detail || raw);

      if (res.status === 503 && detail.includes('OPENAI_API_KEY')) {
        return 'AI raporu için backend ayarı eksik: OPENAI_API_KEY.';
      }

      return `Şu anda analiz oluşturulamıyor (AI servis hatası${detail ? `: ${detail}` : ''}).`;
    }

    const json = (await res.json()) as { report?: string };
    return json.report || 'Analiz şu anda kullanılamıyor.';
  } catch (error) {
    console.error("AI Generation Error:", error);
    return "Ağ hatası veya yapılandırma sorunu nedeniyle şu anda analiz oluşturulamıyor.";
  }
};