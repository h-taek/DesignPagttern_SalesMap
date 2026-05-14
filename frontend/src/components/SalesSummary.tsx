import type { RegionSales } from "../types";

interface Props {
  data: RegionSales;
}

const won = (v: number) => `${v.toLocaleString()}원`;

export function SalesSummary({ data }: Props) {
  const { current, prediction } = data;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      {current && (
        <div>
          <strong>{current.quarter} 매출</strong>
          <div style={{ fontSize: 20 }}>{won(current.totalSales)}</div>
          {current.totalCount != null && (
            <div style={{ color: "#888", fontSize: 12 }}>
              결제 {current.totalCount.toLocaleString()}건
            </div>
          )}
        </div>
      )}
      {prediction ? (
        <div>
          <strong>{prediction.targetQuarter} 예측</strong>
          <div style={{ fontSize: 20, color: "#65a30d" }}>
            {won(prediction.predictedSales)}
            {(() => {
              const prev = prediction.previousSales ?? current?.totalSales;
              if (prev == null || prev === 0) return null;
              const pct = ((prediction.predictedSales - prev) / prev) * 100;
              const absPct = Math.abs(pct);
              if (absPct < 0.1) return null;

              const isUp = pct > 0;
              return (
                <span
                  style={{
                    fontSize: 14,
                    marginLeft: 6,
                    fontWeight: "bold",
                    color: isUp ? "#dc2626" : "#2563eb",
                  }}
                >
                  ({isUp ? "▲" : "▼"} {absPct.toFixed(1)}%)
                </span>
              );
            })()}
          </div>
          <div style={{ color: "#888", fontSize: 12 }}>
            학습 표본 {prediction.model.samplesUsed ?? "-"}분기
          </div>
        </div>
      ) : (
        <div style={{ color: "#888" }}>예측 데이터가 아직 없습니다.</div>
      )}
    </div>
  );
}
