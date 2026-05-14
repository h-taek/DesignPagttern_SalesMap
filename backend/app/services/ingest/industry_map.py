import csv
from pathlib import Path

from app.schemas import IndustryCategory


class IndustryMap:
    """OA-15572 서비스 업종 코드 → 대분류(food/service/retail) 매핑.

    인프라 측 CSV: infra/db/industry_map.csv
    """

    def __init__(self, mapping: dict[str, IndustryCategory]) -> None:
        self._m = mapping

    def get(self, svc_induty_cd: str) -> IndustryCategory | None:
        return self._m.get(svc_induty_cd)

    @classmethod
    def from_csv(cls, path: Path | str) -> "IndustryMap":
        mapping: dict[str, IndustryCategory] = {}
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(_skip_comments(f)):
                code = (row.get("svc_induty_cd") or "").strip()
                cat = (row.get("industry_category") or "").strip()
                if code and cat in ("food", "service", "retail"):
                    mapping[code] = cat  # type: ignore[assignment]
        return cls(mapping)


def _skip_comments(lines):
    for line in lines:
        if line.lstrip().startswith("#"):
            continue
        yield line
