package com.salesmap.backend.repository;

import com.salesmap.backend.model.Region;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface RegionRepository extends JpaRepository<Region, Integer> {
    List<Region> findAllByOrderByRegionIdAsc();
}
