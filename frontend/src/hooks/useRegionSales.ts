import { useQuery } from "@tanstack/react-query";

import { fetchRegionSales } from "../api/sales";
import type { Industry } from "../types";

export function useRegionSales(regionId: number | null, industry: Industry) {
  return useQuery({
    queryKey: ["region-sales", regionId, industry],
    queryFn: () => fetchRegionSales(regionId as number, industry),
    enabled: regionId !== null,
    retry: false,
  });
}
