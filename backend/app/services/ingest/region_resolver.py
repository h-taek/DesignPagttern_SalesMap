from app.repositories.sales import SalesRepository


class RegionResolver:
    """raw 한 행을 자치구 region_id로 환원.

    우선순위: 명시적 sgg_code → 행정동 코드(dong_code) → 상권코드(trdar_code) → 실패.
    OA-15572 API 원본에는 자치구·행정동 컬럼이 없고 TRDAR_CD(상권코드)만 있으므로,
    OA-15560(상권영역)에서 만든 region_trdar_map 으로 환원한다.
    CSV 적재 시에는 sgg_code 컬럼을 직접 넣어도 된다.
    """

    def __init__(self, repo: SalesRepository) -> None:
        self._by_sgg = repo.list_region_sgg()
        self._by_dong = repo.list_dong_map()
        self._by_trdar = repo.list_trdar_map()

    def resolve(
        self,
        sgg_code: str | None,
        dong_code: str | None,
        trdar_code: str | None = None,
    ) -> int | None:
        if sgg_code and sgg_code in self._by_sgg:
            return self._by_sgg[sgg_code]
        if dong_code and dong_code in self._by_dong:
            return self._by_dong[dong_code]
        if trdar_code and trdar_code in self._by_trdar:
            return self._by_trdar[trdar_code]
        return None
