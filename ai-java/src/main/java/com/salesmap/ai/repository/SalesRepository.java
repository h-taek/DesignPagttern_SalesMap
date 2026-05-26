package com.salesmap.ai.repository;

import com.salesmap.ai.model.SalesRecord;
import org.springframework.data.domain.Limit;
import org.springframework.stereotype.Repository;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

@Repository
public class SalesRepository {

    private final RegionJpaRepository regionRepo;
    private final SalesRecordJpaRepository salesRepo;

    public SalesRepository(RegionJpaRepository regionRepo, SalesRecordJpaRepository salesRepo) {
        this.regionRepo = regionRepo;
        this.salesRepo = salesRepo;
    }

    public List<Integer> listRegionIds() {
        return regionRepo.findAllIdsOrdered();
    }

    /** 최근 lookback개 분기를 오래된 순으로 반환. */
    public List<SalesRecord> findQuarters(int regionId, String industry, int lookback) {
        List<SalesRecord> rows = new ArrayList<>(
            salesRepo.findByRegionIdAndIndustryCategoryOrderByQuarterDesc(regionId, industry, Limit.of(lookback))
        );
        Collections.reverse(rows);
        return rows;
    }
}
