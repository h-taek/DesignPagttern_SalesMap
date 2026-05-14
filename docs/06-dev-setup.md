# 06. 로컬 개발 환경 설정

본 문서는 개발자가 로컬 환경에서 SalesMap 프로젝트를 설정하고 실행하는 상세 절차를 다룹니다.

## 1. 사전 요구사항

| 도구 | 권장 버전 | 역할 |
| :--- | :--- | :--- |
| Docker Desktop | 최신 | PostgreSQL DB 및 n8n 컨테이너 실행 |
| Python | 3.11 이상 | Backend 및 AI 서버 실행 |
| Node.js | 20.x 이상 | Frontend(Vite) 개발 서버 실행 |
| npm / pnpm | 최신 | Frontend 패키지 관리 |

## 2. 환경 설정

### 2-1. 소스코드 및 폴더 구조
프로젝트 루트에서 모든 작업을 수행하는 것을 권장합니다.

```
SalesMap/
├── backend/    # FastAPI (Port 8000)
├── ai/         # FastAPI (Port 8100)
├── frontend/   # React (Port 5173)
├── infra/      # Docker Compose & n8n
└── .venv/      # 통합 Python 가상환경
```

### 2-2. 환경 변수 파일 (.env)
각 서버 디렉토리에 `.env` 파일을 생성하고 필수 값을 설정해야 합니다.

*   **backend/.env**
    ```env
    DATABASE_URL=postgresql+psycopg://salesmap:salesmap@localhost:5432/salesmap
    OPEN_API_KEY=발급받은_인증키
    INTERNAL_TOKEN=dev-internal-token
    ```
*   **ai/.env**
    ```env
    DATABASE_URL=postgresql+psycopg://salesmap:salesmap@localhost:5432/salesmap
    INTERNAL_TOKEN=dev-internal-token
    ```

## 3. 실행 단계

### Step 1: 인프라 기동 (Docker)
```bash
cd infra
docker compose up -d
```
*   PostgreSQL(`5432`)과 n8n(`5678`)이 기동됩니다.
*   `infra/db/`에 포함된 SQL 파일들이 실행되어 초기 스키마와 자치구 데이터가 생성됩니다.

### Step 2: Python 가상환경 설정
Backend와 AI 서버는 루트의 단일 가상환경을 공유합니다.
```bash
# 프로젝트 루트에서 실행
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt -r ai/requirements.txt
```

### Step 3: Backend 서버 실행
```bash
.venv/bin/uvicorn app.main:app --reload --port 8000 --app-dir backend
```
*   `--app-dir backend` 옵션을 통해 `backend/app/main.py`를 올바르게 인식합니다.

### Step 4: AI 서버 실행
```bash
.venv/bin/uvicorn app.main:app --reload --port 8100 --app-dir ai
```

### Step 5: Frontend 개발 서버 실행
```bash
cd frontend
npm install
npm run dev
```

## 4. 데이터 초기 수집 (Ingest)

서버 실행 후, 데이터가 없는 상태에서는 지도가 비어 보일 수 있습니다. n8n 워크플로우를 사용하거나 직접 API를 호출하여 데이터를 채워야 합니다.

```bash
# 최신 분기 데이터 수집 예시
curl -X POST http://localhost:8000/api/ingest/sales \
  -H "X-Internal-Token: dev-internal-token" \
  -H "Content-Type: application/json" \
  -d '{"quarters": ["2024Q4"]}'
```

## 5. 트러블슈팅

*   **CORS 에러:** Backend의 `CORS_ORIGINS` 설정에 `http://localhost:5173`이 포함되어 있는지 확인하세요.
*   **ModuleNotFoundError:** `uvicorn` 실행 시 `--app-dir` 경로가 정확한지 확인하세요.
*   **DB 연결 실패:** Docker 컨테이너가 정상 실행 중인지(`docker ps`), 포트 `5432`가 점유되지 않았는지 확인하세요.
