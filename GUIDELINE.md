# SalesMap 실행 가이드 — 처음 시작하는 분들을 위해

SalesMap을 처음 내려받은 분들이 **Docker 기동 → 서버 실행 → 데이터 수집 → 화면 확인**까지
가장 쉽고 빠르게 따라 할 수 있도록 정리했습니다. 아래 순서대로 명령어를 복사해서 사용하세요.

---

## 0. 전체 구조 (아키텍처 요약)

*   **Docker (DB + n8n)**: 데이터 저장소와 배치 작업을 담당합니다.
*   **Backend (FastAPI, :8000)**: 공공 API 수집과 데이터 조회를 담당합니다.
*   **AI 서버 (FastAPI, :8100)**: 과거 매출 기반 미래 예측을 담당합니다.
*   **Frontend (React, :5173)**: 서울 지도를 통해 시각적으로 정보를 보여줍니다.

---

## 1. 사전 준비물 (필수)

| 도구 | 설치 확인 방법 |
| :--- | :--- |
| **Docker Desktop** | `docker version` (실행 중이어야 함) |
| **Python 3.11+** | `python3 --version` (3.14도 가능) |
| **Node.js 20+** | `node --version` |

**체크포인트:** `8000`(BE), `8100`(AI), `5173`(FE), `5432`(DB), `5678`(n8n) 포트가 비어 있어야 합니다.

---

## 2. 처음 한 번만 수행 (셋업)

### 2-1. 소스코드 다운로드
```bash
git clone https://github.com/h-taek/DesignPagttern_SalesMap.git SalesMap
cd SalesMap
```

### 2-2. 환경 설정 파일 복사
```bash
cp backend/.env.example backend/.env
cp ai/.env.example ai/.env
```
*   **중요:** `backend/.env`를 열어 `OPEN_API_KEY`에 발급받은 인증키를 넣으세요.
*   [서울 열린데이터 광장](https://data.seoul.go.kr)에서 즉시 발급 가능합니다.

### 2-3. Python 가상환경 및 라이브러리 설치
```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows는 .venv\Scripts\activate
pip install -r backend/requirements.txt -r ai/requirements.txt
```

### 2-4. Frontend 라이브러리 설치
```bash
cd frontend
npm install
cd ..
```

---

## 3. 서버 실행 순서 (매번 동일)

터미널 4개를 열고 각각 실행하세요. 모든 명령은 **프로젝트 루트(`SalesMap/`)** 기준입니다.

### ① Docker (DB & n8n) 실행
```bash
cd infra && docker compose up -d && cd ..
```
*   데이터베이스와 자동화 도구가 배경에서 돌아갑니다.

### ② Backend 실행 (포트 8000)
```bash
.venv/bin/uvicorn app.main:app --reload --port 8000 --app-dir backend
```
*   **주의:** `--app-dir backend` 옵션이 없으면 서버가 시작되지 않습니다.

### ③ AI 서버 실행 (포트 8100)
```bash
.venv/bin/uvicorn app.main:app --reload --port 8100 --app-dir ai
```

### ④ Frontend 실행 (포트 5173)
```bash
cd frontend && npm run dev
```
*   이제 브라우저에서 `http://localhost:5173`에 접속할 수 있습니다.

---

## 4. 데이터 채우기 (최초 1회 필수)

서버만 띄우면 지도는 보이지만 매출 데이터는 없습니다. 아래 방법 중 하나를 선택하세요.

### 방법 A: API로 직접 수집 (추천)
인증키가 있다면 아래 명령어로 최신 분기 데이터를 가져옵니다.
```bash
curl -X POST http://localhost:8000/api/ingest/sales \
  -H "X-Internal-Token: dev-internal-token" \
  -H "Content-Type: application/json" \
  -d '{"quarters": ["2024Q4"]}'
```

### 방법 B: n8n으로 자동 수집
1. `http://localhost:5678` 접속 후 초기 계정 생성.
2. `infra/n8n/workflows/quarterly-ingest-and-predict.json` 파일을 화면에 끌어다 놓기(Import).
3. **"Execute Workflow"** 클릭. (BE 수집과 AI 예측이 한 번에 진행됩니다.)

### AI 예측 데이터 생성
수집이 끝났다면(방법 A 사용 시), 예측 데이터도 만들어야 합니다.
```bash
curl -X POST http://localhost:8100/predict/batch \
  -H "X-Internal-Token: dev-internal-token" \
  -H "Content-Type: application/json" \
  -d '{"lookbackQuarters": 16}'
```

---

## 5. 변경된 UI 확인하기

정상적으로 데이터가 들어갔다면 지도에서 특정 구를 클릭했을 때 다음을 확인할 수 있습니다:

*   **예측 퍼센트 표시:** 매출 금액 옆에 `(▲ 15.2%)` 같이 이전 분기 대비 변동폭이 보입니다.
*   **차트 라벨:** 하단 차트의 X축이 `2024_4` 같이 깔끔한 형식으로 표시됩니다.
*   **지도 애니메이션:** 구를 클릭하면 부드럽게 확대되며 해당 지역이 강조됩니다.

---

## 6. 자주 발생하는 문제 해결 (FAQ)

| 증상 | 해결 방법 |
| :--- | :--- |
| `ModuleNotFoundError: No module named 'app'` | 실행 명령어에 `--app-dir backend` 또는 `--app-dir ai`가 빠졌는지 확인하세요. |
| 지도는 나오는데 데이터가 '없음'으로 뜸 | **4번 단계(데이터 채우기)**를 수행했는지 확인하세요. |
| n8n에서 연결 오류 발생 | n8n 컨테이너는 호스트를 `host.docker.internal`로 바라봐야 합니다. 워크플로우 URL 설정을 확인하세요. |
| API 수집 시 502 에러 | `backend/.env`에 `OPEN_API_KEY`를 정확히 입력했는지 확인하세요. |
| DB를 완전히 초기화하고 싶을 때 | `cd infra && docker compose down -v` 실행 후 다시 `up -d` 하세요 (모든 데이터 삭제됨). |

---

## 7. 주요 문서 링크 (더 자세히 알고 싶다면)

*   [아키텍처 및 시스템 흐름 (docs/02)](docs/02-architecture.md)
*   [API 명세서 (docs/05)](docs/05-api.md)
*   [배치 및 예측 자동화 설명 (docs/07)](docs/07-batch-prediction.md)
*   [프론트엔드 UI 설계 (docs/09)](docs/09-frontend.md)
*   [디자인 패턴 적용 사례 (docs/10)](docs/10-design-patterns.md)
