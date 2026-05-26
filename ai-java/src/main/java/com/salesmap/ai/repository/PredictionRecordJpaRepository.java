package com.salesmap.ai.repository;

import com.salesmap.ai.model.PredictionRecord;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PredictionRecordJpaRepository extends JpaRepository<PredictionRecord, Long> {
}
