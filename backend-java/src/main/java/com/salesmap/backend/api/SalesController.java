package com.salesmap.backend.api;

import com.salesmap.backend.dto.IndustryCategory;
import com.salesmap.backend.dto.RegionSalesOut;
import com.salesmap.backend.dto.SalesHistoryOut;
import com.salesmap.backend.service.SalesService;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/regions")
@Validated
public class SalesController {

    private final SalesService service;

    public SalesController(SalesService service) {
        this.service = service;
    }

    @GetMapping("/{regionId}/sales")
    public RegionSalesOut getRegionSales(
        @PathVariable int regionId,
        @RequestParam(defaultValue = "food") IndustryCategory industry
    ) {
        return service.getRegionSales(regionId, industry);
    }

    @GetMapping("/{regionId}/sales/history")
    public SalesHistoryOut getSalesHistory(
        @PathVariable int regionId,
        @RequestParam(defaultValue = "food") IndustryCategory industry,
        @RequestParam(defaultValue = "8") @Min(1) @Max(20) int quarters
    ) {
        return service.getSalesHistory(regionId, industry, quarters);
    }
}
