package com.salesmap.backend.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "region_dong_map")
public class RegionDongMap {

    @Id
    @Column(name = "dong_code", length = 10)
    private String dongCode;

    @Column(name = "dong_name", nullable = false, length = 40)
    private String dongName;

    @Column(name = "region_id", nullable = false)
    private Integer regionId;

    public RegionDongMap() {}

    public String getDongCode() { return dongCode; }
    public void setDongCode(String v) { this.dongCode = v; }

    public String getDongName() { return dongName; }
    public void setDongName(String v) { this.dongName = v; }

    public Integer getRegionId() { return regionId; }
    public void setRegionId(Integer v) { this.regionId = v; }
}
