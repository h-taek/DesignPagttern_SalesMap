package com.salesmap.backend.repository;

import com.salesmap.backend.model.PredictionRecord;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public class PredictionRepository {

    private final PredictionRecordJpaRepository repo;

    public PredictionRepository(PredictionRecordJpaRepository repo) {
        this.repo = repo;
    }

    public Optional<PredictionRecord> findLatest(int regionId, String industry) {
        return repo.findFirstByRegionIdAndIndustryCategoryOrderByTargetQuarterDescGeneratedAtDesc(regionId, industry);
    }
}
