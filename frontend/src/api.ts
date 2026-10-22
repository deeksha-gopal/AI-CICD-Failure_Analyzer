import type { Analysis, AnalysisMode, Health, HistoryItem } from './types';

const ROOT = import.meta.env.VITE_API_BASE || '/api';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${ROOT}${path}`, init);
  } catch {
    throw new Error('Cannot reach the backend. Check that the API is running.');
  }
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = await response.json() as { detail?: string };
      if (typeof body.detail === 'string') message = body.detail;
    } catch { /* Non-JSON error response */ }
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}

export const getHealth = () => request<Health>('/health');
export const getHistory = () => request<HistoryItem[]>('/history');
export const getAnalysis = (id: string) => request<Analysis>(`/history/${encodeURIComponent(id)}`);

export async function analyzeLog(file: File, mode: AnalysisMode): Promise<Analysis> {
  const data = new FormData();
  data.set('file', file);
  data.set('mode', mode);
  return request<Analysis>('/analyze', { method: 'POST', body: data });
}
