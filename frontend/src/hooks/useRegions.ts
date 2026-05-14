import { useQuery } from "@tanstack/react-query";

import { fetchRegions } from "../api/regions";

export function useRegions() {
  return useQuery({
    queryKey: ["regions"],
    queryFn: fetchRegions,
  });
}
