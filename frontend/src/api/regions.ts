import { api } from "./client";
import type { Region } from "../types";

export function fetchRegions(): Promise<Region[]> {
  return api<Region[]>("/api/regions");
}
