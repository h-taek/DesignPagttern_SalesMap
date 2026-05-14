# GUIDELINE

SalesMap 프로젝트 작업·협업 가이드. 짧고 실용 위주.

## 1. 처음 한 번만

### 1-1. 사전 요구사항

| 도구 | 권장 버전 |
|------|-----------|
| Docker Desktop | 최신 |
| Node.js | 20.x (frontend용) |
| pnpm | 9.x (`npm i -g pnpm`) |
| Python | **3.11 권장** (3.14는 일부 ML 패키지 wheel 미흡) |
| Git | 최신 |

> 본 레포는 macOS + iCloud Drive 안에 있다. `node_modules`, `.venv`, Docker 볼륨은 동기화 대상이 아니어야 한다. `.gitignore`로 제외되어 있고, iCloud는 폴더별로 동기화 제외가 어렵다면 적어도 폴더를 자주 동기화시키지 말 것.

### 1-2. 레포 클론 & 환경변수

```bash
git clone https://github.com/h-taek/DesignPagttern_SalesMap.git SalesMap
cd SalesMap

# 환경변수 파일 복사 (필요시 값 수정)
cp backend/.env.example backend/.env
cp ai/.env.example ai/.env
# (Frontend는 Phase 4에서 추가)
```

### 1-3. Python venv (로컬 dev)

```bash
# backend
cd backend && python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cd ..

# ai
cd ai && python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cd ..
```

3.14에서 `scikit-learn`/`pandas`/`numpy`가 빌드 실패하면 Python 3.11을 별도로 설치해 `python3.11 -m venv .venv`로 재생성하거나, **AI 서버는 Docker로만 돌린다**.

## 2. 매일 동작

Docker로 띄우는 것은 외부 의존 서비스(DB, n8n)뿐. backend / ai / frontend는 각자 로컬 dev 서버로 실행한다.

```bash
# 1. 인프라 기동 (한 번만)
cd infra
docker compose up -d            # postgres + n8n

# 2. backend (별도 터미널)
cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000

# 3. ai (별도 터미널)
cd ai && .venv/bin/uvicorn app.main:app --reload --port 8100

# 4. frontend (별도 터미널, Phase 4 이후)
cd frontend && pnpm dev
```

### 빠른 확인

```bash
curl http://localhost:8000/healthz   # {"status":"ok","service":"backend"}
curl http://localhost:8100/healthz   # {"status":"ok","service":"ai"}
# DB
docker exec -it salesmap-db psql -U salesmap -d salesmap -c "SELECT COUNT(*) FROM region;"
# n8n
open http://localhost:5678
```

## 3. 디렉토리 약속

```
SalesMap/
├── docs/             # 설계·운영 문서 (변경 시 PR에서 같이 갱신)
├── infra/            # docker-compose, db init/seed, n8n workflow JSON
├── backend/          # FastAPI 백엔드 (사용자 조회 + ingest)
├── ai/               # FastAPI AI 서버 (예측 배치)
├── frontend/         # React + Vite (Phase 4)
├── GUIDELINE.md      # ← 본 문서
└── README.md
```

각 서비스 폴더 내부 구조는 [docs/02-architecture.md](docs/02-architecture.md) 의 "디렉토리 구조" 참고.

## 4. 작업 규칙

### 브랜치

- 메인: `main`
- 작업: `feat/<짧은-슬러그>`, `fix/<…>`, `docs/<…>`
- 멤버별 prefix는 안 씀 (PR author로 추적).

### 커밋 메시지

Conventional Commits 약식:

```
feat(backend): add /api/regions endpoint
fix(ai): handle empty training set
docs(04): update sales_record schema
chore(infra): bump postgres to 16.2
```

본문(선택)은 **왜** 위주. 줄 길이 72자.

### PR

- PR 1개 = 1가지 변경. 50~300 line diff 권장.
- `docs/`에 영향이 가는 변경이면 같은 PR에서 docs도 갱신.
- 리뷰 없으면 24h 후 self-merge 가능. 단, CI(있으면) 통과 필수.

### 코드 스타일

- Python: `ruff` + `black` 사용 권장 (셋업 후 결정). type hint 적극.
- TypeScript: ESLint + Prettier 기본 셋업.
- import 정렬, 미사용 변수 제거 등은 도구가 강제.

## 5. 환경변수 / 비밀값

- 실제 값은 `.env`에만 두고 절대 커밋 금지 (`.gitignore`에 포함됨).
- 새 변수를 추가하면 같은 PR에서 `.env.example`도 갱신.
- `INTERNAL_TOKEN`은 BE/AI/n8n에 같은 값. n8n에는 credential로 등록.

## 6. 문서 갱신 원칙

> 코드가 docs를 바꿔야 하면, 그 PR에서 같이 바꾼다.

- 새 엔드포인트 → `05-api.md`
- DB 스키마 변경 → `04-data-model.md`
- 배치 흐름 변경 → `02-architecture.md`, `07-batch-prediction.md`
- 새 외부 의존성 → `06-dev-setup.md`, `08-external-api.md`

문서 인덱스는 [docs/README.md](docs/README.md).

## 7. 자주 부딪히는 이슈

| 증상 | 원인 / 해결 |
|------|------------|
| BE/AI에서 DB 접속 실패 | DB가 아직 healthcheck 통과 전이거나 컨테이너 미기동. `docker compose ps`로 상태 확인. 호스트에서는 `localhost:5432`로 접속. |
| n8n 컨테이너에서 BE/AI 호출이 connection refused | n8n은 컨테이너, BE/AI는 호스트 로컬이므로 n8n의 HTTP 노드 URL을 `host.docker.internal:8000` / `:8100`으로. Linux는 compose에 `extra_hosts: ["host.docker.internal:host-gateway"]` 추가. |
| CORS 차단 | `backend/.env`의 `CORS_ORIGINS`에 frontend dev origin 추가. |
| Python 3.14에서 `scikit-learn` install 실패 | Python 3.11로 venv 재생성 또는 AI는 Docker로만 실행. |
| iCloud 동기화로 IO 느림 | `.venv`/`node_modules`/`pgdata` 폴더는 iCloud 동기화 제외(가능하면). 최소한 자주 변경되는 동안 동기화를 일시 정지. |

## 8. 다음 작업 진입점

- 진행 중인 작업: [docs/03-mvp.md](docs/03-mvp.md) 마일스톤 M1~M5 참고.
- 본격 코드를 채우기 전 항상 관련 docs 읽기.
