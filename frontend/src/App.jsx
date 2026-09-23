import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { exportUrl, getResults, uploadFile } from "./api.js";
import Sidebar from "./components/Sidebar.jsx";
import UploadDropzone from "./components/UploadDropzone.jsx";
import SummaryPanel from "./components/SummaryPanel.jsx";
import FilterBar from "./components/FilterBar.jsx";
import ResultsTable from "./components/ResultsTable.jsx";
import DetailDrawer from "./components/DetailDrawer.jsx";
import HistoryView from "./components/HistoryView.jsx";
import { IconLogo } from "./components/icons.jsx";

const NO_FILTERS = { verdict: null, search: "", top: null };

const TITLES = { upload: "Nouvelle analyse", history: "Historique", results: "Résultats de l'analyse" };

export default function App() {
  const [view, setView] = useState("upload"); // 'upload' | 'history' | 'results'
  const [jobId, setJobId] = useState(null);
  const [job, setJob] = useState(null);
  const [busy, setBusy] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [selected, setSelected] = useState(null);
  const [filters, setFilters] = useState(NO_FILTERS);
  const timer = useRef(null);

  const stopPolling = () => {
    if (timer.current) clearInterval(timer.current);
    timer.current = null;
  };

  const poll = useCallback(async (id) => {
    try {
      const data = await getResults(id);
      setJob(data);
      if (data.status === "done" || data.status === "error") stopPolling();
    } catch {
      /* transient; keep polling */
    }
  }, []);

  const loadJob = useCallback((id) => {
    stopPolling();
    setSelected(null);
    setFilters(NO_FILTERS);
    setJob({ status: "running", total_rows: 0, completed_rows: 0, results: [] });
    setJobId(id);
    setView("results");
  }, []);

  // Deep-link: /?job=<id> opens an existing analysis.
  useEffect(() => {
    const id = new URLSearchParams(window.location.search).get("job");
    if (id) loadJob(id);
  }, [loadJob]);

  useEffect(() => {
    if (!jobId) return;
    poll(jobId);
    timer.current = setInterval(() => poll(jobId), 2500);
    return stopPolling;
  }, [jobId, poll]);

  async function handleFile(file) {
    setBusy(true);
    setUploadError("");
    try {
      const { job_id, total_rows } = await uploadFile(file);
      setJob({ status: "running", total_rows, completed_rows: 0, results: [] });
      setJobId(job_id);
      setView("results");
    } catch (e) {
      setUploadError(e.message || "Échec du téléversement.");
    } finally {
      setBusy(false);
    }
  }

  function newAnalysis() {
    stopPolling();
    setJobId(null);
    setJob(null);
    setSelected(null);
    setUploadError("");
    setFilters(NO_FILTERS);
    setView("upload");
  }

  function handleExport() {
    if (jobId) window.open(exportUrl(jobId, filters), "_blank");
  }

  function navigate(target) {
    if (target === "upload") newAnalysis();
    else setView(target); // 'history'
  }

  const results = job?.results ?? [];
  const pct = job?.total_rows ? Math.round((job.completed_rows / job.total_rows) * 100) : 0;

  const filtered = useMemo(() => {
    let out = [...results].sort((a, b) => b.score - a.score);
    if (filters.verdict) out = out.filter((r) => r.verdict === filters.verdict);
    if (filters.search) {
      const q = filters.search.toLowerCase();
      out = out.filter(
        (r) =>
          (r.title || "").toLowerCase().includes(q) ||
          (r.reference || "").toLowerCase().includes(q) ||
          (r.client || "").toLowerCase().includes(q) ||
          (r.opportunity_id || "").toLowerCase().includes(q),
      );
    }
    if (filters.top) out = out.slice(0, filters.top);
    return out;
  }, [results, filters]);

  const filtersActive = Boolean(filters.verdict || filters.search || filters.top);

  return (
    <div className="flex h-full">
      <Sidebar view={view} onNavigate={navigate} />

      <main className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center gap-3 border-b border-border px-5 py-3.5 md:px-8">
          <span className="text-accent md:hidden">
            <IconLogo width={20} height={20} />
          </span>
          <h1 className="text-sm font-medium text-text-muted">{TITLES[view]}</h1>
          {view === "results" && (
            <button
              type="button"
              onClick={newAnalysis}
              className="ml-auto rounded-lg border border-border bg-surface px-3 py-1.5 text-sm text-text-muted transition-colors hover:border-text-dim hover:text-text"
            >
              Nouvelle analyse
            </button>
          )}
        </header>

        <div className="flex-1 overflow-y-auto px-5 py-8 md:px-8">
          {view === "upload" && <UploadDropzone onFile={handleFile} busy={busy} error={uploadError} />}

          {view === "history" && <HistoryView onOpen={loadJob} />}

          {view === "results" && (
            <div className="mx-auto flex max-w-6xl flex-col gap-5">
              {job?.status === "running" && (
                <div className="card px-5 py-4 animate-fade-up">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-text">Analyse en cours…</span>
                    <span className="nums text-text-muted">
                      {job.completed_rows}/{job.total_rows} · {pct}%
                    </span>
                  </div>
                  <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-elevated">
                    <div
                      className="h-full rounded-full bg-accent transition-[width] duration-500"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              )}

              {job?.status === "error" && (
                <div
                  className="card px-5 py-4 text-sm"
                  style={{ color: "#f87171", borderColor: "rgba(248,113,113,0.3)" }}
                >
                  Une erreur est survenue pendant l'analyse. Les résultats partiels sont affichés ci-dessous.
                </div>
              )}

              <SummaryPanel
                results={results}
                total={job?.total_rows ?? 0}
                completed={job?.completed_rows ?? 0}
                status={job?.status}
              />

              {results.length > 0 && (
                <FilterBar
                  filters={filters}
                  onChange={setFilters}
                  shown={filtered.length}
                  total={results.length}
                  onExport={handleExport}
                />
              )}

              <ResultsTable
                results={filtered}
                total={filtersActive ? filtered.length : job?.total_rows ?? 0}
                status={job?.status}
                onSelect={setSelected}
                selectedId={selected?.opportunity_id}
              />
            </div>
          )}
        </div>
      </main>

      <DetailDrawer result={selected} onClose={() => setSelected(null)} />
    </div>
  );
}
