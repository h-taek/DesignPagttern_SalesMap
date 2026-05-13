# 07. n8n 배치 (수집 + 예측)

## 왜 하이브리드인가

- **n8n**: 스케줄링, 오케스트레이션(순서 보장), 재시도, 실패 알림. UI에서 실행 이력 확인.
- **BE / AI 서버**: 외부 API 호출·매핑·검증, 모델 학습/예측 같은 코드성 도메인 로직. 단위 테스트와 SQLAlchemy 재사용이 쉽다.

OA-15572는 분기 단위로 갱신되므로 분기마다 한 번 (1) 외부에서 새 분기 데이터를 가져와 자치구 × 업종 대분류로 집계·저장하고, (2) 다음 분기 예측을 미리 계산해두는 것이 목표. 사용자 요청은 단순 SELECT로 처리한다.

## 워크플로우 개요

```
[Cron Trigger]
   ↓ 분기 1일 03:00 KST (0 3 1 1,4,7,10 *)
[HTTP Request: BE Ingest]   POST http://host.docker.internal:8000/api/ingest/sales
   ↓ 200/207
[IF: succeededRegions > 0]
   ↓ true
[HTTP Request: AI Predict]  POST http://host.docker.internal:8100/predict/batch
   ↓
[Set/Log: 결과 정리]
   ↓ (실패 시) → [Notify / Log]
```

n8n 노드 구성:

1. **Schedule Trigger**: `0 3 1 1,4,7,10 *` (분기 첫 달 1일 03:00 KST). 검증 단계에서는 짧은 주기로 두고 결과 확인 후 분기 단위로 되돌린다.
2. **HTTP Request — Ingest (BE)**:
   - Method: `POST`
   - URL: `http://host.docker.internal:8000/api/ingest/sales`
   - Headers: `X-Internal-Token: {{$credentials.internalToken}}`
   - Body:
     ```json
     {
       "regionIds": null,
       "quarters": null,
       "industries": null,
       "source": "OA-15572"
     }
     ```
   - Timeout: 120s (OA-15572 응답 시간 + 행 수 고려).
   - Retry: 3회, 지수 백오프.
3. **IF 노드**: `{{$json["succeededRegions"]}} > 0` 인지 확인. 모두 실패면 Predict 단계 건너뜀.
4. **HTTP Request — Predict (AI)**:
   - Method: `POST`
   - URL: `http://host.docker.internal:8100/predict/batch`
   - Headers: `X-Internal-Token: {{$credentials.internalToken}}`
   - Body:
     ```json
     {
       "regionIds": null,
       "industries": null,
       "targetQuarter": null,
       "lookbackQuarters": 16
     }
     ```
   - Retry: 2회.
5. **Notify / Log** (선택, MVP는 단순 로그):
   - `failedRegions > 0` 또는 `failedCells > 0` 또는 HTTP non-2xx → 콘솔/Slack.
   - 정상 → 실행 메타데이터(`processedRegions`, `processedCells`, `targetQuarter`)만 로그.

## 멱등성 / 재실행 안전

- **Ingest**는 `(region_id, quarter, industry_category)` 유니크 제약 + upsert이므로 같은 페이로드 반복 호출이 안전.
- **Predict**는 같은 `(region_id, industry_category, target_quarter)`에 대해 새 row를 누적(이력)하고, 사용자 조회는 `generated_at DESC LIMIT 1`로 최신 한 건만 본다.
- 결과적으로 워크플로우 전체를 어느 시점에 재실행해도 안전 → n8n retry/수동 재실행 자유롭게 사용.

## 수동 실행 절차 (개발 검증)

1. `cd infra && docker compose up -d` (postgres, n8n 기동).
2. BE, AI 서버를 로컬에서 기동 ([06-dev-setup.md](06-dev-setup.md)).
3. `http://localhost:5678` 접속, 초기 계정 생성, `INTERNAL_TOKEN` credential 등록.
4. `infra/n8n/workflows/quarterly-ingest-and-predict.json` 임포트.
5. URL이 `host.docker.internal:8000` / `:8100`인지 확인 (Linux는 `--add-host=host.docker.internal:host-gateway`).
6. "Execute Workflow" 클릭 → 두 HTTP 노드 모두 2xx → DB의 `sales_record` (구 25 × 업종 3 = 75 row/분기), `prediction_record` (75 row) 증가 확인.

## 인증 / 비밀값 관리

- 외부 공공데이터 API 키(`OPEN_API_KEY`)는 **BE의 `.env`**에 둔다. 호출 주체가 BE이므로 n8n은 모름.
- **내부 API 보호**: `POST /api/ingest/sales` 와 `POST /predict/batch` 둘 다 `X-Internal-Token` 헤더 검사. n8n에는 동일 토큰을 credential로 보관.
- 로컬 프로젝트라 보안 수준은 토큰 1줄 검사까지만 (자세한 의사결정은 [03-mvp.md](03-mvp.md)).

## AI 서버 측 처리 흐름

`POST /predict/batch` 핸들러는 PDF 관리자 시퀀스를 셀(`region × industry`) 단위로 확장한 것:

1. `regionIds`/`industries`가 `null`이면 전체 (25 × 3 = 75 셀).
2. 각 셀에 대해 `SalesRepository.find_quarters_by_region_industry(region_id, industry, lookback)`로 학습 데이터 로드.
3. 학습 데이터가 부족하면(`samples < 4`) `NO_SALES_DATA`로 셀 단위 실패 처리.
4. `LRModel.train(quarters_index, total_sales)` → `LRModel.predict(target_quarter_index)`.
5. `PredictionRepository.save_prediction(region_id, industry, target_quarter, predicted_sales, slope, intercept, samples)`.
6. 셀별 성공/실패를 모아 응답.

`LRModel`은 향후 다른 알고리즘으로 교체 가능하도록 `PredictorBase` 인터페이스를 둔다 — Strategy 패턴.

## 워크플로우 버전 관리

- n8n에서 워크플로우 export → `infra/n8n/workflows/*.json`으로 커밋.
- credential은 export에 포함되지 않으므로 README에 별도 안내.

## 운영 시 고려 (MVP 이후)

- OA-15572 rate limit / 일일 호출 제한 — 분기/업종별 분할 호출, 백오프 설계.
- 결측 분기 보정 정책 (전 분기 값 사용 vs. 학습에서 제외).
- 워크플로우 실행 결과를 별도 테이블(예: `batch_run_log`)에 적재해 운영 대시보드화.
