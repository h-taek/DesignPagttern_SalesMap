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
          <div style={{ fontSize: 20, color: "#2563eb" }}>
            {won(prediction.predictedSales)}
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
