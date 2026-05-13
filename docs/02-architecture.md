# 02. 시스템 아키텍처

## 구성 요소

| 컴포넌트 | 기술 스택 | 실행 환경 | 역할 |
|----------|-----------|-----------|------|
| Frontend | React + Vite, 지도 라이브러리(Leaflet/MapLibre), Chart.js/Recharts | 로컬 Node dev 서버 (`:5173`) | 지도 렌더링, 지역 선택, 팝업/차트 표시 |
| Backend API | FastAPI, SQLAlchemy, Pydantic | 로컬 Uvicorn (`:8000`) | 매출/예측 조회 API, DB 접근 |
| AI 서버 | FastAPI, scikit-learn(`LinearRegression`), pandas | 로컬 Uvicorn (`:8100`) | 선형회귀 학습/예측 수행, 결과 DB 저장 |
| Database | PostgreSQL 16 | Docker (`:5432`) | 매출 원천 데이터, 예측 결과 영속화 |
| Batch | n8n | Docker (`:5678`) | 분기 단위로 BE ingest → AI predict 순서 호출 |
| 외부 데이터 | 서울 열린데이터 OA-15572 | Open API / CSV | 상권분석서비스(추정매출-상권). 자세한 호출은 [08-external-api](08-external-api.md) |

분석 단위 (그레인): `자치구 25 × 분기(YYYYQn) × 업종 대분류 3(food/service/retail)`.

## 런타임 토폴로지

```
       ┌──────────────┐                     ┌──────────────────┐
       │   Browser    │  HTTP (JSON)        │  Frontend (Vite) │
       │              │ ─────────────────▶  │   React + Map    │
       └──────────────┘                     └────────┬─────────┘
                                                     │ fetch /api/...
                                                     ▼
                                ┌────────────────────────────────────┐
                                │       Backend (FastAPI :8000)      │
                                │  ┌──────────────┐ ┌────────────┐   │
                                │  │ SalesAPI     │ │ IngestAPI  │   │
                                │  │ (사용자 조회) │ │ (외부 수집) │   │
                                │  └──────┬───────┘ └─────┬──────┘   │
                                └─────────┼───────────────┼──────────┘
                                          │ SQL           │ HTTP (외부 공공 API)
                                          ▼               ▼
                            ┌────────────────────┐   ┌────────────────────┐
                            │ PostgreSQL (Docker)│   │ OA-15572 (서울 열린│
                            │                    │   │ 데이터 광장)        │
                            └────────▲───────────┘   └────────────────────┘
                                     │ SQL (read/write)
       ┌──────────────┐              │
       │ n8n (Docker) │   ───────────┘ (간접) — n8n은 HTTP만 호출
       │  scheduler   │   step 1: POST :8000/api/ingest/sales      (BE)
       │              │   step 2: POST :8100/predict/batch          (AI)
       └──────────────┘
                                            ┌───────────────────────┐
                                            │ AI server (FastAPI    │
                                            │   :8100) LRModel      │
                                            └───────────────────────┘
```

## 호출 흐름

### 사용자 조회 (실시간)

1. 사용자가 지도에서 자치구를 클릭하고 업종을 선택 → Frontend가 `GET /api/regions/{regionId}/sales?industry={food|service|retail}`로 Backend에 요청.
2. Backend `SalesService.findSalesByRegion(regionId, industry)` 호출 → `SalesRepository`가 최신 분기 매출 1건 조회.
3. Backend `PredictionService.findPredictionByRegion(regionId, industry)` 호출 → 최신 예측 결과 조회.
4. Backend가 매출 + 예측을 JSON으로 묶어 반환.
5. 차트용 과거 추이는 별도 `GET .../sales/history?industry=...&quarters=...` 호출로 받는다.
6. Frontend가 팝업/차트로 렌더링.

### 배치 데이터 수집 + 예측 (분기 단위, 하이브리드)

n8n은 **스케줄링·오케스트레이션·재시도·실패 알림**만 담당하고, 실제 외부 API 호출/매핑/저장 같은 도메인 로직은 BE와 AI 서버 코드에서 처리한다. n8n에서는 HTTP 노드 2개를 순차 호출한다.

1. n8n 워크플로우가 cron으로 트리거 (분기 시작 시점, 예: `0 3 1 1,4,7,10 *` — 1/4/7/10월 1일 03:00 KST). 검증 단계에서는 짧은 주기로 두고 결과 확인 후 되돌린다.
2. **Step 1 — Ingest**: n8n → BE `POST /api/ingest/sales`.
   - BE의 `SalesIngestService`가 OA-15572 Open API(또는 CSV)를 호출.
   - 응답 행 단위로 (`상권 → 행정동 → 자치구`) 매핑 + 100개 서비스 업종 → 3개 대분류 매핑 + 단위/NULL 검증.
   - 자치구 × 분기 × 업종 대분류로 합산.
   - `(region_id, quarter, industry_category)` 기준 upsert로 `sales_record`에 저장.
   - 응답: 처리/성공/실패 카운트와 실패 사유.
3. **Step 2 — Predict**: Step 1이 성공이면 n8n → AI `POST /predict/batch`.
   - AI 서버는 셀(`region × industry`) 단위로 DB의 최근 N 분기 매출을 읽어 `LRModel.train` → 다음 분기 `predict` → `prediction_record`에 저장.
   - 25 구 × 3 업종 = 75 셀.
4. n8n은 결과를 로그/알림 분기로 마무리. 어느 단계에서 실패해도 동일 워크플로우 재실행으로 복구 가능 (멱등 — ingest는 upsert, predict는 동일 `(region, industry, target_quarter)`에 새 row 누적, 사용자 조회는 `generated_at DESC LIMIT 1`).
5. Backend의 사용자 조회 요청은 이 테이블들을 그대로 읽어 즉시 응답.

> **왜 BE에서 수집하나**: 외부 API 응답 → `SalesRecord` 매핑 로직은 단위 변환·검증·재시도가 들어가는 코드성 작업이라 SQLAlchemy 모델과 같은 코드 베이스 안에 두는 편이 테스트·유지보수가 쉽다. n8n은 트리거와 오케스트레이션만 맡는다.

## 클래스 매핑 (PDF Class Diagram 기준)

- `MapView`, `RegionPopupView`, `ChartView` → Frontend 컴포넌트.
- `SalesController` → Backend FastAPI 라우터.
- `SalesService`, `PredictionService` → Backend 서비스 계층 (사용자 조회).
- `SalesIngestService` → Backend 서비스 계층 (외부 API 수집/매핑/upsert). PDF 외 추가 컴포넌트.
- `SalesRepository`, `PredictionRepository` → SQLAlchemy 기반 데이터 접근.
- `PredictionGenerateService`, `LRModel` → AI 서버에 위치 (배치 트리거 시 실행).
- `Region`, `SalesRecord`, `PredictionRecord` → 양쪽이 공유하는 데이터 모델. 자세한 스키마는 [04-data-model.md](04-data-model.md) 참고.

## 디자인 패턴 적용 후보

- **MVC 분리**: Controller(라우터) / Service(도메인 로직) / Repository(데이터 접근) 계층화.
- **Repository 패턴**: SQLAlchemy 세션을 감싼 Repository로 영속성 캡슐화.
- **Adapter 패턴**: OA-15572 응답 → `SalesRecord` 도메인 모델 변환을 어댑터로 격리.
- **Facade 패턴**: `SalesIngestService`가 `fetch + adapt + aggregate + upsert`를 한 인터페이스로 묶음.
- **Template Method**: 배치 파이프라인(validate → fetch → transform → save)을 추상 클래스에 골격으로.
- **Strategy 패턴**: `LRModel`을 `PredictorBase` 인터페이스화해 향후 다른 회귀 모델(예: 다항회귀, ARIMA)로 교체 가능하도록.
- **Observer / Pub-Sub**: 배치 완료 이벤트를 Backend가 구독해 캐시 무효화 등에 활용 (확장 시).
