package com.salesmap.ai.predictor;

import java.util.Map;
import java.util.function.Supplier;

/** Factory Method — 설정값으로 예측 전략 객체 생성. _REGISTRY에 추가하면 호출부 변경 없이 교체 가능. */
public final class PredictorFactory {

    private static final Map<String, Supplier<Predictor>> REGISTRY = Map.of(
        "lr", LinearRegressionPredictor::new
    );

    private PredictorFactory() {}

    public static Predictor create(String name) {
        Supplier<Predictor> s = REGISTRY.get(name == null ? "lr" : name);
        if (s == null) {
            throw new IllegalArgumentException(
                "unknown predictor: " + name + " (available: " + REGISTRY.keySet() + ")");
        }
        return s.get();
    }
}
