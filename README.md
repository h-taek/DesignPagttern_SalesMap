# SalesMap

서울시 소상공인 매출 및 예측 시각화 지도 시스템

지도 기반으로 서울시 자치구 25개의 업종별(외식/서비스/소매) **분기** 매출과 선형회귀 기반 **다음 분기 예측**을 함께 보여주는 시스템. 데이터 소스는 서울 열린데이터 광장 OA-15572 (상권분석서비스 추정매출-상권).

## 팀

정동욱, 이민욱, 신동현, 임형택

## MVP 구성

| 구분 | 구성 | 실행 환경 |
|------|------|-----------|
| Frontend | React | 로컬 dev 서버 |
| Backend API | FastAPI | 로컬 dev 서버 |
| AI 서버 | FastAPI + scikit-learn (선형회귀) | 로컬 dev 서버 |
| Database | PostgreSQL | Docker |
| 배치 스케줄러 | n8n | Docker |

전체 흐름은 [docs/02-architecture.md](docs/02-architecture.md), 실행 절차는 [GUIDELINE.md](GUIDELINE.md) 또는 [docs/06-dev-setup.md](docs/06-dev-setup.md) 참고.

## 디렉토리

```
SalesMap/
├── README.md
├── docs/                  # 설계/운영 문서
├── frontend/              # React 앱 (예정)
├── backend/               # FastAPI 백엔드 (예정)
├── ai/                    # FastAPI AI 서버 (예정)
├── infra/                 # docker-compose, n8n 워크플로우 (예정)
└── data/                  # 원천 CSV 등 (예정, gitignore)
```

## 문서

- [프로젝트 개요](docs/01-overview.md)
- [시스템 아키텍처](docs/02-architecture.md)
- [MVP 범위 및 단계](docs/03-mvp.md)
- [데이터 모델](docs/04-data-model.md)
- [API 명세](docs/05-api.md)
- [로컬 개발 환경](docs/06-dev-setup.md)
- [n8n 배치 예측](docs/07-batch-prediction.md)
- [외부 데이터 API (OA-15572)](docs/08-external-api.md)
- [Frontend 설계](docs/09-frontend.md)
- [디자인 패턴 적용](docs/10-design-patterns.md)
- [테스트 전략](docs/11-testing.md)
- [로깅·관측](docs/12-observability.md)
