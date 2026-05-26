package com.salesmap.backend.api;

import com.salesmap.backend.dto.RegionOut;
import com.salesmap.backend.service.SalesService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/regions")
public class RegionsController {

    private final SalesService service;

    public RegionsController(SalesService service) {
        this.service = service;
    }

    @GetMapping
    public List<RegionOut> listRegions() {
        return service.listRegions();
    }
}
