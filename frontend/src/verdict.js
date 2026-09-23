// Verdict semantics and rubric labels — the single source for colors/labels in the UI.

export const VERDICTS = {
  "Fort intérêt": { color: "#4ade80", rank: 0 },
  "À qualifier": { color: "#fbbf24", rank: 1 },
  "Faible intérêt": { color: "#fb923c", rank: 2 },
  "Non pertinent": { color: "#f87171", rank: 3 },
};

const FALLBACK = { color: "#9a9aa4", rank: 9 };

export function verdictInfo(verdict) {
  return VERDICTS[verdict] || FALLBACK;
}

// hex "#rrggbb" -> "rgba(r,g,b,a)"
export function tint(hex, alpha) {
  const n = parseInt(hex.slice(1), 16);
  const r = (n >> 16) & 255;
  const g = (n >> 8) & 255;
  const b = n & 255;
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

// The 6 rubric criteria, in display order, with French labels and max points.
export const CRITERIA = [
  { key: "alignement_metier", label: "Alignement métier", max: 30 },
  { key: "type_engagement", label: "Type d'engagement", max: 20 },
  { key: "organisme_strategique", label: "Organisme stratégique", max: 15 },
  { key: "domaine_techno", label: "Domaine techno prioritaire", max: 15 },
  { key: "faisabilite_delai", label: "Faisabilité du délai", max: 10 },
  { key: "conditions_favorables", label: "Conditions favorables", max: 10 },
];
