"""OA-15560 / OA-15572에서 ingest용 매핑 파일 2종을 재생성한다.

생성물:
  infra/db/industry_map.csv      서비스 업종 코드 → 대분류 (food/service/retail)
  infra/db/02-seed-trdar-map.sql 상권코드 → 자치구 (region_trdar_map INSERT)

OA-15572(추정매출-상권)에는 자치구 컬럼이 없고 TRDAR_CD(상권코드)만 있다.
OA-15560(상권영역, TbgisTrdarRelm)이 TRDAR_CD ↔ SIGNGU_CD 매핑을 제공하므로
이걸로 상권 → 자치구 환원 테이블을 만든다.

업종 대분류는 코드 prefix 규칙(CS1=외식, CS2=서비스, CS3=소매)을 따른다 —
2024Q4 실데이터 62종 전수 검수로 규칙이 성립함을 확인했다.

실행: backend/.venv/bin/python backend/scripts/build_maps.py
      (OPEN_API_KEY 가 backend/.env 에 있어야 함)
"""

import csv
import json
import urllib.request
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_ENV = _ROOT / "backend" / ".env"
_INDUSTRY_CSV = _ROOT / "infra" / "db" / "industry_map.csv"
_TRDAR_SQL = _ROOT / "infra" / "db" / "02-seed-trdar-map.sql"
_BASE = "http://openapi.seoul.go.kr:8088"

_CATEGORY = {"1": "food", "2": "service", "3": "retail"}


def _read_key() -> str:
    for line in _ENV.read_text(encoding="utf-8").splitlines():
        if line.startswith("OPEN_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("OPEN_API_KEY not found in backend/.env")


def _fetch_all(key: str, service: str, suffix: str = "") -> list[dict]:
    out: list[dict] = []
    start = 1
    while True:
        end = start + 999
        url = f"{_BASE}/{key}/json/{service}/{start}/{end}{suffix}"
        with urllib.request.urlopen(url, timeout=60) as resp:
            payload = json.load(resp)[service]
        rows = payload.get("row") or []
        out.extend(rows)
        if len(rows) < 1000:
            return out
        start += 1000


def main() -> None:
    key = _read_key()

    # OA-15560 상권영역 → trdar_code → sgg_code
    relm = _fetch_all(key, "TbgisTrdarRelm")
    trdar_map = {r["TRDAR_CD"]: r["SIGNGU_CD"] for r in relm}

    # OA-15572 추정매출 → distinct 업종코드
    selng = _fetch_all(key, "VwsmTrdarSelngQq", "/20244")
    industries = {r["SVC_INDUTY_CD"]: r["SVC_INDUTY_CD_NM"] for r in selng}

    with _INDUSTRY_CSV.open("w", newline="", encoding="utf-8") as f:
        f.write("svc_induty_cd,svc_induty_cd_nm,industry_category\n")
        f.write("# OA-15572 서비스 업종 코드 → 대분류 (food / service / retail).\n")
        f.write("# 출처: OA-15572 VwsmTrdarSelngQq 실데이터의 distinct 업종코드.\n")
        f.write("# 규칙: CS1=외식(food), CS2=서비스(service), CS3=소매(retail). "
                "재생성: backend/scripts/build_maps.py\n")
        writer = csv.writer(f)
        for code in sorted(industries):
            writer.writerow([code, industries[code], _CATEGORY[code[2]]])

    with _TRDAR_SQL.open("w", encoding="utf-8") as f:
        f.write("-- 상권코드(OA-15560 TbgisTrdarRelm) → 자치구 매핑. "
                "재생성: backend/scripts/build_maps.py\n")
        f.write("BEGIN;\n")
        f.write("INSERT INTO region_trdar_map (trdar_code, region_id)\n")
        f.write("SELECT v.trdar_code, r.region_id FROM (VALUES\n")
        f.write(",\n".join(f"  ('{tc}','{trdar_map[tc]}')" for tc in sorted(trdar_map)))
        f.write("\n) AS v(trdar_code, sgg_code)\n")
        f.write("JOIN region r ON r.sgg_code = v.sgg_code\n")
        f.write("ON CONFLICT (trdar_code) DO NOTHING;\n")
        f.write("COMMIT;\n")

    print(f"industry_map.csv      — {len(industries)} 업종")
    print(f"02-seed-trdar-map.sql — {len(trdar_map)} 상권")


if __name__ == "__main__":
    main()
