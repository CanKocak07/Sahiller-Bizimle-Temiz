const TR_OFFSET_MINUTES = 180; // Europe/Istanbul is UTC+3 (no DST)

function nowUtcMs(): number {
  const now = new Date();
  return now.getTime() + now.getTimezoneOffset() * 60_000;
}

export function getTrDateKey(utcMs: number = nowUtcMs()): string {
  const trMs = utcMs + TR_OFFSET_MINUTES * 60_000;
  const tr = new Date(trMs);
  const y = tr.getUTCFullYear();
  const m = String(tr.getUTCMonth() + 1).padStart(2, '0');
  const d = String(tr.getUTCDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

export function getNextTrMidnightUtcDate(utcMs: number = nowUtcMs()): Date {
  const trMs = utcMs + TR_OFFSET_MINUTES * 60_000;
  const tr = new Date(trMs);
  const y = tr.getUTCFullYear();
  const m = tr.getUTCMonth();
  const d = tr.getUTCDate();

  // Next day 00:00 in TR, converted back to UTC
  const nextTrMidnightUtcMs = Date.UTC(y, m, d + 1, 0, 0, 0) - TR_OFFSET_MINUTES * 60_000;
  return new Date(nextTrMidnightUtcMs);
}

export function getTimeUntilNextTrMidnightMs(now: Date = new Date()): number {
  const utcMs = now.getTime() + now.getTimezoneOffset() * 60_000;
  const next = getNextTrMidnightUtcDate(utcMs);
  return Math.max(0, next.getTime() - now.getTime());
}

export function formatDuration(ms: number, opts?: { showSeconds?: boolean }): string {
  const showSeconds = opts?.showSeconds ?? true;
  const totalSeconds = Math.floor(ms / 1000);
  const s = totalSeconds % 60;
  const totalMinutes = Math.floor(totalSeconds / 60);
  const m = totalMinutes % 60;
  const h = Math.floor(totalMinutes / 60);

  const hh = String(h).padStart(2, '0');
  const mm = String(m).padStart(2, '0');
  if (!showSeconds) return `${hh}:${mm}`;
  const ss = String(s).padStart(2, '0');
  return `${hh}:${mm}:${ss}`;
}
