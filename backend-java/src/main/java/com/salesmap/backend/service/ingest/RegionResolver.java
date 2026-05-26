package com.salesmap.backend.service.ingest;

import com.salesmap.backend.repository.SalesRepository;

import java.util.Map;

/** raw 한 행을 자치구 region_id로 환원. sgg_code → dong_code → trdar_code 우선순위. */
public class RegionResolver {

    private final Map<String, Integer> bySgg;
    private final Map<String, Integer> byDong;
    private final Map<String, Integer> byTrdar;

    public RegionResolver(SalesRepository repo) {
        this.bySgg = repo.listRegionSgg();
        this.byDong = repo.listDongMap();
        this.byTrdar = repo.listTrdarMap();
    }

    public Integer resolve(String sggCode, String dongCode, String trdarCode) {
        if (sggCode != null && bySgg.containsKey(sggCode)) return bySgg.get(sggCode);
        if (dongCode != null && byDong.containsKey(dongCode)) return byDong.get(dongCode);
        if (trdarCode != null && byTrdar.containsKey(trdarCode)) return byTrdar.get(trdarCode);
        return null;
    }
}
