# 12. 로깅 / 관측

MVP는 **stdout JSON 로그 + 요청 ID 한 줄 추적**까지만. 별도 대시보드/수집기는 안 둔다.

## 로그 형식

- 라이브러리: Python은 `structlog`. JS는 콘솔로 충분.
- 출력: stdout 한 줄당 JSON 1개.
- 필드 규약:

| 필드 | 의미 |
|------|------|
| `ts` | ISO 8601 UTC |
| `level` | `debug` / `info` / `warn` / `error` |
| `service` | `backend` / `ai` |
| `event` | 짧은 이벤트명 (예: `ingest.start`, `predict.cell.done`) |
| `request_id` | 요청 단위 ID (UUID v4) |
| `n8n_execution_id` | n8n에서 호출 시 전달된 실행 ID |
| `region_id`, `industry`, `quarter`, `target_quarter` | 도메인 컨텍스트 |
| `error` | 에러 시 `{ code, message }` |

예시:
```json
{"ts":"2026-05-13T18:00:00Z","level":"info","service":"backend",
 "event":"ingest.upsert.done","request_id":"…","n8n_execution_id":"…",
 "upserted_rows":75}
```

## 요청 ID 미들웨어 (FastAPI)

- 들어오는 요청에 `X-Request-Id` 헤더가 있으면 그 값을 사용, 없으면 새 UUID v4 생성.
- `contextvars`로 핸들러 전 구간 전파, 모든 로그에 자동 첨부.
- 응답에 `X-Request-Id` 에코.

## n8n → 호출 헤더 규약

n8n 워크플로우는 다음 헤더를 같이 보낸다:

```
X-Internal-Token: …
X-Request-Id: {{$json["$execution"]["id"]}}
X-N8n-Execution-Id: {{$json["$execution"]["id"]}}
```

BE/AI는 둘 다 첫 값을 우선 사용해 한 워크플로우 실행이 BE 로그·AI 로그에 동일 ID로 묶이게 한다.

## 무엇을 남기나

- **Ingest**: 시작/끝, 분기·지역·업종 카운트, 외부 API HTTP 상태, 어댑터 거부 카운트, upsert 결과.
- **Predict**: 셀 시작/끝, 학습 샘플 수, 결정계수(있다면), 예측값 1줄.
- **API 라우터**: 4xx/5xx만 자동 로그 (성공은 access log 1줄로 충분).

## 무엇을 안 하나 (MVP 밖)

- 메트릭(Prometheus) / 트레이싱(OpenTelemetry).
- 로그 수집기(Loki, ELK).
- 알림(Slack, Email). 운영 단계에서 n8n의 IF 분기로 우선 처리.

## 디버깅 흐름

문제 발생 시:

1. n8n execution UI에서 실행 ID와 실패 노드 확인.
2. 실행 ID로 BE 컨테이너 로그 grep → 어댑터 단계인지, repository 단계인지 식별.
3. 그래도 안 보이면 AI 컨테이너 로그 grep.
4. DB에 들어간 row를 직접 확인 (`prediction_record WHERE generated_at > …`).
