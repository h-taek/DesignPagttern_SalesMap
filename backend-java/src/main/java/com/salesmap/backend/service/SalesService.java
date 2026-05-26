package com.salesmap.backend.service;

import com.salesmap.backend.core.ApiException;
import com.salesmap.backend.dto.IndustryCategory;
import com.salesmap.backend.dto.PredictionModelOut;
import com.salesmap.backend.dto.PredictionOut;
import com.salesmap.backend.dto.RegionOut;
import com.salesmap.backend.dto.RegionSalesOut;
import com.salesmap.backend.dto.SalesCurrentOut;
import com.salesmap.backend.dto.SalesHistoryItem;
import com.salesmap.backend.dto.SalesHistoryOut;
import com.salesmap.backend.model.PredictionRecord;
import com.salesmap.backend.model.Region;
import com.salesmap.backend.model.SalesRecord;
import com.salesmap.backend.repository.PredictionRepository;
import com.salesmap.backend.repository.SalesRepository;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@Transactional(readOnly = true)
public class SalesService {

    private final SalesRepository sales;
    private final PredictionRepository predictions;

    public SalesService(SalesRepository sales, PredictionRepository predictions) {
        this.sales = sales;
        this.predictions = predictions;
    }

    public List<RegionOut> listRegions() {
        return sales.listRegions().stream().map(SalesService::toRegionOut).toList();
    }

    public RegionSalesOut getRegionSales(int regionId, IndustryCategory industry) {
        Region region = sales.findRegion(regionId)
            .orElseThrow(() -> new ApiException(HttpStatus.NOT_FOUND, "REGION_NOT_FOUND",
                "regionId=" + regionId + " not found"));

        SalesRecord latest = sales.findLatest(regionId, industry.name())
            .orElseThrow(() -> new ApiException(HttpStatus.UNPROCESSABLE_ENTITY, "NO_SALES_DATA",
                "no sales for region=" + regionId + " industry=" + industry.name()));

        Optional<PredictionRecord> predOpt = predictions.findLatest(regionId, industry.name());
        PredictionOut predictionOut = predOpt.map(p -> new PredictionOut(
            p.getTargetQuarter(),
            p.getPredictedSales(),
            p.getPreviousSales(),
            new PredictionModelOut(p.getModelSlope(), p.getModelIntercept(), p.getSamplesUsed()),
            p.getGeneratedAt()
        )).orElse(null);

        return new RegionSalesOut(
            toRegionOut(region),
            industry,
            new SalesCurrentOut(latest.getQuarter(), latest.getTotalSales(), latest.getTotalCount()),
            predictionOut
        );
    }

    public SalesHistoryOut getSalesHistory(int regionId, IndustryCategory industry, int quarters) {
        if (sales.findRegion(regionId).isEmpty()) {
            throw new ApiException(HttpStatus.NOT_FOUND, "REGION_NOT_FOUND",
                "regionId=" + regionId + " not found");
        }
        List<SalesHistoryItem> series = sales.findQuarters(regionId, industry.name(), quarters).stream()
            .map(r -> new SalesHistoryItem(r.getQuarter(), r.getTotalSales()))
            .toList();
        return new SalesHistoryOut(regionId, industry, series);
    }

    private static RegionOut toRegionOut(Region r) {
        return new RegionOut(r.getRegionId(), r.getRegionName(), r.getSggCode());
    }
}
