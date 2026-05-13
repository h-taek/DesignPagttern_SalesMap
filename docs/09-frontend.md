# 09. Frontend 설계

## 기술 선택

| 항목 | 선택 | 이유 |
|------|------|------|
| 빌드 | Vite + TypeScript | 빠른 HMR, 표준 React 셋업. |
| 지도 | Leaflet + `react-leaflet` | 가볍고, 한국어 자료 풍부. GeoJSON 폴리곤 렌더링이 핵심이라 벡터 타일까지는 불필요. |
| 차트 | Recharts | React 친화, 분기 라벨/툴팁 간단. 차트 1~2종이면 충분. |
| 서버 상태 | `@tanstack/react-query` | 캐싱·재요청·로딩/에러 상태 일괄 처리. |
| 전역 상태 | **없음** | 선택된 `regionId`/`industry`는 URL 쿼리스트링으로 보관. Zustand/Redux 불필요. |
| 스타일 | CSS Modules 또는 Tailwind | 팀 취향에 맡김. MVP는 기본 CSS Modules로 충분. |

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
│   │   ├── MapView.tsx        # 지도 + 폴리곤
│   │   ├── IndustryToggle.tsx # food/service/retail
│   │   ├── RegionPopup.tsx    # 팝업 컨테이너
│   │   ├── SalesSummary.tsx   # 최신 분기 + 예측 카드
│   │   └── SalesHistoryChart.tsx
│   ├── assets/
│   │   └── seoul-gu.geojson   # 서울 25 구 폴리곤
│   ├── types.ts               # API 응답 타입
│   ├── routes/                # (단일 페이지라 미사용 가능)
│   └── styles/
├── index.html
├── package.json
└── vite.config.ts
```

## 상태 / 라우팅 모델

- 단일 페이지. URL 쿼리스트링으로 선택 상태 보관:
  - `?regionId=1&industry=food`
- 새로고침/공유 시 같은 셀을 재현 가능.
- React Query 키:
  - `['regions']`
  - `['region-sales', regionId, industry]`
  - `['sales-history', regionId, industry, quarters]`

## 사용자 인터랙션

```
페이지 로드
  └─ useQuery(['regions'])  → GeoJSON과 매칭해 폴리곤 색칠 (선택사항: 최신 매출로 단계 색)

구 폴리곤 클릭
  └─ setSearchParams({ regionId, industry })

쿼리스트링 변경
  ├─ useRegionSales(regionId, industry) → 팝업의 SalesSummary
  └─ useSalesHistory(regionId, industry, 8) → SalesHistoryChart
```

## 컴포넌트 트리

```
<App>
 ├─ <IndustryToggle value=industry onChange=… />
 ├─ <MapView geojson regions onSelect=(id)=>setParam("regionId", id) />
 └─ {regionId && (
       <RegionPopup>
         <SalesSummary data={sales} prediction={sales.prediction} />
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

## GeoJSON 출처

- 후보: `southkorea-maps` (GitHub 공개, MIT 또는 동등 라이선스로 추정 — 라이선스 파일 재확인 후 채택).
- 좌표계: WGS84 (EPSG:4326). Leaflet 기본.
- `region_name` 또는 `sgg_code`로 BE의 `region` 테이블과 조인. GeoJSON properties에 `SIG_CD`(5자리 시군구 코드)가 들어있으면 그대로 `sggCode`와 매칭.
- 파일 크기: 25 구만 추리면 수십 KB. 정적 자산으로 번들.

## 에러/빈 상태

- `regionId`만 있고 `prediction === null`: "예측 데이터 없음" 안내 (Activity Diagram의 분기).
- `NO_SALES_DATA` (422): "해당 업종 매출 데이터 없음" 안내.
- 네트워크 에러: React Query 자동 재시도 + 토스트.

## CORS / 개발 호스트

- BE의 `CORS_ORIGINS`에 `http://localhost:5173` 필수.
- 프로덕션 도메인이 생기면 `.env`로 분리.

## 비-MVP

- 동/상권 단위 드릴다운.
- 100개 세부 업종 필터.
- 다중 지역 비교 (지도 위 사이드 패널).
- 다크 모드.
