package com.salesmap.ai.dto;

import java.time.OffsetDateTime;
import java.util.List;

public record PredictBatchResponse(
    String targetQuarter,
    int processedCells,
    int succeededCells,
    int failedCells,
    OffsetDateTime generatedAt,
    List<CellError> errors
) {}
