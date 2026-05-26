package com.salesmap.ai.core;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "salesmap")
public class Settings {
    private String internalToken = "dev-internal-token";
    private String predictor = "lr";

    public String getInternalToken() { return internalToken; }
    public void setInternalToken(String v) { this.internalToken = v; }

    public String getPredictor() { return predictor; }
    public void setPredictor(String v) { this.predictor = v; }
}
