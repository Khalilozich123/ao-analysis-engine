// Backend API client. Base URL is overridable via VITE_API_BASE for other environments.
const BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000/api/v1";

export async function uploadFile(file) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/upload`, { method: "POST", body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Échec du téléversement.");
  }
  return res.json(); // { job_id, total_rows }
}

export async function getResults(jobId) {
  const res = await fetch(`${BASE}/results/${jobId}`);
  if (!res.ok) throw new Error("Impossible de récupérer les résultats.");
  return res.json(); // { job_id, status, total_rows, completed_rows, results: [...] }
}

export async function listJobs() {
  const res = await fetch(`${BASE}/jobs`);
  if (!res.ok) throw new Error("Impossible de charger l'historique.");
  return res.json(); // [{ job_id, filename, status, total_rows, completed_rows, created_at }]
}

// URL for the Excel export, carrying the current filters (opened directly to trigger a download).
export function exportUrl(jobId, { verdict, search, top } = {}) {
  const p = new URLSearchParams();
  if (verdict) p.set("verdict", verdict);
  if (search) p.set("search", search);
  if (top) p.set("top", String(top));
  const qs = p.toString();
  return `${BASE}/results/${jobId}/export${qs ? `?${qs}` : ""}`;
}
