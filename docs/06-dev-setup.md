# 06. 로컬 개발 환경

MVP는 다음과 같이 동작한다:

- **Docker**: PostgreSQL, n8n
- **로컬 dev 서버**: Frontend (Vite), Backend (Uvicorn), AI 서버 (Uvicorn)

## 사전 요구사항

| 도구 | 버전 (권장) |
|------|------------|
| Docker Desktop | 최신 |
| Node.js | 20.x |
| pnpm 또는 npm | pnpm 9 / npm 10 |
| Python | 3.11+ |
| uv 또는 venv | (택1) |

## 디렉토리 구조 (목표)

```
SalesMap/
├── infra/
│   ├── docker-compose.yml         # postgres + n8n
│   ├── db/
│   │   ├── init.sql               # 스키마 DDL
│   │   └── seed.sql               # 시드 데이터
│   └── n8n/
│       └── workflows/             # 워크플로우 JSON export
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI entry
│   │   ├── api/                   # 라우터 (SalesController)
│   │   ├── services/              # SalesService, PredictionService
│   │   ├── repositories/          # SalesRepository, PredictionRepository
│   │   ├── models.py              # SQLAlchemy 모델
│   │   └── schemas.py             # Pydantic
│   ├── pyproject.toml
│   └── .env.example
├── ai/
│   ├── app/
│   │   ├── main.py                # FastAPI entry (port 8100)
│   │   ├── predictor.py           # LRModel + PredictionGenerateService
│   │   └── repositories.py        # DB 접근 (backend와 공유 가능)
│   ├── pyproject.toml
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── App.tsx
    │   ├── components/MapView.tsx
    │   ├── components/RegionPopup.tsx
    │   └── api/client.ts
    ├── package.json
    └── .env.example
```

## 환경변수 (`.env.example` 초안)

### `backend/.env.example`
```
DATABASE_URL=postgresql+psycopg://salesmap:salesmap@localhost:5432/salesmap
CORS_ORIGINS=http://localhost:5173
INTERNAL_TOKEN=dev-internal-token
# 서울 열린데이터 광장 인증키 (OA-15572)
OPEN_API_KEY=발급받은_키
OPEN_API_BASE=http://openapi.seoul.go.kr:8088
```

### `ai/.env.example`
```
DATABASE_URL=postgresql+psycopg://salesmap:salesmap@localhost:5432/salesmap
INTERNAL_TOKEN=dev-internal-token
```

### `frontend/.env.example`
```
VITE_API_BASE_URL=http://localhost:8000
```

> `INTERNAL_TOKEN`은 BE/AI/n8n에 동일 값 사용. n8n에는 credential로 별도 등록.

## 실행 순서

### 1. 인프라 기동 (Postgres + n8n)

```bash
cd infra
docker compose up -d
```

- Postgres: `localhost:5432` (user/pass: `salesmap`/`salesmap`)
- n8n: `http://localhost:5678`
- 최초 기동 시 `infra/db/init.sql`이 자동 실행되어 스키마 생성, `seed.sql`로 시드 적재.

### 2. Python venv (한 번만, 레포 루트)

backend/ai는 **루트의 단일 `.venv`를 공유**한다.

```bash
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt -r ai/requirements.txt
```

### 3. Backend

```bash
cp backend/.env.example backend/.env
.venv/bin/uvicorn app.main:app --reload --port 8000 --app-dir backend
```

- Swagger: `http://localhost:8000/docs`

### 4. AI 서버

```bash
cp ai/.env.example ai/.env
.venv/bin/uvicorn app.main:app --reload --port 8100 --app-dir ai
```

- Swagger: `http://localhost:8100/docs`
- 동작 확인: `curl -X POST http://localhost:8100/predict/batch -H 'Content-Type: application/json' -d '{}'`

### 5. Frontend

```bash
cd frontend
pnpm install   # 또는 npm install
cp .env.example .env.local
pnpm dev
```

- 브라우저: `http://localhost:5173`

### 6. n8n 워크플로우

자세한 절차는 [07-batch-prediction.md](07-batch-prediction.md) 참고.

## docker-compose 초안 (`infra/docker-compose.yml`)

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: salesmap
      POSTGRES_PASSWORD: salesmap
      POSTGRES_DB: salesmap
    ports: ["5432:5432"]
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./db/init.sql:/docker-entrypoint-initdb.d/01-init.sql:ro
      - ./db/seed.sql:/docker-entrypoint-initdb.d/02-seed.sql:ro

  n8n:
    image: n8nio/n8n:latest
    environment:
      N8N_PORT: 5678
      GENERIC_TIMEZONE: Asia/Seoul
    ports: ["5678:5678"]
    volumes:
      - n8n_data:/home/node/.n8n

volumes:
  pgdata:
  n8n_data:
```

> n8n 컨테이너에서 호스트의 AI 서버(`localhost:8100`)를 호출할 때는 `host.docker.internal:8100`을 사용한다 (macOS/Windows 기준).

## 자주 부딪히는 이슈

- **CORS**: Backend의 `CORS_ORIGINS`에 Frontend dev origin이 빠지면 브라우저에서 차단된다.
- **iCloud 경로**: 프로젝트가 iCloud 동기화 폴더 안에 있으므로 Docker 볼륨/Node `node_modules`로 인한 동기화 지연 가능. `data/`, `node_modules/`, `pgdata/`는 `.gitignore` + iCloud 제외 권장.
- **포트 충돌**: 위 5개 포트가 모두 비어있어야 한다.
