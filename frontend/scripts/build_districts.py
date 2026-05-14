"""서울 25개 자치구 TopoJSON → 부드러운 SVG path (seoul-districts.json) 변환.

입력:  scripts/seoul_municipalities_topo.json
        출처: github.com/southkorea/seoul-maps (KOSTAT 2013, topo_simple — 토폴로지 보존 단순화본)
출력:  src/assets/seoul-districts.json

왜 TopoJSON인가:
- 인접 자치구가 공유하는 경계선은 TopoJSON의 같은 arc 하나로 저장된다.
- arc 단위로 곡선화(Catmull-Rom)하면 공유 경계가 한 번만 부드러워지므로
  양쪽 구가 동일한 곡선을 공유 → 구 사이에 틈/겹침이 생기지 않는다.
- GeoJSON을 구별로 따로 단순화/곡선화하면 공유 경계가 어긋나 틈이 생긴다.

좌표: 경위도를 viewBox 좌표계로 선형 투영 (경도는 cos(위도) 보정).
코드: properties.name(구 이름)으로 행정안전부 표준 시군구 코드 매핑.

실행: python3 frontend/scripts/build_districts.py   (표준 라이브러리만 사용)
"""

import json
import math
from pathlib import Path

# 구 이름 → 행정안전부 표준 시군구 코드 (infra/db/init.sql 의 region seed 와 일치)
SGG_CODE = {
    "종로구": "11110", "중구": "11140", "용산구": "11170", "성동구": "11200",
    "광진구": "11215", "동대문구": "11230", "중랑구": "11260", "성북구": "11290",
    "강북구": "11305", "도봉구": "11320", "노원구": "11350", "은평구": "11380",
    "서대문구": "11410", "마포구": "11440", "양천구": "11470", "강서구": "11500",
    "구로구": "11530", "금천구": "11545", "영등포구": "11560", "동작구": "11590",
    "관악구": "11620", "서초구": "11650", "강남구": "11680", "송파구": "11710",
    "강동구": "11740",
}

W = 1000
PAD = 50
SMOOTH_SAMPLES = 12  # arc 한 세그먼트당 Catmull-Rom 보간점 수

# 라벨(무게중심) 미세 조정이 필요한 구의 viewBox 좌표 오프셋.
LABEL_OFFSET = {
    "11110": (-17.0, 0.0),  # 종로구 — 왼쪽으로 약간 이동
    "11140": (0.0, 0.0),    # 중구
    "11470": (0.0, 10.0),    # 양천구 — 아래로 약간 이동
}

_HERE = Path(__file__).resolve().parent
_SRC = _HERE / "seoul_municipalities_topo.json"
_OUT = _HERE.parent / "src" / "assets" / "seoul-districts.json"


# ---- TopoJSON 디코딩 ------------------------------------------------------

def decode_arcs(topo: dict) -> list[list[tuple[float, float]]]:
    """delta-encoded arcs → 절대 경위도 좌표 arc 리스트."""
    sx, sy = topo["transform"]["scale"]
    tx, ty = topo["transform"]["translate"]
    arcs = []
    for arc in topo["arcs"]:
        x = y = 0
        ring = []
        for dx, dy in arc:
            x += dx
            y += dy
            ring.append((x * sx + tx, y * sy + ty))
        arcs.append(ring)
    return arcs


def assemble_ring(arc_indices: list[int], arcs: list) -> list[tuple[float, float]]:
    """arc 인덱스 목록을 하나의 ring 좌표열로 조립. 음수 인덱스는 역방향 arc."""
    coords: list[tuple[float, float]] = []
    for idx in arc_indices:
        seg = arcs[idx] if idx >= 0 else arcs[~idx][::-1]
        coords.extend(seg if not coords else seg[1:])
    return coords


# ---- arc 곡선화 (Catmull-Rom) ---------------------------------------------

def _catmull_rom(p0, p1, p2, p3, t):
    t2 = t * t
    t3 = t2 * t
    x = 0.5 * (
        2 * p1[0]
        + (-p0[0] + p2[0]) * t
        + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
        + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3
    )
    y = 0.5 * (
        2 * p1[1]
        + (-p0[1] + p2[1]) * t
        + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
        + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3
    )
    return (x, y)


def smooth_arc(arc: list, samples: int = SMOOTH_SAMPLES) -> list[tuple[float, float]]:
    """arc(열린 곡선)를 Catmull-Rom 보간으로 촘촘하게. 양 끝점은 보존되어
    인접 arc와의 연결점이 어긋나지 않는다."""
    if len(arc) < 3:
        return list(arc)
    ext = [arc[0]] + list(arc) + [arc[-1]]
    out: list[tuple[float, float]] = []
    for i in range(len(ext) - 3):
        p0, p1, p2, p3 = ext[i], ext[i + 1], ext[i + 2], ext[i + 3]
        for s in range(samples):
            out.append(_catmull_rom(p0, p1, p2, p3, s / samples))
    out.append(arc[-1])
    return out


# ---- 라벨 위치 (polylabel) -------------------------------------------------

def ring_area(ring: list) -> float:
    a = 0.0
    for i in range(len(ring) - 1):
        x0, y0 = ring[i]
        x1, y1 = ring[i + 1]
        a += x0 * y1 - x1 * y0
    return a * 0.5


def ring_centroid(ring: list) -> tuple[float, float]:
    a = ring_area(ring)
    if abs(a) < 1e-12:
        xs = [p[0] for p in ring]
        ys = [p[1] for p in ring]
        return sum(xs) / len(xs), sum(ys) / len(ys)
    cx = cy = 0.0
    for i in range(len(ring) - 1):
        x0, y0 = ring[i]
        x1, y1 = ring[i + 1]
        cross = x0 * y1 - x1 * y0
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    return cx / (6 * a), cy / (6 * a)


# ---- main ------------------------------------------------------------------

def main() -> None:
    topo = json.loads(_SRC.read_text(encoding="utf-8"))
    raw_arcs = decode_arcs(topo)
    smooth_arcs = [smooth_arc(a) for a in raw_arcs]
    geometries = topo["objects"]["seoul_municipalities_geo"]["geometries"]

    # 투영 파라미터 — 곡선화된 좌표 기준 bbox (Catmull-Rom 살짝 overshoot 대비)
    pts = [p for arc in smooth_arcs for p in arc]
    lons = [p[0] for p in pts]
    lats = [p[1] for p in pts]
    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)

    kx = math.cos(math.radians((min_lat + max_lat) / 2))
    lon_span = (max_lon - min_lon) * kx
    lat_span = max_lat - min_lat
    inner_w = W - 2 * PAD
    inner_h = inner_w * lat_span / lon_span
    H = inner_h + 2 * PAD

    def project(lon: float, lat: float) -> tuple[float, float]:
        x = PAD + (lon - min_lon) * kx / lon_span * inner_w
        y = PAD + (max_lat - lat) / lat_span * inner_h
        return x, y

    def ring_path(ring: list) -> str:
        pts_ = (project(lon, lat) for lon, lat in ring)
        return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_) + " Z"

    districts = []
    for g in geometries:
        name = g["properties"]["name"]
        if name not in SGG_CODE:
            raise SystemExit(f"unmapped district name: {name!r}")

        # Polygon: arcs = [[outer ring arc indices], [hole arc indices], ...]
        smooth_rings = [assemble_ring(ri, smooth_arcs) for ri in g["arcs"]]
        raw_rings = [assemble_ring(ri, raw_arcs) for ri in g["arcs"]]

        path = " ".join(ring_path(r) for r in smooth_rings)
        # 라벨은 면적이 가장 큰 ring의 무게중심(centroid)에 둔다.
        outer = max(raw_rings, key=lambda r: abs(ring_area(r)))
        cx, cy = ring_centroid(outer)
        lx, ly = project(cx, cy)
        dx, dy = LABEL_OFFSET.get(SGG_CODE[name], (0.0, 0.0))
        lx += dx
        ly += dy

        districts.append(
            {
                "sggCode": SGG_CODE[name],
                "regionName": name,
                "path": path,
                "label": [round(lx, 1), round(ly, 1)],
            }
        )

    districts.sort(key=lambda d: d["sggCode"])
    out = {
        "_comment": (
            "서울 25개 자치구 SVG path (TopoJSON arc 단위 Catmull-Rom 곡선화 — 구 사이 틈 없음). "
            "출처: github.com/southkorea/seoul-maps (KOSTAT 2013 topo_simple). "
            "sggCode는 행정안전부 표준 시군구 코드. "
            "재생성: python3 frontend/scripts/build_districts.py"
        ),
        "viewBox": f"0 0 {W} {round(H)}",
        "districts": districts,
    }
    _OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {_OUT} — {len(districts)} districts, viewBox={out['viewBox']}")


if __name__ == "__main__":
    main()
