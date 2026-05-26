package com.salesmap.backend.dto;

import java.util.List;
import java.util.Map;

public record IngestResponse(
    String source,
    List<String> quarters,
    List<String> industries,
    int processedRows,
    int acceptedRows,
    int upsertedRows,
    int failedRows,
    int dedupedRows,
    int negativeRows,
    List<Map<String, String>> errors
) {}
