package com.salesmap.ai.predictor;

import org.apache.commons.math3.stat.regression.SimpleRegression;

import java.util.HashMap;
import java.util.Map;

/** 단순 선형회귀 (Apache Commons Math). Strategy 구현체. */
public class LinearRegressionPredictor implements Predictor {

    public static final int MIN_SAMPLES = 2;

    private final SimpleRegression model = new SimpleRegression(true);
    private boolean fitted = false;

    @Override
    public void train(int[] x, long[] y) {
        if (x.length < MIN_SAMPLES || x.length != y.length) {
            throw new NotEnoughDataException(
                "need >= " + MIN_SAMPLES + " samples, got " + x.length);
        }
        for (int i = 0; i < x.length; i++) {
            model.addData((double) x[i], (double) y[i]);
        }
        fitted = true;
    }

    @Override
    public double predict(int x) {
        if (!fitted) throw new IllegalStateException("model not trained");
        return model.predict((double) x);
    }

    @Override
    public Map<String, Double> params() {
        Map<String, Double> m = new HashMap<>();
        if (!fitted) {
            m.put("slope", null);
            m.put("intercept", null);
            return m;
        }
        m.put("slope", model.getSlope());
        m.put("intercept", model.getIntercept());
        return m;
    }
}
