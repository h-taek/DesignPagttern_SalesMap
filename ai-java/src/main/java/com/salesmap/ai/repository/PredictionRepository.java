package com.salesmap.ai.repository;

import com.salesmap.ai.model.PredictionRecord;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

/** 예측 결과를 새 row로 누적 저장(이력 보존). 사용자 조회는 generated_at DESC LIMIT 1. */
@Repository
public class PredictionRepository {

    private final PredictionRecordJpaRepository repo;

    public PredictionRepository(PredictionRecordJpaRepository repo) {
        this.repo = repo;
    }

    @Transactional
    public PredictionRecord save(
        int regionId,
        String industry,
        String targetQuarter,
        long predictedSales,
        Long previousSales,
        Double modelSlope,
        Double modelIntercept,
        int samplesUsed
    ) {
        PredictionRecord row = new PredictionRecord();
        row.setRegionId(regionId);
        row.setIndustryCategory(industry);
        row.setTargetQuarter(targetQuarter);
        row.setPredictedSales(predictedSales);
        row.setPreviousSales(previousSales);
        row.setModelSlope(modelSlope);
        row.setModelIntercept(modelIntercept);
        row.setSamplesUsed(samplesUsed);
        return repo.save(row);
    }
}
