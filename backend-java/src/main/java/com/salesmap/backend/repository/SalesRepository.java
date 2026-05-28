package com.salesmap.backend.repository;

import com.salesmap.backend.model.Region;
import com.salesmap.backend.model.RegionDongMap;
import com.salesmap.backend.model.RegionTrdarMap;
import com.salesmap.backend.model.SalesRecord;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Limit;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/** Python SalesRepository와 동일한 책임. JPA + UPSERT는 JdbcTemplate. */
@Repository
public class SalesRepository {

    private final RegionRepository regionRepo;
    private final SalesRecordJpaRepository salesRepo;
    private final RegionDongMapRepository dongRepo;
    private final RegionTrdarMapRepository trdarRepo;
    private final JdbcTemplate jdbc;

    @Autowired
    public SalesRepository(RegionRepository regionRepo,
                           SalesRecordJpaRepository salesRepo,
                           RegionDongMapRepository dongRepo,
                           RegionTrdarMapRepository trdarRepo,
                           JdbcTemplate jdbc) {
        this.regionRepo = regionRepo;
        this.salesRepo = salesRepo;
        this.dongRepo = dongRepo;
        this.trdarRepo = trdarRepo;
        this.jdbc = jdbc;
    }

    public List<Region> listRegions() {
        return regionRepo.findAllByOrderByRegionIdAsc();
    }

    public Optional<Region> findRegion(int regionId) {
        return regionRepo.findById(regionId);
    }

    public Optional<SalesRecord> findLatest(int regionId, String industry) {
        return salesRepo.findFirstByRegionIdAndIndustryCategoryOrderByQuarterDesc(regionId, industry);
    }

    /** 오래된 분기 → 최신 순으로 n개. (Python: desc limit + reverse) */
    public List<SalesRecord> findQuarters(int regionId, String industry, int n) {
        List<SalesRecord> rows = new ArrayList<>(
            salesRepo.findByRegionIdAndIndustryCategoryOrderByQuarterDesc(regionId, industry, Limit.of(n))
        );
        Collections.reverse(rows);
        return rows;
    }

    /** ON CONFLICT (region_id, quarter, industry_category) DO UPDATE — Postgres 네이티브. */
    public int upsertMany(List<SalesRow> rows) {
        if (rows.isEmpty()) return 0;
        String sql = """
            INSERT INTO sales_record (region_id, quarter, industry_category, total_sales, total_count)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT (region_id, quarter, industry_category)
            DO UPDATE SET total_sales = EXCLUDED.total_sales,
                          total_count = EXCLUDED.total_count
            """;
        int[][] result = jdbc.batchUpdate(sql, rows, rows.size(), (ps, r) -> {
            ps.setInt(1, r.regionId());
            ps.setString(2, r.quarter());
            ps.setString(3, r.industryCategory());
            ps.setLong(4, r.totalSales());
            if (r.totalCount() == null) ps.setNull(5, java.sql.Types.BIGINT);
            else ps.setLong(5, r.totalCount());
        });
        int sum = 0;
        for (int[] batch : result) for (int n : batch) sum += Math.max(n, 0);
        return sum > 0 ? sum : rows.size();
    }

    public Map<String, Integer> listRegionSgg() {
        Map<String, Integer> m = new HashMap<>();
        for (Region r : regionRepo.findAll()) m.put(r.getSggCode(), r.getRegionId());
        return m;
    }

    public Map<String, Integer> listDongMap() {
        Map<String, Integer> m = new HashMap<>();
        for (RegionDongMap r : dongRepo.findAll()) m.put(r.getDongCode(), r.getRegionId());
        return m;
    }

    public Map<String, Integer> listTrdarMap() {
        Map<String, Integer> m = new HashMap<>();
        for (RegionTrdarMap r : trdarRepo.findAll()) m.put(r.getTrdarCode().strip(), r.getRegionId());
        return m;
    }

    public record SalesRow(
        int regionId,
        String quarter,
        String industryCategory,
        long totalSales,
        Long totalCount
    ) {}
}
