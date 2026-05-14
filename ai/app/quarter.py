"""분기 코드(YYYYQn) ↔ 정수 인덱스 변환.

인덱스 = year * 4 + (n - 1). 회귀 학습의 x축으로 사용.
"""


def to_index(q: str) -> int:
    if len(q) != 6 or q[4] != "Q" or q[5] not in "1234":
        raise ValueError(f"invalid quarter: {q!r}")
    year = int(q[:4])
    n = int(q[5])
    return year * 4 + (n - 1)


def from_index(idx: int) -> str:
    year, rem = divmod(idx, 4)
    return f"{year}Q{rem + 1}"


def next_quarter(q: str) -> str:
    return from_index(to_index(q) + 1)
