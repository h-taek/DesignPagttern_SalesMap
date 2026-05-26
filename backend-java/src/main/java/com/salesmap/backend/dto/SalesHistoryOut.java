package com.salesmap.backend.dto;

import java.util.List;

public record SalesHistoryOut(int regionId, IndustryCategory industry, List<SalesHistoryItem> series) {}
