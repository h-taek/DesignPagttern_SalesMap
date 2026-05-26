package com.salesmap.ai.dto;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;

public enum IndustryCategory {
    food, service, retail;

    @JsonValue
    public String value() { return name(); }

    @JsonCreator
    public static IndustryCategory from(String s) {
        if (s == null) return null;
        return IndustryCategory.valueOf(s);
    }
}
