import numpy as np
from sklearn.linear_model import LinearRegression

from app.predictor.base import NotEnoughData, PredictorBase


class LRModel(PredictorBase):
    """단순 선형회귀 (scikit-learn). Strategy 구현체."""

    MIN_SAMPLES = 2

    def __init__(self) -> None:
        self._model = LinearRegression()
        self._fitted = False

    def train(self, x: list[int], y: list[int]) -> None:
        if len(x) < self.MIN_SAMPLES or len(x) != len(y):
            raise NotEnoughData(f"need >= {self.MIN_SAMPLES} samples, got {len(x)}")
        X = np.asarray(x, dtype=float).reshape(-1, 1)
        Y = np.asarray(y, dtype=float)
        self._model.fit(X, Y)
        self._fitted = True

    def predict(self, x: int) -> float:
        if not self._fitted:
            raise RuntimeError("model not trained")
        return float(self._model.predict(np.asarray([[x]], dtype=float))[0])

    def params(self) -> dict:
        if not self._fitted:
            return {"slope": None, "intercept": None}
        return {
            "slope": float(self._model.coef_[0]),
            "intercept": float(self._model.intercept_),
        }
