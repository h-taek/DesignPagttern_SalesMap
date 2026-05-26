package com.salesmap.ai.repository;

import com.salesmap.ai.model.SalesRecord;
import org.springframework.data.domain.Limit;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface SalesRecordJpaRepository extends JpaRepository<SalesRecord, Long> {
    List<SalesRecord> findByRegionIdAndIndustryCategoryOrderByQuarterDesc(
        Integer regionId, String industryCategory, Limit limit);
}
