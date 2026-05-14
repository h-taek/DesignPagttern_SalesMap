# 04. 데이터 모델

## 그레인 (확정)

| 축 | 단위 | 비고 |
|----|------|------|
| 시간 | **분기** (`YYYYQn`, 예: `2024Q4`) | OA-15572가 분기 단위로만 제공. 공개 API로 가용한 월별 데이터 없음. |
| 공간 | **자치구 25개** | OA-15572의 상권 코드 → 자치구로 집계 (OA-15560 매핑 사용). |
| 업종 | **대분류 3개** (`food` / `service` / `retail`) | 세부 업종(2024Q4 기준 62종)은 화면에 안 쓰고, 적재는 위 3개로 사전 집계해서 저장. |

따라서 `region × quarter × industry_category` 가 분석 단위. 단일 셀의 의미는 "강남구의 2024Q4 외식업 합계 매출".

## ER 개요

```
region (1) ───< (N) sales_record
region (1) ───< (N) prediction_record
region (1) ───< (N) region_trdar_map
```

업종은 ENUM/CHAR 컬럼으로만 표현하고 별도 테이블을 두지 않는다 (3개 고정).

## 테이블

### `region`

서울시 자치구 25개로 고정. (MVP에서 동/상권 미사용)

| 컬럼 | 타입 | 제약 | 비고 |
|------|------|------|------|
| `region_id` | `SERIAL` | PK | |
| `region_name` | `VARCHAR(20)` | NOT NULL | 예: "강남구" |
| `sgg_code` | `CHAR(5)` | UNIQUE NOT NULL | 행정안전부 시군구 코드 (예: `11680`) |

### `region_trdar_map`

OA-15572의 상권 코드(`TRDAR_CD`)를 자치구로 환원하기 위한 정적 매핑 테이블.
OA-15560(상권영역)에서 생성하며, `infra/db/02-seed-trdar-map.sql` 로 한 번 적재한다 (약 1,650행).

| 컬럼 | 타입 | 제약 | 비고 |
|------|------|------|------|
| `trdar_code` | `CHAR(7)` | PK | 상권 코드 |
| `region_id` | `INT` | FK → `region.region_id`, NOT NULL | 소속 자치구 |

### `region_dong_map`

행정동 코드를 자치구로 묶기 위한 정적 매핑 테이블 (예비). OA-15572 적재 자체는
`region_trdar_map` 으로 해결되며, 이 테이블은 행정동 단위 데이터를 다룰 때를 위한 자리.

| 컬럼 | 타입 | 제약 | 비고 |
|------|------|------|------|
| `dong_code` | `CHAR(10)` | PK | 행정동 코드 |
| `dong_name` | `VARCHAR(40)` | NOT NULL | |
| `region_id` | `INT` | FK → `region.region_id`, NOT NULL | 소속 자치구 |

### `sales_record`

매출 원천을 `region × quarter × industry_category` 그레인으로 사전 집계한 결과.

| 컬럼 | 타입 | 제약 | 비고 |
|------|------|------|------|
| `sales_id` | `BIGSERIAL` | PK | |
| `region_id` | `INT` | FK → `region.region_id`, NOT NULL | |
| `quarter` | `CHAR(6)` | NOT NULL | `YYYYQn` 예: `2024Q4` |
| `industry_category` | `VARCHAR(10)` | NOT NULL, CHECK IN (`food`, `service`, `retail`) | |
| `total_sales` | `BIGINT` | NOT NULL | 분기 합계 매출(원) |
| `total_count` | `BIGINT` | | 분기 합계 결제 건수 |
| `created_at` | `TIMESTAMPTZ` | DEFAULT `now()` | |

인덱스:
- `UNIQUE (region_id, quarter, industry_category)` — upsert 키.
- `INDEX (region_id, industry_category, quarter DESC)` — 최신 조회 / 시계열 추출.

### `prediction_record`

배치 예측 결과. 같은 (구, 업종, 대상 분기)에 대해 여러 시점 이력을 누적.

| 컬럼 | 타입 | 제약 | 비고 |
|------|------|------|------|
| `prediction_id` | `BIGSERIAL` | PK | |
| `region_id` | `INT` | FK → `region.region_id`, NOT NULL | |
| `industry_category` | `VARCHAR(10)` | NOT NULL | |
| `target_quarter` | `CHAR(6)` | NOT NULL | 예측 대상 분기 |
| `predicted_sales` | `BIGINT` | NOT NULL | |
| `previous_sales` | `BIGINT` | | 직전 실측치 (참고용) |
| `model_slope` | `DOUBLE PRECISION` | | LR 계수 |
| `model_intercept` | `DOUBLE PRECISION` | | LR 절편 |
| `samples_used` | `INT` | | 학습에 쓴 분기 수 |
| `generated_at` | `TIMESTAMPTZ` | DEFAULT `now()` | 배치 실행 시각 |

인덱스:
- `INDEX (region_id, industry_category, target_quarter DESC, generated_at DESC)` — 최신 예측 조회용.

## OA-15572 → `sales_record` 매핑

OA-15572의 주요 컬럼과 본 스키마의 매핑.

| OA-15572 원본 컬럼 | 처리 | sales_record 매핑 |
|------|------|------|
| `STDR_YYQU_CD` (예: `20244`) | `f"{c[:4]}Q{c[4]}"` | `quarter` (`2024Q4`) |
| `TRDAR_CD` (상권 코드) | `region_trdar_map` 으로 자치구 환원 | `region_id` |
| `SVC_INDUTY_CD` (세부 업종 코드) | `industry_map.csv`로 3개 대분류 매핑 | `industry_category` |
| `THSMON_SELNG_AMT` (분기 합계 매출) | 같은 (구, 분기, 대분류) 합산 | `total_sales` (SUM) |
| `THSMON_SELNG_CO` (분기 합계 건수) | 합산 | `total_count` (SUM) |
| 그 외 (요일/시간대/성연령 분해) | MVP 미사용 | — |

> 컬럼명이 `THSMON_SELNG_AMT`("당월")로 표기되지만 OA-15572는 본문상 분기 합계임.
> OA-15572 원본에는 자치구·행정동 컬럼이 없어 `TRDAR_CD` → 자치구 환원에 OA-15560을 보조로 쓴다 ([08-external-api.md](08-external-api.md) 참조).

### 업종 매핑 룰 (`SVC_INDUTY_CD` → `industry_category`)

`infra/db/industry_map.csv`로 분리해 두고 변경 가능. `backend/scripts/build_maps.py`가
OA-15572 실데이터의 distinct 업종 코드를 추출해 자동 생성한다. 코드 prefix 규칙:

- `CS1xxxxx` 외식업 → `food`
- `CS2xxxxx` 서비스업 → `service`
- `CS3xxxxx` 소매업 → `retail`

## ORM 매핑 (예시)

BE와 AI 서버 양쪽이 동일한 SQLAlchemy 모델을 각자 정의 (MVP는 중복 정의 허용). 변경 시 양쪽 동기화.

```python
class Region(Base):
    __tablename__ = "region"
    region_id = Column(Integer, primary_key=True)
    region_name = Column(String(20), nullable=False)
    sgg_code = Column(String(5), unique=True, nullable=False)

class SalesRecord(Base):
    __tablename__ = "sales_record"
    sales_id = Column(BigInteger, primary_key=True)
    region_id = Column(Integer, ForeignKey("region.region_id"), nullable=False)
    quarter = Column(String(6), nullable=False)
    industry_category = Column(String(10), nullable=False)
    total_sales = Column(BigInteger, nullable=False)
    total_count = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (
        UniqueConstraint("region_id", "quarter", "industry_category"),
    )

class PredictionRecord(Base):
    __tablename__ = "prediction_record"
    prediction_id = Column(BigInteger, primary_key=True)
    region_id = Column(Integer, ForeignKey("region.region_id"), nullable=False)
    industry_category = Column(String(10), nullable=False)
    target_quarter = Column(String(6), nullable=False)
    predicted_sales = Column(BigInteger, nullable=False)
    previous_sales = Column(BigInteger)
    model_slope = Column(Float)
    model_intercept = Column(Float)
    samples_used = Column(Integer)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
```

## 적재 / 시드 전략

1. **정적 데이터** (`docker compose up` 시 initdb 단계에서 자동 적재):
   - `region` 25행 — `infra/db/init.sql` 의 `INSERT`.
   - `region_trdar_map` ~1,650행 — `infra/db/02-seed-trdar-map.sql`.
   - 두 매핑 파일(`industry_map.csv`, `02-seed-trdar-map.sql`)은 `backend/scripts/build_maps.py`로 OA-15560/15572에서 재생성한다.
2. **OA-15572 매출 데이터** (분기마다 또는 최초 1회):
   - `POST /api/ingest/sales` (BE) — 외부 API 호출 → 어댑터 정규화 → 구 단위 합산 → `sales_record` upsert.
   - 또는 `backend/scripts/load_csv.py` — API 키 없이 CSV로 같은 파이프라인 적재.
3. **`prediction_record`** — n8n 배치(또는 `POST /predict/batch`)가 채움.

> Alembic은 도입하지 않는다. 스키마 변경 시 `init.sql`을 직접 수정하고 DB 볼륨 재생성. MVP 단계에선 마이그레이션 비용보다 단순함이 이득.
