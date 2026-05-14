from app.predictor.base import PredictorBase
from app.predictor.lr import LRModel

_REGISTRY: dict[str, type[PredictorBase]] = {
    "lr": LRModel,
}


def create_predictor(name: str = "lr") -> PredictorBase:
    """Factory Method — 설정값으로 예측 전략 객체 생성.

    향후 'poly', 'arima' 등을 _REGISTRY에 추가하면 호출부 변경 없이 교체 가능.
    """
    cls = _REGISTRY.get(name)
    if cls is None:
        raise ValueError(f"unknown predictor: {name!r} (available: {list(_REGISTRY)})")
    return cls()
