# 11. 테스트 전략

MVP에서는 **가장 잘 깨질 만한 곳**만 좁고 단단하게 테스트한다. 전수 커버리지는 목표가 아니다.

## 우선순위

| 순위 | 대상 | 이유 |
|------|------|------|
| 1 | OpenApi → `SalesRecord` 어댑터 | 외부 컬럼명·단위가 변할 때 가장 먼저 깨진다 |
| 2 | `SalesRepository.upsert_many` 멱등성 | 배치 재실행 안전성의 핵심 |
| 3 | `LRModel.train/predict` 결정성 | 결과 재현성 |
| 4 | `POST /predict/batch` 통합 | 셀 단위 성공/실패 누적이 정확한지 |
| 5 | Frontend 핵심 컴포넌트 1~2개 | 클릭→쿼리스트링→데이터 페치 흐름 |

## Backend / AI 공통 (Python)

- `pytest` + `pytest-asyncio` + `httpx`(TestClient)
- DB 의존 테스트는 **testcontainers-python** 으로 Postgres 컨테이너를 띄움 (CI/로컬 모두 동일).

### 디렉토리

```
backend/tests/
├── conftest.py            # fixtures: db_engine, session, client, sample_rows
├── test_adapter.py
├── test_repository.py
├── test_ingest_service.py
└── test_api_sales.py

ai/tests/
├── conftest.py
├── test_lr_model.py
├── test_predict_pipeline.py
└── test_api_predict.py
```

### 핵심 테스트 케이스

**`test_adapter.py`**
- 정상 1행 → 기대 `NormalizedRow` (분기 변환, 업종 매핑, 단위 정수화).
- 매핑 누락된 `SVC_INDUTY_CD` → `None` 반환 + 워크플로우는 errors에 누적.
- 콤마/공백/NULL 포함 매출 → 깨지지 않고 0 또는 None 처리.

**`test_repository.py`**
- `upsert_many` 두 번 호출해도 row 수 동일 (멱등성).
- 다른 `quarter`나 `industry`로 호출하면 row 증가.
- `find_quarters(n)` 가 정확히 최신 N개 정렬 반환.

**`test_lr_model.py`**
- 같은 입력 → 같은 출력 (seed 고정 또는 deterministic 알고리즘).
- 학습 샘플 < 2이면 명시적 예외.
- 단순 1차 함수 데이터에 대해 slope/intercept ≈ 기대치.

**`test_predict_pipeline.py`**
- 25 구 × 3 업종 = 75 셀 중 일부에 매출이 없는 상황 → `succeededCells + failedCells == 75`.

**`test_api_sales.py`**
- `GET /api/regions` 200 + 25 row.
- `GET /api/regions/1/sales?industry=food` 200 + 키 존재.
- 예측 없음 케이스 → `prediction: null`.
- 잘못된 `industry` → 422 `INVALID_INDUSTRY`.

### fixture 예시

```python
@pytest.fixture(scope="session")
def pg_container():
    from testcontainers.postgres import PostgresContainer
    with PostgresContainer("postgres:16") as pg:
        yield pg

@pytest.fixture
def session(pg_container):
    engine = create_engine(pg_container.get_connection_url())
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    with Session() as s:
        yield s
    Base.metadata.drop_all(engine)
```

샘플 CSV 1행 fixture는 `tests/fixtures/oa15572_sample.json` 등으로 커밋.

## Frontend

- `vitest` + `@testing-library/react`
- 최소 2개:
  1. `MapView` — 폴리곤 클릭 시 `onSelect(regionId)` 호출.
  2. `RegionPopup` — `sales`·`history` props 주입 시 숫자/차트가 렌더.

API 호출 자체는 MSW(Mock Service Worker)로 모킹.

## 통합 시연 (e2e 대체)

E2E 자동화는 MVP 밖. 대신 **수동 시연 시나리오**를 [03-mvp.md](03-mvp.md)의 DoD로 갈음.

## CI

- MVP에는 미포함. 로컬 `pytest` / `pnpm test` 실행 결과로 PR 리뷰.
- 후속으로 GitHub Actions에 두 잡(Python, Node) 추가 후보.

## 안 하는 것

- 80%+ 라인 커버리지 추구.
- 모든 라우터에 대한 happy-path 반복 테스트.
- DB mock (testcontainers로 진짜 Postgres 사용).
