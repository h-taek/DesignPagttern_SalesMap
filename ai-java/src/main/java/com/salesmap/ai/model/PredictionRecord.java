package com.salesmap.ai.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import org.hibernate.annotations.CreationTimestamp;

import java.time.OffsetDateTime;

@Entity
@Table(name = "prediction_record")
public class PredictionRecord {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "prediction_id")
    private Long predictionId;

    @Column(name = "region_id", nullable = false)
    private Integer regionId;

    @Column(name = "industry_category", nullable = false, length = 10)
    private String industryCategory;

    @Column(name = "target_quarter", nullable = false, length = 6)
    private String targetQuarter;

    @Column(name = "predicted_sales", nullable = false)
    private Long predictedSales;

    @Column(name = "previous_sales")
    private Long previousSales;

    @Column(name = "model_slope")
    private Double modelSlope;

    @Column(name = "model_intercept")
    private Double modelIntercept;

    @Column(name = "samples_used")
    private Integer samplesUsed;

    @CreationTimestamp
    @Column(name = "generated_at", insertable = false, updatable = false)
    private OffsetDateTime generatedAt;

    public PredictionRecord() {}

    public Long getPredictionId() { return predictionId; }
    public void setPredictionId(Long v) { this.predictionId = v; }

    public Integer getRegionId() { return regionId; }
    public void setRegionId(Integer v) { this.regionId = v; }

    public String getIndustryCategory() { return industryCategory; }
    public void setIndustryCategory(String v) { this.industryCategory = v; }

    public String getTargetQuarter() { return targetQuarter; }
    public void setTargetQuarter(String v) { this.targetQuarter = v; }

    public Long getPredictedSales() { return predictedSales; }
    public void setPredictedSales(Long v) { this.predictedSales = v; }

    public Long getPreviousSales() { return previousSales; }
    public void setPreviousSales(Long v) { this.previousSales = v; }

    public Double getModelSlope() { return modelSlope; }
    public void setModelSlope(Double v) { this.modelSlope = v; }

    public Double getModelIntercept() { return modelIntercept; }
    public void setModelIntercept(Double v) { this.modelIntercept = v; }

    public Integer getSamplesUsed() { return samplesUsed; }
    public void setSamplesUsed(Integer v) { this.samplesUsed = v; }

    public OffsetDateTime getGeneratedAt() { return generatedAt; }
}
