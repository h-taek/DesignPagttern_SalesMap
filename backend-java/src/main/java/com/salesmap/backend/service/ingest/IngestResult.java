package com.salesmap.backend.service.ingest;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class IngestResult {
    public String source;
    public List<String> quarters = new ArrayList<>();
    public List<String> industries = new ArrayList<>();
    public int processedRows;
    public int acceptedRows;
    public int upsertedRows;
    public int failedRows;
    public int dedupedRows;
    public int negativeRows;
    public List<Map<String, String>> errors = new ArrayList<>();
}
