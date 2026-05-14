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
          top: 16,
          left: 16,
          zIndex: 1000,
          background: "#fff",
          padding: 12,
          borderRadius: 8,
          boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
          fontFamily: '"Noto Sans KR", sans-serif',
        }}
      >
        <h3 style={{ margin: "0 0 8px" }}>SalesMap — 서울시 매출·예측</h3>
        <IndustryToggle value={industry} onChange={setIndustry} />
        {regions.isError && (
          <p style={{ color: "#c00", fontSize: 12 }}>
            지역 목록을 불러오지 못했습니다. 백엔드(:8000) 확인.
          </p>
        )}
      </div>

      <MapView
        districts={districts}
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
