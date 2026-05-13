# 05. API 명세

## 포트 규약 (로컬)

| 서비스 | 호스트 | 포트 |
|--------|--------|------|
| Frontend | `localhost` | `5173` |
| Backend | `localhost` | `8000` |
| AI server | `localhost` | `8100` |
| Postgres | `localhost` | `5432` |
| n8n | `localhost` | `5678` |

## 공통 규약

- 모든 응답은 JSON. 시각은 ISO 8601, 금액은 정수(원).
- 분기 표기: `YYYYQn` (예: `2024Q4`).
- 업종 코드 (`industry`): `food` / `service` / `retail` 중 하나.
- 내부 호출 엔드포인트(`/api/ingest/*`, `/predict/*`)는 `X-Internal-Token` 헤더 검사.

---

## Backend API (`:8000`)

브라우저 → Backend 가 호출하는 사용자 대상 API. FastAPI의 `/docs`에서 Swagger UI 제공.

### `GET /api/regions`

서울시 자치구 25개 목록.

**Response 200**
```json
[
  { "regionId": 1, "regionName": "강남구", "sggCode": "11680" },
  { "regionId": 2, "regionName": "강동구", "sggCode": "11740" }
]
```

### `GET /api/regions/{regionId}/sales?industry=food`

특정 지역의 최신 매출 + 최신 예측. 업종별로 조회.

**Path param**
- `regionId` (int)

**Query**
- `industry` (string, optional, default `food`) — `food` / `service` / `retail`.

**Response 200**
```json
{
  "region": { "regionId": 1, "regionName": "강남구", "sggCode": "11680" },
  "industry": "food",
  "current": {
    "quarter": "2024Q4",
    "totalSales": 123456789012,
    "totalCount": 4567890
  },
  "prediction": {
    "targetQuarter": "2025Q1",
    "predictedSales": 128000000000,
    "previousSales": 123456789012,
    "model": { "slope": 1234567.0, "intercept": 9876543210.0, "samplesUsed": 16 },
    "generatedAt": "2026-04-01T03:00:00Z"
  }
}
```

- **`prediction`이 `null`**: 매출은 있으나 예측 미생성 (Activity Diagram의 "예측 데이터 없음" 케이스).
- **Response 404**: `regionId` 미존재.
- **Response 422 (`NO_SALES_DATA`)**: 해당 `(region, industry)` 매출 없음.

### `GET /api/regions/{regionId}/sales/history?industry=food&quarters=8`

차트용 과거 N개 분기 추이.

**Query**
- `industry` (string, optional, default `food`).
- `quarters` (int, optional, default `8`, max `20`).

**Response 200**
```json
{
  "regionId": 1,
  "industry": "food",
  "series": [
    { "quarter": "2023Q1", "totalSales": 110000000000 },
    { "quarter": "2023Q2", "totalSales": 112000000000 },
    "..."
  ]
}
```

### `POST /api/ingest/sales`

n8n이 호출하는 내부 수집 엔드포인트. OA-15572 Open API(또는 CSV)에서 상권 데이터를 받아 자치구 × 분기 × 업종 대분류로 집계 후 `sales_record`에 upsert. **내부 호출 전용** — `X-Internal-Token` 헤더 검사.

**Request body**
```json
{
  "regionIds": null,
  "quarters": null,
  "industries": null,
  "source": "OA-15572"
}
```

- `regionIds`: `null`이면 전체 25개 구.
- `quarters`: `null`이면 OA-15572의 최신 가용 분기 1개. 명시 시 `["2024Q3", "2024Q4"]`.
- `industries`: `null`이면 3개 대분류 전부. 명시 시 `["food"]` 등.
- `source`: 향후 다중 소스 대비 (현재 `OA-15572`만).

**Response 200**
```json
{
  "source": "OA-15572",
  "quarters": ["2024Q4"],
  "industries": ["food", "service", "retail"],
  "processedRegions": 25,
  "succeededRegions": 25,
  "failedRegions": 0,
  "upsertedRows": 75,
  "errors": []
}
```

- **Response 207 (`INGEST_PARTIAL_FAIL`)**: 일부 지역 실패 시 `errors`에 `{ regionId, reason }` 누적.
- **Response 502 (`UPSTREAM_API_ERROR`)**: OA-15572 응답 자체가 비정상.

> **멱등성**: `(region_id, quarter, industry_category)` 유니크 제약 + upsert. 동일 페이로드를 여러 번 호출해도 안전.

---

## AI 서버 API (`:8100`)

n8n / 관리자 도구가 호출하는 내부 API. 모두 `X-Internal-Token` 검사.

### `POST /predict/batch`

전체(또는 일부) 지역·업종에 대해 다음 분기 예측을 일괄 수행하고 `prediction_record`에 저장.

**Request body**
```json
{
  "regionIds": null,
  "industries": null,
  "targetQuarter": null,
  "lookbackQuarters": 16
}
```

- `regionIds`: `null`이면 전체. 명시 시 `[1, 2, 3]`.
- `industries`: `null`이면 3개 대분류 전부.
- `targetQuarter`: `null`이면 DB 최신 분기의 다음 분기.
- `lookbackQuarters`: 학습에 쓸 과거 분기 수 (기본 16 ≒ 4년).

**Response 200**
```json
{
  "targetQuarter": "2025Q1",
  "processedCells": 75,
  "succeededCells": 75,
  "failedCells": 0,
  "generatedAt": "2026-05-13T18:00:00Z",
  "errors": []
}
```

- 1 "cell" = `(region, industry)` 조합. 25 구 × 3 업종 = 75.
- **Response 207 (`BATCH_PARTIAL_FAIL`)**: 일부 셀 실패 시 `errors`에 `{ regionId, industry, reason }`.

### `POST /predict/{regionId}`

단일 지역 즉시 예측 (디버깅/관리자용).

**Request body**
```json
{
  "industry": "food",
  "targetQuarter": "2025Q1",
  "lookbackQuarters": 16
}
```

**Response 200**
```json
{
  "regionId": 1,
  "industry": "food",
  "targetQuarter": "2025Q1",
  "predictedSales": 128000000000,
  "model": { "slope": 1234567.0, "intercept": 9876543210.0 },
  "trainedOn": { "from": "2021Q1", "to": "2024Q4", "samples": 16 }
}
```

### `GET /healthz`

상태 점검. `{ "status": "ok" }` 반환.

---

## 오류 응답 포맷

```json
{ "error": { "code": "REGION_NOT_FOUND", "message": "regionId=999 not found" } }
```

| code | HTTP | 의미 |
|------|------|------|
| `REGION_NOT_FOUND` | 404 | 지역 미존재 |
| `INVALID_INDUSTRY` | 422 | `industry` 값이 food/service/retail 아님 |
| `NO_SALES_DATA` | 422 | 해당 `(region, industry)`의 매출/학습 데이터 부족 |
| `BATCH_PARTIAL_FAIL` | 207 | 일부 셀 예측 실패 (응답 body의 `errors` 참조) |
| `INGEST_PARTIAL_FAIL` | 207 | 일부 지역 수집 실패 |
| `UPSTREAM_API_ERROR` | 502 | 외부 공공데이터 API 비정상 응답 |
| `UNAUTHORIZED` | 401 | `X-Internal-Token` 누락/불일치 |
