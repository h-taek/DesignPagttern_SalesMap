package com.salesmap.ai.service;

public record CellPrediction(
    int regionId,
    String industry,
    String targetQuarter,
    long predictedSales,
    Long previousSales,
    Double slope,
    Double intercept,
    int samplesUsed,
    String fromQuarter,
    String toQuarter
) {}
