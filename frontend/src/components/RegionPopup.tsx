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

  return (
    <div
      style={{
        position: "absolute",
        top: 16,
        right: 16,
        width: 320,
        background: "#fff",
        borderRadius: 8,
        boxShadow: "0 4px 16px rgba(0,0,0,0.2)",
        padding: 16,
        zIndex: 1000,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <strong>
          {sales.data?.region.regionName ?? `지역 ${regionId}`}
        </strong>
        <button type="button" onClick={onClose} style={{ cursor: "pointer" }}>
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
