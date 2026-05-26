package com.salesmap.ai.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;

import java.util.List;

public record PredictBatchRequest(
    List<Integer> regionIds,
    List<IndustryCategory> industries,
    String targetQuarter,
    @Min(2) @Max(40) Integer lookbackQuarters
) {
    public int lookback() { return lookbackQuarters == null ? 16 : lookbackQuarters; }
}
