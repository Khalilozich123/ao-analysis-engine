// Icon set — drawn SVG, one consistent 1.5 stroke, currentColor. No emoji.
const base = {
  width: 18,
  height: 18,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.5,
  strokeLinecap: "round",
  strokeLinejoin: "round",
};

export const IconLogo = (p) => (
  <svg {...base} {...p}>
    <path d="M12 3l7 4v10l-7 4-7-4V7l7-4z" />
    <path d="M12 8v8M8.5 10v4M15.5 10v4" />
  </svg>
);

export const IconUpload = (p) => (
  <svg {...base} {...p}>
    <path d="M12 15V4m0 0L8 8m4-4l4 4" />
    <path d="M5 15v3a2 2 0 002 2h10a2 2 0 002-2v-3" />
  </svg>
);

export const IconSheet = (p) => (
  <svg {...base} {...p}>
    <path d="M6 3h8l4 4v14a1 1 0 01-1 1H6a1 1 0 01-1-1V4a1 1 0 011-1z" />
    <path d="M14 3v4h4M8 13h8M8 17h8M8 9h3" />
  </svg>
);

export const IconClose = (p) => (
  <svg {...base} {...p}>
    <path d="M6 6l12 12M18 6L6 18" />
  </svg>
);

export const IconExternal = (p) => (
  <svg {...base} {...p}>
    <path d="M14 5h5v5M19 5l-8 8" />
    <path d="M18 14v4a1 1 0 01-1 1H6a1 1 0 01-1-1V7a1 1 0 011-1h4" />
  </svg>
);

export const IconSort = (p) => (
  <svg {...base} {...p}>
    <path d="M8 5v14M8 19l-3-3M8 19l3-3" />
    <path d="M16 19V5M16 5l-3 3M16 5l3 3" opacity="0.4" />
  </svg>
);

export const IconGrid = (p) => (
  <svg {...base} {...p}>
    <path d="M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z" />
  </svg>
);

export const IconSearch = (p) => (
  <svg {...base} {...p}>
    <circle cx="11" cy="11" r="7" />
    <path d="M20 20l-3.5-3.5" />
  </svg>
);

export const IconDownload = (p) => (
  <svg {...base} {...p}>
    <path d="M12 4v11m0 0l-4-4m4 4l4-4" />
    <path d="M5 19h14" />
  </svg>
);

export const IconHistory = (p) => (
  <svg {...base} {...p}>
    <path d="M3 12a9 9 0 109-9 9 9 0 00-7 3.3M3 4v3.5h3.5" />
    <path d="M12 8v4l3 2" />
  </svg>
);
