# 10. 디자인 패턴 적용

수업 산출물 관점에서 본 프로젝트가 어느 부분에 어떤 패턴을 적용했는지 표로 정리한다. PDF Class Diagram + 본 문서들의 설계 합본 기준.

## 한눈에 보기

| 패턴 | 적용 위치 | 의도 |
|------|-----------|------|
| Layered Architecture (MVC) | Backend (`api` → `services` → `repositories`) | 관심사 분리. 라우터는 입출력만, 서비스는 도메인, 레포지토리는 영속성. |
| Repository | `SalesRepository`, `PredictionRepository` | SQLAlchemy 세션과 SQL을 캡슐화해 서비스 계층을 DB 구현에서 분리. |
| Adapter | `OpenApiRowAdapter` (OA-15572 행 → `SalesRecord` 정규화 행) | 외부 응답 스키마 변화로부터 도메인 모델 보호. |
| Facade | `SalesIngestService` (`fetch` + `adapt` + `aggregate` + `upsert` 한 호출로) | 다단계 파이프라인을 단순한 진입점으로 제공. 컨트롤러/배치가 알 필요 없는 내부를 숨김. |
| Template Method | `BatchPipeline` 추상 클래스 (`validate → fetch → transform → save`) | 배치 절차의 골격을 고정, 세부 단계만 하위 클래스가 구현. Ingest 배치와 Predict 배치가 같은 골격 재사용. |
| Strategy | `PredictorBase` ↔ `LRModel` (그리고 향후 `PolyModel`, `ARIMAModel`) | 예측 알고리즘을 런타임에 교체 가능하도록. |
| Factory Method | `PredictorFactory.create(model_name)` | 설정/환경변수로 회귀 모델 선택 시 객체 생성을 중앙화. |
| Singleton (de facto) | DB Engine, OpenApi 클라이언트 | FastAPI의 `Depends` + 모듈 캐시로 사실상 1회 생성. 명시 패턴은 아니지만 결과는 동일. |
| DTO / Value Object | Pydantic `schemas.py` (요청·응답 모델) | API 경계에서 도메인 모델과 직렬화 모델을 분리. |
| Observer (확장 예정) | 배치 완료 이벤트 → 캐시 무효화 / 알림 | MVP 미포함. 운영 단계 확장 후보. |

## 패턴별 세부

### Layered Architecture
- **위치**: `backend/app/{api,services,repositories,models,schemas}.py`
- **규칙**: 위 계층이 아래 계층만 의존. `api`는 `schemas`+`services`만, `services`는 `repositories`+도메인, `repositories`는 `models` ORM만.
- **이점**: 단위 테스트가 계층 단위로 가능. 라우터에 DB를 직접 쓰지 않으므로 mock service로 라우터 테스트 가능.

### Repository
- **인터페이스 예시** (`SalesRepository`):
  ```python
  class SalesRepository:
      def find_latest(self, region_id: int, industry: str) -> SalesRecord | None: ...
      def find_quarters(self, region_id: int, industry: str, n: int) -> list[SalesRecord]: ...
      def upsert_many(self, rows: list[SalesRow]) -> int: ...
  ```
- **이점**: 서비스가 SQL/ORM 세부를 모름. 추후 PostGIS 도입 등 변경이 캡슐화됨.

### Adapter
- **위치**: `backend/app/services/ingest/adapter.py`
- **역할**: OA-15572 1행 (CSV/XML/JSON 어느 쪽이든) → 정규화된 도메인 행으로 변환.
- **이점**: 외부 컬럼명이 바뀌어도 영향 범위가 한 파일.

```python
@dataclass
class NormalizedRow:
    region_id: int
    quarter: str           # 'YYYYQn'
    industry: str          # food|service|retail
    total_sales: int
    total_count: int

class OpenApiRowAdapter:
    def __init__(self, region_resolver: RegionResolver, industry_map: IndustryMap): ...
    def adapt(self, raw: dict) -> NormalizedRow | None: ...
```

### Facade
- **위치**: `SalesIngestService.run(...)`
- **숨기는 것**: Open API 호출(`OpenApiClient`), 페이지네이션, 어댑터, 집계, upsert, 에러 누적.
- **외부에 노출되는 인터페이스 하나**: `run(quarters, region_ids, industries) -> IngestResult`.

### Template Method
- **추상 골격** (`BatchPipeline`):
  ```python
  class BatchPipeline:
      def execute(self) -> Result:
          self.validate()
          raw = self.fetch()
          rows = self.transform(raw)
          return self.save(rows)
  ```
- **하위 구현**: `IngestPipeline`(BE), `PredictPipeline`(AI). 같은 골격 + 다른 세부.

### Strategy
- **추상**:
  ```python
  class PredictorBase(ABC):
      @abstractmethod
      def train(self, x: list[int], y: list[int]) -> None: ...
      @abstractmethod
      def predict(self, x: int) -> int: ...
      @abstractmethod
      def params(self) -> dict: ...
  ```
- **구현**: `LRModel(scikit-learn.LinearRegression)`. 향후 `PolyModel`, `ARIMAModel`로 확장.
- **사용**: `PredictionGenerateService`는 `PredictorBase`만 안다.

### Factory Method
- **위치**: `ai/app/factory.py`
- **역할**: 환경변수 `PREDICTOR=lr|poly|arima`에 따라 적절한 `PredictorBase` 반환.
- **이점**: `PredictionGenerateService`는 어떤 모델을 받았는지 신경 쓰지 않음.

### DTO / Value Object
- **위치**: `backend/app/schemas.py`, `ai/app/schemas.py` (Pydantic)
- **역할**: HTTP 경계의 입/출력 모델. `SalesRecord`(ORM) ↔ `SalesRecordOut`(Pydantic)을 분리해 직렬화 변경이 ORM에 새지 않게.

### Observer (확장 예정)
- 배치 완료 시 BE의 cache/메모리에 알림 → 사용자 조회 응답을 더 빨리.
- MVP에서는 매 호출이 DB 단순 조회라 필요 없음.

## PDF Class Diagram → 본 문서 패턴 매핑

| PDF 클래스 | 본 문서 패턴 |
|------------|--------------|
| `MapView`, `RegionPopupView`, `ChartView` | View (Frontend, [09-frontend](09-frontend.md)) |
| `SalesController` | Controller (FastAPI Router) |
| `SalesService`, `PredictionService` | Service (Layered) |
| `SalesRepository`, `PredictionRepository` | Repository |
| `LRModel` | Strategy 구현체 |
| `PredictionGenerateService` | Strategy 호출자 + Template Method 하위 |
| `Region`, `SalesRecord`, `PredictionRecord` | Entity (ORM) |

추가된 클래스(`SalesIngestService`, `OpenApiRowAdapter`, `BatchPipeline`, `PredictorBase`, `PredictorFactory`)는 본 문서 라인에서 새로 도입된 컴포넌트.
