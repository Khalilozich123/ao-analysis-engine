import { useEffect, useState } from "react";
import { listJobs } from "../api.js";
import { IconSheet } from "./icons.jsx";

const STATUS = {
  done: { label: "Terminé", color: "#4ade80" },
  running: { label: "En cours", color: "#7c83ff" },
  pending: { label: "En attente", color: "#9a9aa4" },
  error: { label: "Erreur", color: "#f87171" },
};

function fmtDate(iso) {
  try {
    return new Date(iso).toLocaleString("fr-FR", { dateStyle: "medium", timeStyle: "short" });
  } catch {
    return iso;
  }
}

export default function HistoryView({ onOpen }) {
  const [jobs, setJobs] = useState(null); // null = loading
  const [error, setError] = useState("");

  useEffect(() => {
    listJobs()
      .then(setJobs)
      .catch((e) => setError(e.message));
  }, []);

  return (
    <div className="mx-auto max-w-4xl">
      <h1 className="text-2xl font-semibold tracking-tight">Historique des analyses</h1>
      <p className="mt-2 text-sm text-text-muted">
        Rouvrez n'importe quelle analyse passée avec l'ensemble de ses résultats.
      </p>

      {error && (
        <div className="mt-6 card px-4 py-3 text-sm" style={{ color: "#f87171" }} role="alert">
          {error}
        </div>
      )}

      {jobs === null && !error && (
        <div className="mt-6 flex flex-col gap-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="card px-4 py-4">
              <span className="skeleton block h-4 w-1/3 rounded" />
              <span className="skeleton mt-2 block h-3 w-1/4 rounded" />
            </div>
          ))}
        </div>
      )}

      {jobs && jobs.length === 0 && (
        <div className="mt-6 card flex flex-col items-center justify-center px-6 py-16 text-center">
          <p className="text-sm font-medium text-text">Aucune analyse pour le moment</p>
          <p className="mt-1 text-xs text-text-dim">Lancez une première analyse depuis « Nouvelle analyse ».</p>
        </div>
      )}

      {jobs && jobs.length > 0 && (
        <ul className="mt-6 flex flex-col gap-2">
          {jobs.map((j) => {
            const st = STATUS[j.status] || STATUS.pending;
            return (
              <li key={j.job_id}>
                <button
                  type="button"
                  onClick={() => onOpen(j.job_id)}
                  className="card flex w-full items-center gap-4 px-4 py-3.5 text-left transition-colors hover:border-text-dim"
                >
                  <span className="text-text-dim">
                    <IconSheet width={20} height={20} />
                  </span>
                  <div className="min-w-0 flex-1">
                    <div className="truncate text-sm font-medium text-text">{j.filename}</div>
                    <div className="mt-0.5 text-xs text-text-dim">{fmtDate(j.created_at)}</div>
                  </div>
                  <span className="nums text-sm text-text-muted">
                    {j.completed_rows}/{j.total_rows}
                  </span>
                  <span
                    className="rounded-full px-2.5 py-1 text-xs font-medium"
                    style={{ color: st.color, backgroundColor: `${st.color}1f` }}
                  >
                    {st.label}
                  </span>
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
