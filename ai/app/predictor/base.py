from abc import ABC, abstractmethod


class NotEnoughData(Exception):
    """학습 표본이 부족할 때."""


class PredictorBase(ABC):
    """예측 모델 전략 인터페이스 (Strategy 패턴).

    x: 분기 인덱스(정수) 리스트, y: 매출액 리스트.
    """

    @abstractmethod
    def train(self, x: list[int], y: list[int]) -> None: ...

    @abstractmethod
    def predict(self, x: int) -> float: ...

    @abstractmethod
    def params(self) -> dict: ...
