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
            border: "1px solid #ccc",
            borderRadius: 6,
            background: opt.value === value ? "#2563eb" : "#fff",
            color: opt.value === value ? "#fff" : "#333",
            cursor: "pointer",
          }}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}
