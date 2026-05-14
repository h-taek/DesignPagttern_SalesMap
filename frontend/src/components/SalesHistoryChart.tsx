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

export function SalesHistoryChart({ series }: Props) {
  if (series.length === 0) {
    return <p style={{ color: "#888" }}>분기 추이 데이터가 없습니다.</p>;
  }
  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={series} margin={{ top: 8, right: 8, bottom: 8, left: 8 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="quarter" fontSize={11} />
        <YAxis tickFormatter={formatEok} fontSize={11} width={48} />
        <Tooltip
          formatter={(v: number) => [`${v.toLocaleString()}원`, "매출"]}
        />
        <Line
          type="monotone"
          dataKey="totalSales"
          stroke="#2563eb"
          strokeWidth={2}
          dot={{ r: 3 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
