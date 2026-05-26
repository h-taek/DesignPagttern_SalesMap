package com.salesmap.backend.core;

import org.springframework.boot.context.properties.ConfigurationProperties;

import java.util.Arrays;
import java.util.List;

@ConfigurationProperties(prefix = "salesmap")
public class Settings {
    private String corsOrigins = "http://localhost:5173";
    private String internalToken = "dev-internal-token";
    private String openApiKey = "";
    private String openApiBase = "http://openapi.seoul.go.kr:8088";

    public String getCorsOrigins() { return corsOrigins; }
    public void setCorsOrigins(String v) { this.corsOrigins = v; }

    public String getInternalToken() { return internalToken; }
    public void setInternalToken(String v) { this.internalToken = v; }

    public String getOpenApiKey() { return openApiKey; }
    public void setOpenApiKey(String v) { this.openApiKey = v; }

    public String getOpenApiBase() { return openApiBase; }
    public void setOpenApiBase(String v) { this.openApiBase = v; }

    public List<String> getCorsOriginList() {
        return Arrays.stream(corsOrigins.split(","))
                .map(String::trim)
                .filter(s -> !s.isEmpty())
                .toList();
    }
}
