package com.salesmap.ai.api;

import com.salesmap.ai.dto.CellError;
import com.salesmap.ai.dto.IndustryCategory;
import com.salesmap.ai.dto.ModelParamsOut;
import com.salesmap.ai.dto.PredictBatchRequest;
import com.salesmap.ai.dto.PredictBatchResponse;
import com.salesmap.ai.dto.PredictSingleRequest;
import com.salesmap.ai.dto.PredictSingleResponse;
import com.salesmap.ai.dto.TrainedOnOut;
import com.salesmap.ai.service.BatchResult;
import com.salesmap.ai.service.CellPrediction;
import com.salesmap.ai.service.PredictionGenerateService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.List;

@RestController
@RequestMapping("/predict")
public class PredictController {

    private final PredictionGenerateService service;

    public PredictController(PredictionGenerateService service) {
        this.service = service;
    }

    @PostMapping("/batch")
    public ResponseEntity<PredictBatchResponse> predictBatch(@Valid @RequestBody PredictBatchRequest body) {
        List<String> industries = body.industries() == null ? null
            : body.industries().stream().map(Enum::name).toList();
        BatchResult result = service.runBatch(body.regionIds(), industries, body.targetQuarter(), body.lookback());

        List<CellError> errors = result.failures().stream()
            .map(f -> new CellError(f.regionId(), f.industry(), f.reason())).toList();

        PredictBatchResponse resp = new PredictBatchResponse(
            result.targetQuarter(),
            result.processed(),
            result.succeeded(),
            result.failed(),
            OffsetDateTime.now(ZoneOffset.UTC),
            errors
        );
        HttpStatus status = result.failed() > 0 ? HttpStatus.MULTI_STATUS : HttpStatus.OK;
        return ResponseEntity.status(status).body(resp);
    }

    @PostMapping("/{regionId}")
    public PredictSingleResponse predictSingle(
        @PathVariable int regionId,
        @Valid @RequestBody PredictSingleRequest body
    ) {
        IndustryCategory industry = body.industryOrDefault();
        CellPrediction cell = service.predictCell(regionId, industry.name(), body.targetQuarter(), body.lookback());

        service.predRepo().save(
            cell.regionId(),
            cell.industry(),
            cell.targetQuarter(),
            cell.predictedSales(),
            cell.previousSales(),
            cell.slope(),
            cell.intercept(),
            cell.samplesUsed()
        );

        return new PredictSingleResponse(
            cell.regionId(),
            industry,
            cell.targetQuarter(),
            cell.predictedSales(),
            new ModelParamsOut(cell.slope(), cell.intercept()),
            new TrainedOnOut(cell.fromQuarter(), cell.toQuarter(), cell.samplesUsed())
        );
    }
}
