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

  const isActive = (d: District) =>
    d.sggCode === hoveredSgg ||
    sggToRegionId.get(d.sggCode) === selectedRegionId;

  // 레이어 분리: 비활성 path → 비활성 text → 활성(path+text) 최상단.
  // 텍스트를 path 위 레이어에 둬서 인접 구 경계선에 가려지지 않게 하고,
  // hover/선택된 구는 그보다 위에 그려 확대 시 라벨에 가리지 않게 한다.
  const inactive = districts.filter((d) => !isActive(d));
  const active = districts.filter(isActive);

  const handlers = (d: District) => {
    const regionId = sggToRegionId.get(d.sggCode);
    return {
      onClick: () => {
        if (regionId != null) onSelect(regionId);
      },
      onMouseEnter: () => setHoveredSgg(d.sggCode),
      onMouseLeave: () =>
        setHoveredSgg((s) => (s === d.sggCode ? null : s)),
      style: { cursor: regionId != null ? "pointer" : "default" },
    };
  };

  const renderPath = (d: District, activeState: boolean) => {
    const regionId = sggToRegionId.get(d.sggCode);
    const selected = regionId != null && regionId === selectedRegionId;
    const fill = selected
      ? COLOR_SELECTED
      : d.sggCode === hoveredSgg
        ? COLOR_HOVER
        : COLOR_DEFAULT;
    return (
      <path
        d={d.path}
        fill={fill}
        stroke={activeState ? "#4d7c0f" : "#94a3b8"}
        strokeWidth={activeState ? 2.8 : 1.2}
        strokeLinejoin="round"
        strokeLinecap="round"
        style={{
          transformBox: "view-box",
          transformOrigin: `${d.label[0]}px ${d.label[1]}px`,
          transform: activeState ? "scale(1.1)" : "scale(1)",
          transition: "all 0.4s cubic-bezier(0.23, 1, 0.32, 1)",
          filter: activeState ? "url(#shadow)" : "none",
        }}
      />
    );
  };

  const renderText = (d: District, activeState: boolean) => {
    const regionId = sggToRegionId.get(d.sggCode);
    const selected = regionId != null && regionId === selectedRegionId;
    return (
      <text
        x={d.label[0]}
        y={d.label[1]}
        textAnchor="middle"
        dominantBaseline="middle"
        fontSize={activeState ? 15 : 13}
        fontWeight={activeState ? 700 : 500}
        fill={selected ? "#1a2e05" : "#334155"}
        style={{
          pointerEvents: "none",
          userSelect: "none",
          transformBox: "view-box",
          transformOrigin: `${d.label[0]}px ${d.label[1]}px`,
          transform: activeState ? "scale(1.1)" : "scale(1)",
          transition: "all 0.4s cubic-bezier(0.23, 1, 0.32, 1)",
          textShadow: activeState ? "0 0 8px rgba(255,255,255,0.8)" : "none",
        }}
      >
        {d.regionName}
      </text>
    );
  };

  return (
    <svg
      viewBox={viewBox}
      style={{
        width: "100%",
        height: "100%",
        background: "#f8fafc",
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
      </defs>

      {/* Layer 1 — 비활성 구 경계 path */}
      {inactive.map((d) => (
        <g key={d.sggCode} {...handlers(d)}>
          {renderPath(d, false)}
        </g>
      ))}

      {/* Layer 2 — 비활성 구 텍스트 라벨 (모든 path 위, 경계선에 안 가림) */}
      {inactive.map((d) => (
        <g key={`label-${d.sggCode}`}>{renderText(d, false)}</g>
      ))}

      {/* Layer 3 — 활성(hover/선택) 구: path+text 최상단 */}
      {active.map((d) => (
        <g key={d.sggCode} {...handlers(d)}>
          {renderPath(d, true)}
          {renderText(d, true)}
        </g>
      ))}
    </svg>
  );
}
