from dataclasses import dataclass

from app.schemas import IndustryCategory
from app.services.ingest.industry_map import IndustryMap
from app.services.ingest.region_resolver import RegionResolver


@dataclass(frozen=True)
class NormalizedRow:
    region_id: int
    quarter: str  # YYYYQn
    industry: IndustryCategory
    total_sales: int
    total_count: int | None


class AdaptError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


# OA-15572 표준 컬럼 이름. 적재 CSV가 약식 헤더를 쓸 수 있어 fallback도 둠.
_COL_QUARTER = ("STDR_YYQU_CD", "stdr_yyqu_cd", "quarter_raw")
_COL_INDUSTRY = ("SVC_INDUTY_CD", "svc_induty_cd")
_COL_SALES = ("THSMON_SELNG_AMT", "thsmon_selng_amt", "total_sales")
_COL_COUNT = ("THSMON_SELNG_CO", "thsmon_selng_co", "total_count")
_COL_SGG = ("SGG_CD", "sgg_code")
_COL_DONG = ("ADSTRD_CD", "adstrd_cd", "dong_code")


def _pick(raw: dict, keys: tuple[str, ...]) -> str | None:
    for k in keys:
        if k in raw and raw[k] not in (None, ""):
            return str(raw[k]).strip()
    return None


def _parse_quarter(s: str) -> str:
    s = s.strip()
    if len(s) == 5 and s.isdigit() and s[4] in "1234":
        return f"{s[:4]}Q{s[4]}"
    if len(s) == 6 and s[:4].isdigit() and s[4] == "Q" and s[5] in "1234":
        return s.upper()
    raise AdaptError("BAD_QUARTER", f"invalid quarter: {s!r}")


def _parse_amount(s: str) -> int:
    s = s.replace(",", "").strip()
    if s in ("", "-"):
        raise AdaptError("BAD_AMOUNT", "empty amount")
    return int(float(s))


class OpenApiRowAdapter:
    """OA-15572 원본 행 → NormalizedRow.

    실패는 None 반환 + 호출자가 errors로 누적. 예외는 던지지 않는다.
    """

    def __init__(self, industry_map: IndustryMap, region_resolver: RegionResolver) -> None:
        self._industry = industry_map
        self._region = region_resolver

    def adapt(self, raw: dict) -> NormalizedRow | tuple[None, str]:
        try:
            q = _parse_quarter(_pick(raw, _COL_QUARTER) or "")
            sales = _parse_amount(_pick(raw, _COL_SALES) or "")
            count = _pick(raw, _COL_COUNT)
            count_int = _parse_amount(count) if count else None
        except AdaptError as e:
            return None, f"{e.code}:{e.message}"

        svc_cd = _pick(raw, _COL_INDUSTRY)
        if not svc_cd:
            return None, "MISSING_INDUSTRY_CODE"
        industry = self._industry.get(svc_cd)
        if industry is None:
            return None, f"UNMAPPED_INDUSTRY:{svc_cd}"

        region_id = self._region.resolve(_pick(raw, _COL_SGG), _pick(raw, _COL_DONG))
        if region_id is None:
            return None, "UNMAPPED_REGION"

        return NormalizedRow(
            region_id=region_id,
            quarter=q,
            industry=industry,
            total_sales=sales,
            total_count=count_int,
        )
