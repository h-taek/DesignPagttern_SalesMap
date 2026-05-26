package com.salesmap.ai.repository;

import com.salesmap.ai.model.Region;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;

public interface RegionJpaRepository extends JpaRepository<Region, Integer> {
    @Query("SELECT r.regionId FROM Region r ORDER BY r.regionId ASC")
    List<Integer> findAllIdsOrdered();
}
