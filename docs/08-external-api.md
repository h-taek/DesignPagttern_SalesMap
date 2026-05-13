# 08. 외부 데이터 API (OA-15572)

본 프로젝트는 **서울 열린데이터 광장**의 **OA-15572 — 상권분석서비스(추정매출-상권)** 한 가지 소스를 사용한다.

- 데이터셋: <https://data.seoul.go.kr/dataList/OA-15572/S/1/datasetView.do>
- 제공 형식: **Open API (XML/JSON)** + **CSV(zip) 다운로드**
- 라이선스: 공공누리 1유형 (출처 표시, 상업·변경 가능)
- 단위: 원
- 갱신 주기: 분기
- 그레인: `(상권, 분기, 서비스 업종)`

## 인증키 발급

1. <https://data.seoul.go.kr/together/guide/openApiManage.do> 에서 회원가입 후 인증키 신청.
2. 신청은 보통 즉시 승인. 인증키는 BE의 `.env`에 `OPEN_API_KEY`로 저장.

## 호출 방식

### 옵션 1. CSV 일괄 적재 (개발 초기에 권장)

- 데이터셋 페이지에서 zip 다운로드 → 압축 해제.
- `backend/scripts/load_csv.py`로 전체 적재. 인증키 불필요.
- 초기 개발과 학습용 데이터 확보에 적합.

### 옵션 2. Open API 호출 (n8n 배치에서 사용)

- 엔드포인트 (XML):
  ```
  http://openapi.seoul.go.kr:8088/{KEY}/xml/VwsmTrdarSelngQq/{START}/{END}/{YEAR_QUARTER}
  ```
- 엔드포인트 (JSON): `xml` 부분을 `json`으로 교체.
- `VwsmTrdarSelngQq`가 OA-15572의 서비스명.
- 한 번에 최대 1,000행. `START`/`END`로 페이지네이션 (`1/1000`, `1001/2000` …).
- `YEAR_QUARTER`는 `20244` 형식 (선택, 생략하면 전체).

> BE의 `SalesIngestService`는 옵션 2를 사용하지만, **옵션 1로 적재된 데이터와 같은 정규화 결과**가 나오도록 어댑터를 공유한다.

## 주요 원본 컬럼

데이터셋 페이지에 컬럼별 세부 정의는 게시되지 않으므로 CSV 헤더 기준으로 정리. 실제 헤더는 적재 스크립트에서 한 번 검증한다.

| 컬럼 (예시) | 의미 | 비고 |
|------|------|------|
| `STDR_YYQU_CD` (`기준_년_분기_코드`) | 예: `20244` (2024Q4) | `quarter`로 변환 |
| `TRDAR_SE_CD`, `TRDAR_SE_CD_NM` | 상권 구분 코드/명 | 골목/발달/전통/관광특구 |
| `TRDAR_CD`, `TRDAR_CD_NM` | 상권 코드/명 | 행정동 코드 조회 키 |
| `SVC_INDUTY_CD`, `SVC_INDUTY_CD_NM` | 서비스 업종 코드/명 | 100개 세부 업종 |
| `THSMON_SELNG_AMT` (`당월_매출_금액`) | **분기 합계 매출** (원) | 컬럼명에 "당월"이지만 OA-15572는 분기 단위 |
| `THSMON_SELNG_CO` (`당월_매출_건수`) | 분기 합계 결제 건수 | |
| 그 외 요일·시간대·성별·연령 분해 컬럼 | MVP 미사용 | |

## OA-15572 → `sales_record` 매핑

```
원본 1 행
  ├─ STDR_YYQU_CD            (20244)
  ├─ TRDAR_CD                (상권 코드)
  ├─ SVC_INDUTY_CD           (세부 업종 코드)
  ├─ THSMON_SELNG_AMT        (분기 매출)
  └─ THSMON_SELNG_CO         (분기 건수)
       │
       ▼  (1) 상권 → 행정동 → 자치구 환원
       │  (2) 세부 업종 → 대분류 매핑 (food/service/retail)
       │  (3) (자치구, 분기, 대분류) 그룹 SUM
       ▼
sales_record
  region_id, quarter='2024Q4', industry_category='food',
  total_sales=SUM(...), total_count=SUM(...)
```

### (1) 상권 → 자치구 매핑

- `TRDAR_CD` ↔ 행정동 코드 매핑이 OA-15572 단독으로는 없음.
- 보조 데이터셋 **"서울시 상권 영역 정보"** (`OA-15561` 또는 유사) 또는 빅데이터캠퍼스 제공 매핑표로 1회 적재.
- 또는 상권 좌표(`XCNTS_VALUE`, `YDNTS_VALUE`)를 자치구 GeoJSON과 point-in-polygon으로 매핑 (PostGIS 또는 Python `shapely`).
- 결과를 `region_dong_map` 혹은 별도 `trdar_region_map`에 저장.

MVP는 가장 단순한 길로 **공식 상권 영역 데이터셋 1회 다운로드 → CSV 매핑표**로 적재한다. 자세한 설정은 적재 스크립트 주석에서.

### (2) 세부 업종 → 대분류 매핑

`infra/db/industry_map.csv` 한 파일로 관리.

```
svc_induty_cd,svc_induty_cd_nm,industry_category
CS100001,한식음식점,food
CS100002,중식음식점,food
...
CS200001,일반의류,retail
...
CS300001,세탁소,service
...
```

규칙:
- OA-15572 코드 정의서 기준 외식업 10종 → `food`
- 서비스업 47종 → `service`
- 소매업 43종 → `retail`

운영 중 신규 업종 코드가 들어오면 매핑 누락으로 처리하고 `errors`에 누적 (응답 207).

### (3) 단위 검증

- 금액은 정수 원 단위로 보존. CSV가 문자열로 들어오면 콤마 제거 후 `BIGINT` 캐스팅.
- `NULL`, 음수, `0` 인 경우 분리해 통계 로깅 (학습 시 0 분기 비중을 봐야 함).

## `SalesIngestService` (BE) 구현 골격

```python
class SalesIngestService:
    def __init__(self, repo: SalesRepository, client: OpenApiClient,
                 industry_map: IndustryMap, region_resolver: RegionResolver):
        ...

    def run(self, quarters: list[str] | None,
            region_ids: list[int] | None,
            industries: list[str] | None) -> IngestResult:
        # 1. fetch (페이지네이션)
        rows = self.client.fetch_quarters(quarters)
        # 2. adapt (어댑터)
        adapted = (self._adapt_row(r) for r in rows)
        # 3. filter (regionIds / industries 지정 시)
        filtered = (a for a in adapted if self._keep(a, region_ids, industries))
        # 4. aggregate (region, quarter, industry) groupby sum
        aggregated = self._aggregate(filtered)
        # 5. upsert
        upserted = self.repo.upsert_many(aggregated)
        return IngestResult(...)
```

각 단계는 단위 테스트 가능하도록 분리. 어댑터·매핑은 디자인 패턴 적용 후보(Adapter, Facade).

## 적재 흐름 요약

```
[OA-15572 CSV/API]
      │
      ▼  fetch
[원본 행]
      │
      ▼  Adapter (1행 → 정규화 행)
[정규화 행: region_id, quarter, industry, sales, count]
      │
      ▼  groupby + SUM
[그룹 결과]
      │
      ▼  upsert (region_id, quarter, industry_category)
[sales_record]
```
