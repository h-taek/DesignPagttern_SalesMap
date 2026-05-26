package com.salesmap.ai.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;

public record PredictSingleRequest(
    IndustryCategory industry,
    String targetQuarter,
    @Min(2) @Max(40) Integer lookbackQuarters
) {
    public IndustryCategory industryOrDefault() { return industry == null ? IndustryCategory.food : industry; }
    public int lookback() { return lookbackQuarters == null ? 16 : lookbackQuarters; }
}
