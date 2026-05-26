package com.salesmap.ai.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import org.hibernate.annotations.CreationTimestamp;

import java.time.OffsetDateTime;

@Entity
@Table(
    name = "sales_record",
    uniqueConstraints = @UniqueConstraint(
        name = "uq_sales_region_quarter_industry",
        columnNames = {"region_id", "quarter", "industry_category"}
    )
)
public class SalesRecord {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "sales_id")
    private Long salesId;

    @Column(name = "region_id", nullable = false)
    private Integer regionId;

    @Column(name = "quarter", nullable = false, length = 6)
    private String quarter;

    @Column(name = "industry_category", nullable = false, length = 10)
    private String industryCategory;

    @Column(name = "total_sales", nullable = false)
    private Long totalSales;

    @Column(name = "total_count")
    private Long totalCount;

    @CreationTimestamp
    @Column(name = "created_at", insertable = false, updatable = false)
    private OffsetDateTime createdAt;

    public SalesRecord() {}

    public Long getSalesId() { return salesId; }
    public void setSalesId(Long v) { this.salesId = v; }

    public Integer getRegionId() { return regionId; }
    public void setRegionId(Integer v) { this.regionId = v; }

    public String getQuarter() { return quarter; }
    public void setQuarter(String v) { this.quarter = v; }

    public String getIndustryCategory() { return industryCategory; }
    public void setIndustryCategory(String v) { this.industryCategory = v; }

    public Long getTotalSales() { return totalSales; }
    public void setTotalSales(Long v) { this.totalSales = v; }

    public Long getTotalCount() { return totalCount; }
    public void setTotalCount(Long v) { this.totalCount = v; }

    public OffsetDateTime getCreatedAt() { return createdAt; }
}
