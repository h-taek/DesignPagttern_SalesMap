package com.salesmap.backend.dto;

import java.util.List;

public record IngestRequest(
    List<Integer> regionIds,
    List<String> quarters,
    List<IndustryCategory> industries,
    String source
) {
    public IngestRequest {
        if (source == null || source.isBlank()) source = "OA-15572";
    }
}
