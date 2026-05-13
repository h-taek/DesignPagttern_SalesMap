# 03. MVP 범위 및 단계

## MVP 정의

> "지도에서 서울시 자치구를 클릭하고 업종(외식/서비스/소매)을 선택하면, 해당 셀의 최신 분기 매출과 다음 분기 예측이 팝업/차트로 보이고, 예측은 n8n 분기 배치로 갱신된다."

이 한 문장이 동작하면 MVP 완료로 본다.

## 포함 / 비포함

### 포함

- 로컬에서 전체 스택 실행 (Docker Compose 일부 + 로컬 dev 서버).
- 서울시 **자치구 25개** 지도 렌더링.
- 업종 **대분류 3개** (외식/서비스/소매) 토글.
- 분기 단위 매출 조회 (`YYYYQn`) + 분기 추이 차트 (8 분기).
- 선형회귀(`scikit-learn.LinearRegression`) 기반 **다음 1분기** 예측.
- n8n으로 수동/스케줄 트리거 모두 가능한 배치 워크플로우 1개 (ingest → predict).

### 비포함 (후속 작업)

- 행정동/상권 단위 세분화.
- 100개 세부 업종, 다중 지역 비교 뷰.
- 실사용자 인증, 권한.
- 모델 고도화 (계절성, ARIMA, Prophet 등).
- 운영 배포 (클라우드, CI/CD).

## 완료 기준 (Done Definition)

| # | 항목 | 검증 방법 |
|---|------|----------|
| 1 | Postgres가 Docker로 기동되고 `region`(25), `region_dong_map`이 적재된다 | `docker compose up db` 후 `psql`로 row 수 확인 |
| 2 | OA-15572 CSV 또는 Open API 응답이 `sales_record`에 25 구 × 분기 × 3 업종으로 정규화 적재된다 | `SELECT COUNT(*) GROUP BY industry_category` 확인 |
| 3 | Backend가 로컬에서 기동되고 `/api/regions/{id}/sales?industry=food` 응답 | Swagger UI(`/docs`)에서 호출 |
| 4 | Backend `/api/ingest/sales` 호출 시 신규 분기를 받아 upsert | DB row 증가 + 동일 호출 반복 시 중복 없음 |
| 5 | AI 서버가 로컬에서 기동되고 `/predict/batch` 호출 시 `prediction_record`에 75 row(25 구 × 3 업종) 적재 | DB row 수 확인 |
| 6 | n8n 워크플로우가 `ingest → predict` 순서로 동작 | n8n execution log + 양쪽 테이블 row 증가 확인 |
| 7 | Frontend에서 자치구 클릭 + 업종 토글 시 팝업에 분기 매출/예측과 8 분기 차트가 표시 | 브라우저에서 직접 확인 |

## 마일스톤

### M1. 기반 셋업

- 레포 초기 구조 (`frontend/`, `backend/`, `ai/`, `infra/`).
- `infra/docker-compose.yml`: postgres + n8n.
- `infra/db/init.sql`: 스키마 + `region`(25) seed.
- `infra/db/seed_dong_map.csv`: 행정동 → 자치구 매핑 (~425행).
- OA-15572 CSV 1회 다운로드 → `backend/scripts/load_csv.py`로 `sales_record` 정규화 적재.

### M2. Backend & DB

- SQLAlchemy 모델: `Region`, `SalesRecord`, `PredictionRecord`.
- Repository / Service / Controller 계층.
- `GET /api/regions`, `GET /api/regions/{id}/sales` (조회 2개).
- `POST /api/ingest/sales` (외부 공공 API 수집 + upsert, 내부 토큰 보호).

### M3. AI 서버 & 배치

- `POST /predict/batch` (전체 지역 일괄) / `POST /predict/{regionId}` (단건).
- `LRModel` (train + predict) — scikit-learn 래핑.
- n8n 워크플로우 1개: cron → BE ingest → IF 성공 → AI predict → 로그.

### M4. Frontend

- Leaflet + `react-leaflet` + 서울 25 구 GeoJSON.
- 업종 토글(food/service/retail), 구 클릭 시 Backend 호출 → 팝업/차트(Recharts) 렌더링.

### M5. 통합 점검

- 전체 흐름 end-to-end 시연 시나리오 작성.
- README의 "빠른 시작"이 그대로 동작하는지 점검.

## 결정된 사항

- **데이터 소스**: 서울 열린데이터 OA-15572 (상권분석서비스 추정매출-상권). 공공누리 1유형. 자세한 매핑은 [08-external-api](08-external-api.md).
- **시간 그레인**: 분기 (`YYYYQn`). OA-15572가 분기 단위. 공개 API로 가용한 월별 데이터 없음.
- **공간 그레인**: 자치구 25개. 상권 → 행정동 → 자치구로 환원해 집계.
- **업종 그레인**: 대분류 3개 (외식/서비스/소매). 100개 세부는 적재·노출 안 함.

## 남은 리스크

- **GeoJSON 출처**: 서울 25 구 폴리곤을 어디서 받을지 라이선스 포함 확정 필요 (예: `southkorea-maps`, 행정안전부 공공데이터).
- **OA-15572 컬럼명 변동**: 연도에 따라 컬럼명이 미세하게 다를 수 있음. 적재 스크립트에 헤더 검증 필요.
- **분기 수 부족**: 학습에 쓸 과거 분기 수가 적으면 회귀가 의미 없음. `lookbackQuarters` 기본 16(4년) 확보.
