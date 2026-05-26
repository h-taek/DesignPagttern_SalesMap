package com.salesmap.ai.dto;

public record PredictSingleResponse(
    int regionId,
    IndustryCategory industry,
    String targetQuarter,
    long predictedSales,
    ModelParamsOut model,
    TrainedOnOut trainedOn
) {}
