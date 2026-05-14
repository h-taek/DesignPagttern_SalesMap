import { useState } from "react";

export interface District {
  sggCode: string;
  regionName: string;
  path: string;
  label: [number, number];
}

interface Props {
  districts: District[];
  sggToRegionId: Map<string, number>;
  selectedRegionId: number | null;
  onSelect: (regionId: number) => void;
}

const COLOR_DEFAULT = "#ffffff";
const COLOR_HOVER = "#ecfccb"; // 약한 연두 (lime-100)
const COLOR_SELECTED = "#bef264"; // 조금 더 진한 연두 (lime-300)

export function MapView({
  districts,
  sggToRegionId,
  selectedRegionId,
  onSelect,
}: Props) {
  const [hoveredSgg, setHoveredSgg] = useState<string | null>(null);

  // active(hover/selected)한 구를 뒤에 그려 스케일 시 다른 구에 가려지지 않게
  const ordered = [...districts].sort((a, b) => {
    const aActive =
      a.sggCode === hoveredSgg ||
      sggToRegionId.get(a.sggCode) === selectedRegionId;
    const bActive =
      b.sggCode === hoveredSgg ||
      sggToRegionId.get(b.sggCode) === selectedRegionId;
    return Number(aActive) - Number(bActive);
  });

  return (
    <svg
      viewBox="0 0 1000 831"
      style={{
        width: "100%",
        height: "100%",
        background: "#eef2f7",
        fontFamily:
          '"Noto Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", system-ui, sans-serif',
      }}
      preserveAspectRatio="xMidYMid meet"
    >
      <defs>
        <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur in="SourceAlpha" stdDeviation="5" />
          <feOffset dx="0" dy="4" result="offsetblur" />
          <feComponentTransfer>
            <feFuncA type="linear" slope="0.4" />
          </feComponentTransfer>
          <feMerge>
            <feMergeNode />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      {ordered.map((d) => {
        const regionId = sggToRegionId.get(d.sggCode);
        const selected = regionId != null && regionId === selectedRegionId;
        const hovered = d.sggCode === hoveredSgg;
        const active = selected || hovered;
        const clickable = regionId != null;
        const fill = selected
          ? COLOR_SELECTED
          : hovered
            ? COLOR_HOVER
            : COLOR_DEFAULT;

        return (
          <g
            key={d.sggCode}
            onClick={() => {
              if (regionId != null) onSelect(regionId);
            }}
            onMouseEnter={() => setHoveredSgg(d.sggCode)}
            onMouseLeave={() =>
              setHoveredSgg((s) => (s === d.sggCode ? null : s))
            }
            style={{ cursor: clickable ? "pointer" : "default" }}
          >
            <path
              d={d.path}
              fill={fill}
              fillOpacity={1}
              stroke={active ? "#3f6212" : "#475569"}
              strokeWidth={active ? 2.5 : 1.2}
              strokeLinejoin="round"
              strokeLinecap="round"
              style={{
                // polylabel 좌표(구의 시각적 중심) 기준으로 확대 → 쏠림 없음
                transformBox: "view-box",
                transformOrigin: `${d.label[0]}px ${d.label[1]}px`,
                transform: active ? "scale(1.2)" : "scale(1)",
                transition: "all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)",
                filter: active ? "url(#shadow)" : "none",
              }}
            />
            <text
              x={d.label[0]}
              y={d.label[1]}
              textAnchor="middle"
              dominantBaseline="middle"
              fontSize={active ? 14 : 13}
              fontWeight={active ? 800 : 500}
              fill={selected ? "#1a2e05" : "#334155"}
              style={{
                pointerEvents: "none",
                userSelect: "none",
                // path와 동일한 중심을 써서 글씨도 함께 균등 확대
                transformBox: "view-box",
                transformOrigin: `${d.label[0]}px ${d.label[1]}px`,
                transform: active ? "scale(1.15)" : "scale(1)",
                transition: "all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)",
              }}
            >
              {d.regionName}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
