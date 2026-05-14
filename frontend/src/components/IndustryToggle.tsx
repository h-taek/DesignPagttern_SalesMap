import type { Industry } from "../types";

const OPTIONS: { value: Industry; label: string }[] = [
  { value: "food", label: "외식업" },
  { value: "service", label: "서비스업" },
  { value: "retail", label: "소매업" },
];

interface Props {
  value: Industry;
  onChange: (industry: Industry) => void;
}

export function IndustryToggle({ value, onChange }: Props) {
  return (
    <div style={{ display: "flex", gap: 4 }}>
      {OPTIONS.map((opt) => (
        <button
          key={opt.value}
          type="button"
          onClick={() => onChange(opt.value)}
          style={{
            padding: "6px 12px",
            border: `1px solid ${opt.value === value ? "#bef264" : "#ccc"}`,
            borderRadius: 6,
            background: opt.value === value ? "#bef264" : "#f8fafc",
            color: opt.value === value ? "#1a2e05" : "#64748b",
            fontWeight: opt.value === value ? 600 : 400,
            boxShadow: opt.value === value ? "0 2px 4px rgba(163, 230, 53, 0.4)" : "none",
            cursor: "pointer",
            transition: "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
          }}
          onMouseOver={(e) => {
            if (opt.value !== value) e.currentTarget.style.borderColor = "#bef264";
          }}
          onMouseOut={(e) => {
            if (opt.value !== value) e.currentTarget.style.borderColor = "#ccc";
          }}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}
