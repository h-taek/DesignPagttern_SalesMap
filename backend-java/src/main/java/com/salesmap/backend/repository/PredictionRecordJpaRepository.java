package com.salesmap.backend.repository;

import com.salesmap.backend.model.PredictionRecord;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface PredictionRecordJpaRepository extends JpaRepository<PredictionRecord, Long> {
    Optional<PredictionRecord> findFirstByRegionIdAndIndustryCategoryOrderByTargetQuarterDescGeneratedAtDesc(
        Integer regionId, String industryCategory
    );
}
