package com.salesmap.ai.predictor;

import java.util.Map;

/** 예측 모델 전략 인터페이스 (Strategy 패턴). x: 분기 인덱스, y: 매출액. */
public interface Predictor {

    void train(int[] x, long[] y);

    double predict(int x);

    Map<String, Double> params();
}
