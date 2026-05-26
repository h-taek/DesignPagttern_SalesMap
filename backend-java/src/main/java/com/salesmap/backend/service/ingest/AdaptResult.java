package com.salesmap.backend.service.ingest;

/** 성공이면 row != null, 실패면 reason != null. (Python: tuple union 동등물) */
public record AdaptResult(NormalizedRow row, String reason) {
    public static AdaptResult ok(NormalizedRow row) { return new AdaptResult(row, null); }
    public static AdaptResult fail(String reason) { return new AdaptResult(null, reason); }
    public boolean isOk() { return row != null; }
}
