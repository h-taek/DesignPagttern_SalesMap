"""OA-15572 CSV 일괄 적재.

외부 API 인증키 없이 개발을 시작하기 위한 스크립트.
같은 SalesIngestService 어댑터를 재사용하므로 결과는 /api/ingest/sales 와 동일.

사용:
    .venv/bin/python backend/scripts/load_csv.py <csv_path>

CSV는 OA-15572 표준 헤더(STDR_YYQU_CD, SVC_INDUTY_CD, THSMON_SELNG_AMT ...) 또는
약식 헤더(quarter_raw, svc_induty_cd, total_sales, total_count, sgg_code|dong_code)를
사용할 수 있다. (adapter._COL_* 참고)
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import SessionLocal  # noqa: E402
from app.services.ingest.service import SalesIngestService  # noqa: E402


def main(csv_path: str) -> None:
    path = Path(csv_path)
    if not path.exists():
        raise SystemExit(f"file not found: {path}")

    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    with SessionLocal() as session:
        service = SalesIngestService(session)
        result = service.run(rows=rows, source=f"csv:{path.name}")

    print(
        f"processed={result.processed_rows} accepted={result.accepted_rows} "
        f"upserted={result.upserted_rows} failed={result.failed_rows}"
    )
    if result.errors:
        print(f"sample errors: {result.errors[:5]}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python backend/scripts/load_csv.py <csv_path>")
    main(sys.argv[1])
