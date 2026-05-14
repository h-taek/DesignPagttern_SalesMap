import { useMemo, useState } from "react";

import { IndustryToggle } from "./components/IndustryToggle";
import { MapView } from "./components/MapView";
import type { District } from "./components/MapView";
import { RegionPopup } from "./components/RegionPopup";
import { useRegions } from "./hooks/useRegions";
import type { Industry } from "./types";
import seoulMap from "./assets/seoul-districts.json";

const districts = seoulMap.districts as District[];

export default function App() {
  const [industry, setIndustry] = useState<Industry>("food");
  const [selectedRegionId, setSelectedRegionId] = useState<number | null>(null);
  const regions = useRegions();

  const sggToRegionId = useMemo(() => {
    const m = new Map<string, number>();
    for (const r of regions.data ?? []) m.set(r.sggCode, r.regionId);
    return m;
  }, [regions.data]);

  return (
    <div style={{ position: "relative", height: "100vh", width: "100vw" }}>
      <div
        style={{
          position: "absolute",
          top: 20,
          left: 20,
          zIndex: 1000,
          background: "rgba(255, 255, 255, 0.95)",
          backdropFilter: "blur(8px)",
          padding: "16px 20px",
          borderRadius: 12,
          boxShadow: "0 8px 32px rgba(0,0,0,0.08)",
          fontFamily: '"Noto Sans KR", sans-serif',
          borderLeft: "4px solid #bef264",
        }}
      >
        <h3 style={{ margin: "0 0 12px", color: "#1e293b", fontSize: 18, fontWeight: 700 }}>
          SalesMap <span style={{ fontWeight: 400, fontSize: 14, color: "#64748b", marginLeft: 4 }}>| 서울 상권 분석</span>
        </h3>
        <IndustryToggle value={industry} onChange={setIndustry} />
        {regions.isError && (
          <p style={{ color: "#c00", fontSize: 12 }}>
            지역 목록을 불러오지 못했습니다. 백엔드(:8000) 확인.
          </p>
        )}
      </div>

      <MapView
        districts={districts}
        viewBox={seoulMap.viewBox}
        sggToRegionId={sggToRegionId}
        selectedRegionId={selectedRegionId}
        onSelect={setSelectedRegionId}
      />

      {selectedRegionId !== null && (
        <RegionPopup
          key={selectedRegionId}
          regionId={selectedRegionId}
          industry={industry}
          onClose={() => setSelectedRegionId(null)}
        />
      )}
    </div>
  );
}
