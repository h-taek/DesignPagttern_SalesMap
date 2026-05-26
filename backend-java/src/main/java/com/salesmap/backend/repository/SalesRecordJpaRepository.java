package com.salesmap.backend.repository;

import com.salesmap.backend.model.SalesRecord;
import org.springframework.data.domain.Limit;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface SalesRecordJpaRepository extends JpaRepository<SalesRecord, Long> {

    Optional<SalesRecord> findFirstByRegionIdAndIndustryCategoryOrderByQuarterDesc(
        Integer regionId, String industryCategory
    );

    List<SalesRecord> findByRegionIdAndIndustryCategoryOrderByQuarterDesc(
        Integer regionId, String industryCategory, Limit limit
    );
}
