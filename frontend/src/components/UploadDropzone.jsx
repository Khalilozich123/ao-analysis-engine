import { useRef, useState } from "react";
import { IconUpload, IconSheet } from "./icons.jsx";

export default function UploadDropzone({ onFile, busy, error }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const [picked, setPicked] = useState(null);

  function handleFiles(files) {
    const f = files?.[0];
    if (f) {
      setPicked(f);
      onFile(f);
    }
  }

  return (
    <div className="mx-auto max-w-xl">
      <h1 className="text-2xl font-semibold tracking-tight">Analyser un lot d'opportunités</h1>
      <p className="mt-2 text-sm text-text-muted">
        Déposez votre fichier Excel des appels d'offres. Chaque ligne est recherchée puis notée
        (0–100) par le moteur multi-agents, avec un verdict et une justification.
      </p>

      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          handleFiles(e.dataTransfer.files);
        }}
        disabled={busy}
        className={`mt-6 flex w-full flex-col items-center justify-center gap-3 rounded-card border border-dashed px-6 py-14 text-center transition-colors duration-200 disabled:opacity-60 ${
          dragging ? "border-accent bg-accent/5" : "border-border bg-surface hover:border-text-dim"
        }`}
      >
        <span className="text-text-muted">
          <IconUpload width={26} height={26} />
        </span>
        <span className="text-sm font-medium text-text">
          Glissez-déposez un fichier <span className="text-text-muted">.xlsx</span>
        </span>
        <span className="text-xs text-text-dim">ou cliquez pour parcourir</span>
      </button>

      <input
        ref={inputRef}
        type="file"
        accept=".xlsx"
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />

      {picked && !error && (
        <div className="mt-4 flex items-center gap-2.5 rounded-lg border border-border bg-surface px-3 py-2.5 text-sm">
          <span className="text-text-muted">
            <IconSheet width={18} height={18} />
          </span>
          <span className="truncate text-text">{picked.name}</span>
          {busy && <span className="ml-auto text-xs text-text-dim">Téléversement…</span>}
        </div>
      )}

      {error && (
        <div
          className="mt-4 rounded-lg px-3 py-2.5 text-sm"
          style={{ color: "#f87171", backgroundColor: "rgba(248,113,113,0.1)" }}
          role="alert"
        >
          {error}
        </div>
      )}
    </div>
  );
}
