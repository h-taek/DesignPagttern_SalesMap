from app.repositories.sales import SalesRepository


class RegionResolver:
    """raw 한 행을 자치구 region_id로 환원.

    우선순위: 명시적 sgg_code → 행정동 코드(dong_code) → 실패.
    OA-15572 자체는 상권 단위라 행정동/구가 직접 들어있지 않을 수 있으므로,
    CSV 적재 시 사용자가 sgg_code 컬럼을 추가하거나 보조 매핑을 채워야 한다.
    """

    def __init__(self, repo: SalesRepository) -> None:
        self._by_sgg = repo.list_region_sgg()
        self._by_dong = repo.list_dong_map()

    def resolve(self, sgg_code: str | None, dong_code: str | None) -> int | None:
        if sgg_code and sgg_code in self._by_sgg:
            return self._by_sgg[sgg_code]
        if dong_code and dong_code in self._by_dong:
            return self._by_dong[dong_code]
        return None
