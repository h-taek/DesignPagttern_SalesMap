import { useState } from "react";

export interface District {
  sggCode: string;
  regionName: string;
  path: string;
  label: [number, number];
}

interface Props {
  districts: District[];
  viewBox: string;
  sggToRegionId: Map<string, number>;
  selectedRegionId: number | null;
  onSelect: (regionId: number) => void;
}

const COLOR_DEFAULT = "#ffffff";
const COLOR_HOVER = "#ecfccb"; // lime-100
const COLOR_SELECTED = "#bef264"; // lime-300

export function MapView({
  districts,
  viewBox,
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
      viewBox={viewBox}
      style={{
        width: "100%",
        height: "100%",
        background: "#f8fafc", // 조금 더 밝은 배경
        fontFamily:
          '"Noto Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", system-ui, sans-serif',
      }}
      preserveAspectRatio="xMidYMid meet"
    >
      <defs>
        <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur in="SourceAlpha" stdDeviation="6" />
          <feOffset dx="0" dy="6" result="offsetblur" />
          <feComponentTransfer>
            <feFuncA type="linear" slope="0.3" />
          </feComponentTransfer>
          <feMerge>
            <feMergeNode />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
        {/* 외곽선을 더 단순하고 부드럽게 만드는 SVG 필터 (Gooey effect) */}
        <filter id="smooth-edge" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur in="SourceGraphic" stdDeviation="2.2" result="blur" />
          <feColorMatrix
            in="blur"
            mode="matrix"
            values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 30 -12"
            result="smooth"
          />
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
              stroke={active ? "#4d7c0f" : "#64748b"}
              strokeWidth={active ? 2.8 : 1.2}
              strokeLinejoin="round"
              strokeLinecap="round"
              style={{
                transformBox: "view-box",
                transformOrigin: `${d.label[0]}px ${d.label[1]}px`,
                transform: active ? "scale(1.1)" : "scale(1)", // 1.2는 너무 커서 1.1로 조정
                transition: "all 0.4s cubic-bezier(0.23, 1, 0.32, 1)",
                filter: active ? "url(#shadow) url(#smooth-edge)" : "url(#smooth-edge)",
              }}
            />
            <text
              x={d.label[0]}
              y={d.label[1]}
              textAnchor="middle"
              dominantBaseline="middle"
              fontSize={active ? 15 : 13}
              fontWeight={active ? 700 : 500}
              fill={selected ? "#1a2e05" : "#334155"}
              style={{
                pointerEvents: "none",
                userSelect: "none",
                transformBox: "view-box",
                transformOrigin: `${d.label[0]}px ${d.label[1]}px`,
                transform: active ? "scale(1.1)" : "scale(1)",
                transition: "all 0.4s cubic-bezier(0.23, 1, 0.32, 1)",
                textShadow: active ? "0 0 8px rgba(255,255,255,0.8)" : "none",
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
