// Backend API 응답 타입 — docs/05-api.md 와 1:1.

export type Industry = "food" | "service" | "retail";

export interface Region {
  regionId: number;
  regionName: string;
  sggCode: string;
}

export interface SalesCurrent {
  quarter: string;
  totalSales: number;
  totalCount: number | null;
}

export interface PredictionModel {
  slope: number | null;
  intercept: number | null;
  samplesUsed: number | null;
}

export interface Prediction {
  targetQuarter: string;
  predictedSales: number;
  previousSales: number | null;
  model: PredictionModel;
  generatedAt: string;
}

export interface RegionSales {
  region: Region;
  industry: Industry;
  current: SalesCurrent | null;
  prediction: Prediction | null;
}

export interface SalesHistoryItem {
  quarter: string;
  totalSales: number;
}

export interface SalesHistory {
  regionId: number;
  industry: Industry;
  series: SalesHistoryItem[];
}

export interface ApiErrorBody {
  error: { code: string; message: string };
}
