package com.salesmap.ai.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "region")
public class Region {

    @Id
    @Column(name = "region_id")
    private Integer regionId;

    @Column(name = "region_name", nullable = false, length = 20)
    private String regionName;

    @Column(name = "sgg_code", nullable = false, unique = true, length = 5)
    private String sggCode;

    public Region() {}

    public Integer getRegionId() { return regionId; }
    public void setRegionId(Integer v) { this.regionId = v; }

    public String getRegionName() { return regionName; }
    public void setRegionName(String v) { this.regionName = v; }

    public String getSggCode() { return sggCode; }
    public void setSggCode(String v) { this.sggCode = v; }
}
