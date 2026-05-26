package com.salesmap.backend.dto;

public record RegionSalesOut(
    RegionOut region,
    IndustryCategory industry,
    SalesCurrentOut current,
    PredictionOut prediction
) {}
