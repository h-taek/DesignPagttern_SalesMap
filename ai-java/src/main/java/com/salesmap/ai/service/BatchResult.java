package com.salesmap.ai.service;

import java.util.List;

public record BatchResult(
    String targetQuarter,
    int processed,
    int succeeded,
    int failed,
    List<CellFailure> failures
) {}
