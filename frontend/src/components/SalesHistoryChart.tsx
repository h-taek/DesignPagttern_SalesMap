import { useMemo } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { SalesHistoryItem } from "../types";

interface Props {
  series: SalesHistoryItem[];
}

const formatEok = (v: number) => `${Math.round(v / 1e8)}억`;
const formatQuarter = (q: string) => {
  // YYYYQn -> YYYY_n 형식으로 변환 (예: 2024Q4 -> 2024_4)
  if (q.includes("Q")) {
    return q.replace("Q", "_");
  }
  return q;
};

export function SalesHistoryChart({ series }: Props) {
  const chartData = useMemo(() => {
    if (series.length < 2) return series;

    // 분기 순서대로 정렬 (YYYYQn)
    const sorted = [...series].sort((a, b) => a.quarter.localeCompare(b.quarter));
    const filled: SalesHistoryItem[] = [];

    for (let i = 0; i < sorted.length; i++) {
      const curr = sorted[i];
      filled.push(curr);

      if (i < sorted.length - 1) {
        const next = sorted[i + 1];
        // 현재 분기: YYYYQn
        let [y, q] = [
          parseInt(curr.quarter.substring(0, 4)),
          parseInt(curr.quarter.substring(5)),
        ];
        // 다음 데이터 분기
        const [ny, nq] = [
          parseInt(next.quarter.substring(0, 4)),
          parseInt(next.quarter.substring(5)),
        ];

        // 빈 분기 채우기
        // eslint-disable-next-line no-constant-condition
        while (true) {
          q++;
          if (q > 4) {
            q = 1;
            y++;
          }

          if (y > ny || (y === ny && q >= nq)) break;

          filled.push({
            quarter: `${y}Q${q}`,
            totalSales: null as any, // 데이터 없음 표시
          });
        }
      }
    }
    return filled;
  }, [series]);

  if (series.length === 0) {
    return <p style={{ color: "#888" }}>분기 추이 데이터가 없습니다.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart
        data={chartData}
        margin={{ top: 10, right: 10, bottom: 40, left: 0 }}
      >
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        <XAxis
          dataKey="quarter"
          fontSize={10}
          interval={0}
          tickFormatter={formatQuarter}
          tick={{ fill: "#666" }}
          angle={-45}
          textAnchor="end"
          height={50}
          padding={{ left: 10, right: 10 }}
        />
        <YAxis
          tickFormatter={formatEok}
          fontSize={11}
          width={45}
          tick={{ fill: "#666" }}
        />
        <Tooltip
          formatter={(v: number) => [v ? `${v.toLocaleString()}원` : "데이터 없음", "매출"]}
          labelFormatter={formatQuarter}
        />
        <Line
          type="monotone"
          dataKey="totalSales"
          stroke="#84cc16"
          strokeWidth={3}
          dot={{ r: 4, fill: "#84cc16", strokeWidth: 0 }}
          activeDot={{ r: 6, stroke: "#bef264", strokeWidth: 2 }}
          animationDuration={500}
          connectNulls={false} // 끊어진 선으로 표시하여 데이터 부재를 명시함
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

