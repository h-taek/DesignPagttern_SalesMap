package com.salesmap.backend.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

/** 상권코드(OA-15560) → 자치구. OA-15572는 자치구 컬럼 없이 TRDAR_CD만 주므로 필요. */
@Entity
@Table(name = "region_trdar_map")
public class RegionTrdarMap {

    @Id
    @JdbcTypeCode(SqlTypes.CHAR)
    @Column(name = "trdar_code", length = 7)
    private String trdarCode;

    @Column(name = "region_id", nullable = false)
    private Integer regionId;

    public RegionTrdarMap() {}

    public String getTrdarCode() { return trdarCode; }
    public void setTrdarCode(String v) { this.trdarCode = v; }

    public Integer getRegionId() { return regionId; }
    public void setRegionId(Integer v) { this.regionId = v; }
}
