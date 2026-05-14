import { api } from "./client";
import type { Industry, RegionSales, SalesHistory } from "../types";

export function fetchRegionSales(
  regionId: number,
  industry: Industry,
): Promise<RegionSales> {
  return api<RegionSales>(
    `/api/regions/${regionId}/sales?industry=${industry}`,
  );
}

export function fetchSalesHistory(
  regionId: number,
  industry: Industry,
  quarters = 8,
): Promise<SalesHistory> {
  return api<SalesHistory>(
    `/api/regions/${regionId}/sales/history?industry=${industry}&quarters=${quarters}`,
  );
}
