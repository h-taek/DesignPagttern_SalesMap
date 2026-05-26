package com.salesmap.backend.dto;

import java.time.OffsetDateTime;

public record PredictionOut(
    String targetQuarter,
    long predictedSales,
    Long previousSales,
    PredictionModelOut model,
    OffsetDateTime generatedAt
) {}
