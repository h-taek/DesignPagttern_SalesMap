import { useEffect, useState } from "react";

import { ApiError } from "../api/client";
import { useRegionSales } from "../hooks/useRegionSales";
import { useSalesHistory } from "../hooks/useSalesHistory";
import type { Industry } from "../types";
import { SalesHistoryChart } from "./SalesHistoryChart";
import { SalesSummary } from "./SalesSummary";

interface Props {
  regionId: number;
  industry: Industry;
  onClose: () => void;
}

export function RegionPopup({ regionId, industry, onClose }: Props) {
  const sales = useRegionSales(regionId, industry);
  const history = useSalesHistory(regionId, industry);

  // 마운트 직후 한 프레임 뒤 위로 올라오는 슬라이드업
  const [shown, setShown] = useState(false);
  useEffect(() => {
    const id = requestAnimationFrame(() => setShown(true));
    return () => cancelAnimationFrame(id);
  }, []);

  return (
    <div
      style={{
        position: "fixed",
        left: "50%",
        bottom: 24,
        transform: `translateX(-50%) translateY(${shown ? "0" : "120%"})`,
        transition: "transform 0.32s cubic-bezier(0.4, 0, 0.2, 1)",
        width: 440,
        maxWidth: "92vw",
        background: "#fff",
        borderRadius: 14,
        boxShadow: "0 12px 36px rgba(0,0,0,0.22)",
        padding: 20,
        zIndex: 1000,
        fontFamily: '"Noto Sans KR", sans-serif',
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <strong style={{ fontSize: 16 }}>
          {sales.data?.region.regionName ?? `지역 ${regionId}`}
        </strong>
        <button
          type="button"
          onClick={onClose}
          style={{
            cursor: "pointer",
            border: "none",
            background: "transparent",
            fontSize: 16,
            color: "#888",
          }}
        >
          ✕
        </button>
      </div>

      <div style={{ marginTop: 12 }}>
        {sales.isLoading && <p>불러오는 중…</p>}
        {sales.isError && (
          <p style={{ color: "#c00" }}>
            {sales.error instanceof ApiError && sales.error.code === "NO_SALES_DATA"
              ? "해당 업종 매출 데이터가 없습니다."
              : "매출을 불러오지 못했습니다."}
          </p>
        )}
        {sales.data && <SalesSummary data={sales.data} />}
      </div>

      <div style={{ marginTop: 12 }}>
        {history.data && <SalesHistoryChart series={history.data.series} />}
      </div>
    </div>
  );
}
