# docs/

SalesMap 프로젝트 문서 모음. 발표 자료(`디자인패턴_중간발표.pdf`)의 설계를 기반으로 MVP 구현 기준으로 구체화한다.

## 문서 목록

| 번호 | 문서 | 내용 |
|------|------|------|
| 01 | [overview](01-overview.md) | 프로젝트 주제 / 동기 / 주요 기능 / 시나리오 |
| 02 | [architecture](02-architecture.md) | 컴포넌트 구성과 호출 흐름, 패턴 적용 |
| 03 | [mvp](03-mvp.md) | MVP 정의 / 완료 기준 / 마일스톤 |
| 04 | [data-model](04-data-model.md) | DB 스키마와 ORM 매핑 |
| 05 | [api](05-api.md) | Backend / AI 서버 API 명세 |
| 06 | [dev-setup](06-dev-setup.md) | 로컬 개발 환경 구성 절차 |
| 07 | [batch-prediction](07-batch-prediction.md) | n8n 배치 예측 워크플로우 |
| 08 | [external-api](08-external-api.md) | OA-15572 호출 방식, 컬럼 매핑, 업종/상권→구 매핑 |
| 09 | [frontend](09-frontend.md) | 라이브러리·컴포넌트 트리·데이터 페칭 |
| 10 | [design-patterns](10-design-patterns.md) | 패턴 적용 위치 표 (수업 산출물) |
| 11 | [testing](11-testing.md) | BE/AI 단위·통합 테스트 전략 |
| 12 | [observability](12-observability.md) | 로깅·요청 ID·n8n 실행 ID 추적 |

## 처음 보는 사람을 위한 읽기 순서

1. `01-overview` — 무엇을 만드는지.
2. `03-mvp` — 어디까지 만드는지.
3. `02-architecture` — 어떻게 구성되는지.
4. `06-dev-setup` — 어떻게 돌리는지.
5. 필요할 때 `04`, `05`, `07`을 참조.
