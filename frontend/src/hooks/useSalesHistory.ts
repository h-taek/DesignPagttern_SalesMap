import { useQuery } from "@tanstack/react-query";

import { fetchSalesHistory } from "../api/sales";
import type { Industry } from "../types";

export function useSalesHistory(
  regionId: number | null,
  industry: Industry,
  quarters = 8,
) {
  return useQuery({
    queryKey: ["sales-history", regionId, industry, quarters],
    queryFn: () => fetchSalesHistory(regionId as number, industry, quarters),
    enabled: regionId !== null,
    retry: false,
  });
}
