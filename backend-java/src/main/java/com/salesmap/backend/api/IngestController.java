package com.salesmap.backend.api;

import com.salesmap.backend.core.ApiException;
import com.salesmap.backend.dto.IngestRequest;
import com.salesmap.backend.dto.IngestResponse;
import com.salesmap.backend.service.ingest.IngestResult;
import com.salesmap.backend.service.ingest.SalesIngestService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/ingest")
public class IngestController {

    private final SalesIngestService service;

    public IngestController(SalesIngestService service) {
        this.service = service;
    }

    @PostMapping("/sales")
    public ResponseEntity<IngestResponse> ingestSales(@RequestBody IngestRequest body) {
        IngestResult result;
        try {
            result = service.run(body.quarters(), body.regionIds(), body.industries(), body.source(), null);
        } catch (RuntimeException e) {
            throw new ApiException(HttpStatus.BAD_GATEWAY, "UPSTREAM_API_ERROR", e.getMessage());
        }
        IngestResponse resp = new IngestResponse(
            result.source, result.quarters, result.industries,
            result.processedRows, result.acceptedRows, result.upsertedRows, result.failedRows,
            result.dedupedRows, result.negativeRows, result.errors
        );
        HttpStatus status = result.failedRows > 0 ? HttpStatus.MULTI_STATUS : HttpStatus.OK;
        return ResponseEntity.status(status).body(resp);
    }
}
