package com.salesmap.backend.service.ingest;

import com.salesmap.backend.dto.IndustryCategory;

public record NormalizedRow(
    int regionId,
    String quarter,
    IndustryCategory industry,
    long totalSales,
    Long totalCount
) {}
