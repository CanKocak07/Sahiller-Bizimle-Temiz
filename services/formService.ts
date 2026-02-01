type Json = any;

const RAW_API_BASE = (import.meta as any)?.env?.VITE_API_BASE_URL;
// Prefer same-origin (/api) so Vite proxy (dev) and reverse-proxy (prod) work.
const API_BASE =
  typeof RAW_API_BASE === 'string' && RAW_API_BASE.trim() !== ''
    ? RAW_API_BASE.replace(/\/$/, '')
    : '';

async function postJSON<T = Json>(path: string, body: unknown): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const txt = await res.text().catch(() => '');
    throw new Error(`HTTP ${res.status} ${res.statusText} - ${url} - ${txt}`);
  }

  return (await res.json()) as T;
}

export type VolunteerSignup = {
  name: string;
  email: string;
  phone: string;
  beachId: string;
  date: string;
  message?: string;
};

export async function submitVolunteerSignup(payload: VolunteerSignup) {
  return postJSON('/api/forms/volunteer', payload);
}

export async function subscribeNewsletter(email: string) {
  return postJSON('/api/forms/newsletter', { email });
}
