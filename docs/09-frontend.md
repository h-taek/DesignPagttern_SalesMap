# 09. Frontend 설계

## 기술 선택

| 항목 | 선택 | 이유 |
|------|------|------|
| 빌드 | Vite + TypeScript | 빠른 HMR, 표준 React 셋업. |
| 지도 | **SVG 클릭맵** (라이브러리 없음) | 일러스트 스타일 지도 — 서울 25구를 SVG `<path>` 25개로. 타일맵의 도로/건물 정보가 불필요하고, path에 클릭·호버·선택색을 직접 줄 수 있어 Leaflet 의존성 제거. |
| 차트 | Recharts | React 친화, 분기 라벨/툴팁 간단. 차트 1~2종이면 충분. |
| 서버 상태 | `@tanstack/react-query` | 캐싱·재요청·로딩/에러 상태 일괄 처리. |
| 전역 상태 | **없음** | 선택된 `regionId`/`industry`는 컴포넌트 state(useState)로 보관. Zustand/Redux 불필요. |
| 스타일 | 인라인 스타일 | MVP는 컴포넌트별 인라인으로 충분. 확장 시 CSS Modules. |

## 디렉토리 구조

```
frontend/
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── api/
│   │   ├── client.ts          # fetch 래퍼 + 에러 매핑
│   │   ├── regions.ts         # GET /api/regions
│   │   └── sales.ts           # GET /api/regions/{id}/sales(+history)
│   ├── hooks/
│   │   ├── useRegionSales.ts  # React Query
│   │   └── useSalesHistory.ts
│   ├── components/
│   │   ├── MapView.tsx        # SVG 클릭맵 (path 25개)
│   │   ├── IndustryToggle.tsx # food/service/retail
│   │   ├── RegionPopup.tsx    # 팝업 컨테이너
│   │   ├── SalesSummary.tsx   # 최신 분기 + 예측 카드
│   │   └── SalesHistoryChart.tsx
│   ├── hooks/
│   │   ├── useRegions.ts
│   │   ├── useRegionSales.ts
│   │   └── useSalesHistory.ts
│   ├── assets/
│   │   └── seoul-districts.json  # 서울 25 구 SVG path + label
│   ├── types.ts               # API 응답 타입
│   └── vite-env.d.ts
├── index.html
├── package.json
└── vite.config.ts
```

## 상태 모델

- 단일 페이지. 선택 상태는 `App`의 `useState`로 보관:
  - `industry: Industry`, `selectedRegionId: number | null`
- React Query 키:
  - `['regions']`
  - `['region-sales', regionId, industry]`
  - `['sales-history', regionId, industry, quarters]`

## 사용자 인터랙션

```
페이지 로드
  └─ useRegions()  → sggCode→regionId 매핑 테이블 구성

SVG path(구) 클릭
  └─ setSelectedRegionId(regionId)   ← path의 sggCode를 매핑 테이블로 환원

selectedRegionId / industry 변경
  ├─ useRegionSales(regionId, industry) → 팝업의 SalesSummary
  └─ useSalesHistory(regionId, industry, 8) → SalesHistoryChart
```

## 컴포넌트 트리

```
<App>
 ├─ <IndustryToggle value=industry onChange=… />
 ├─ <MapView viewBox districts sggToRegionId selectedRegionId onSelect=… />
 └─ {selectedRegionId && (
       <RegionPopup regionId industry onClose=…>
         <SalesSummary data={sales} />
         <SalesHistoryChart series={history.series} />
       </RegionPopup>
    )}
```

## API 클라이언트

```ts
// src/api/client.ts
const BASE = import.meta.env.VITE_API_BASE_URL;

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, init);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(body?.error?.code ?? "UNKNOWN", body?.error?.message ?? res.statusText, res.status);
  }
  return res.json() as Promise<T>;
}
```

응답 타입은 [05-api](05-api.md)와 1:1로 일치하는 `types.ts`에 정의.

## 지도 자산 (`seoul-districts.json`)

일러스트 스타일 지도를 SVG path로 표현한다. 타일맵을 쓰지 않는다.

```json
{
  "viewBox": "0 0 1000 800",
  "districts": [
    { "sggCode": "11680", "regionName": "강남구", "path": "M ...", "label": [x, y] }
  ]
}
```

- `sggCode`로 BE의 `region` 테이블(`sgg_code`)과 조인 → `regionId` 환원.
- `path`: SVG path 데이터. `label`: 구 이름 표시 좌표.
- **데이터 확보**: 서울 25구 TopoJSON(`southkorea-maps`)을 Catmull-Rom 곡선화 및 무게중심(Centroid) 기반 라벨 배치를 통해 `frontend/scripts/build_districts.py`에서 생성.
- 현재 **서울 25개 자치구 전체**가 실제 경계 데이터 기반으로 구현되어 있음.
- `MapView`는 선택된 구의 `<path>` fill 색을 바꿔 강조하고, label은 `pointer-events:none`로 클릭을 path에 위임.

## 에러/빈 상태

- `prediction === null`: "예측 데이터가 아직 없습니다" 안내 (Activity Diagram의 분기).
- `NO_SALES_DATA` (422): "해당 업종 매출 데이터가 없습니다" 안내. `ApiError.code`로 분기.
- 지역 목록 로드 실패: 좌상단 패널에 백엔드 확인 안내.

## CORS / 개발 호스트

- BE의 `CORS_ORIGINS`에 `http://localhost:5173` 필수.
- 프로덕션 도메인이 생기면 `.env`로 분리.

## 비-MVP

- 동/상권 단위 드릴다운.
- 100개 세부 업종 필터.
- 다중 지역 비교 (지도 위 사이드 패널).
- 다크 모드.
