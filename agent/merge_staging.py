"""수집 후보 통합·균형 리포트 (#180).

여러 질의로 나눠 수집한 staging CSV를 하나로 합치고, **골든셋에 넣기 전에
반드시 봐야 할 두 가지**를 보고한다.

1. **판정 균형.** 위험만 잔뜩 모으면 리콜은 부풀고 정밀도는 못 잰다.
   실제로 공정위 경로만 돌렸을 때 297건 중 295건(99%)이 위험이었다.
2. **검수 우선순위.** 추론으로 판정한 것, 신호가 섞인 것, 조항 문구가 없는 것을
   앞에 세운다. 검수자의 시간은 유한하고, 틀릴 가능성이 큰 것부터 봐야 한다.

사용법: cd agent && python merge_staging.py [--out merged.csv]
"""

import argparse
import csv
import re
from collections import Counter
from pathlib import Path

from collect_cases import is_clause_like

STAGING = Path(__file__).parent.parent / "data" / "staging"
REPO = STAGING.parent.parent
LEDGER = STAGING / "review_ledger.csv"


def _clause_key(text: str) -> str:
    """review_pipeline과 같은 중복 키를 만든다."""
    return re.sub(r"\s+", "", text)[:60]


def _golden_keys() -> set[str]:
    keys: set[str] = set()
    for path in sorted((REPO / "data").glob("real_clause_labels*.csv")):
        for row in csv.DictReader(path.open(encoding="utf-8")):
            key = _clause_key(row.get("clause_text", ""))
            if key:
                keys.add(key)
    return keys


def _ledger_verdicts() -> dict[str, str]:
    if not LEDGER.exists():
        return {}
    return {
        row["clause_key"]: row["verdict"]
        for row in csv.DictReader(LEDGER.open(encoding="utf-8"))
    }


def review_status_for(
    row: dict,
    golden_keys: set[str],
    ledger: dict[str, str],
) -> str:
    """후보의 실제 상태를 골든셋·검수 장부와 대조해 반환한다.

    수집 시점의 `review_status=미검수`는 이후 검수 결과를 반영하지 못한다.
    원문이 없는 후보는 자동 검수 대상도 아니므로 별도로 표시한다.
    """
    text = (row.get("clause_text") or row.get("clause_text_candidate") or "").strip()
    if not text:
        return "원문확보필요"
    key = _clause_key(text)
    if key in golden_keys:
        return "골든셋"
    if key in ledger:
        return f"검수완료:{ledger[key]}"
    return "미검수"

# 검수 우선순위 — 숫자가 작을수록 먼저 본다.
def _priority(row: dict) -> int:
    src = row.get("opinion_source", "")
    if "혼재" in src:
        return 0                       # 판정이 뒤집힐 수 있다
    if "추론" in src:
        return 1                       # 원문 확인 필수
    if not row.get("clause_text") and not row.get("clause_text_candidate"):
        return 2                       # 조항 문구를 사람이 찾아야 한다
    if row.get("confidence") == "낮음":
        return 3
    return 4


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="merged_candidates.csv")
    args = ap.parse_args()

    files = sorted(f for f in STAGING.glob("candidates_*.csv"))
    if not files:
        print("staging에 후보 파일이 없다.")
        return

    rows, cols = [], []
    for f in files:
        for r in csv.DictReader(f.open(encoding="utf-8")):
            r["_source_file"] = f.name
            rows.append(r)
            for c in r:
                if c not in cols:
                    cols.append(c)

    # 이미 수집된 파일에도 조항 여부 검사를 적용한다 — 재수집 없이 정리하기
    # 위해서다. 판례 경로에서만 서술문 조각이 섞이므로 그쪽만 본다.
    dropped = 0
    filtered = []
    for r in rows:
        text = r.get("clause_text", "")
        if text and "prec" in r.get("_source_file", "") and not is_clause_like(text):
            dropped += 1
            continue
        filtered.append(r)
    rows = filtered

    # 같은 조항 문구가 여러 질의에서 잡히는 것을 합친다.
    seen, merged = set(), []
    for r in rows:
        key = (r.get("clause_text") or r.get("clause_text_candidate")
               or r.get("rationale", "")[:200])
        if key in seen:
            continue
        seen.add(key)
        merged.append(r)

    merged.sort(key=_priority)
    golden_keys = _golden_keys()
    ledger = _ledger_verdicts()
    for row in merged:
        row["review_status"] = review_status_for(row, golden_keys, ledger)

    out = STAGING / args.out
    with out.open("w", encoding="utf-8", newline="") as fh:
        # Git에서 파일 전체가 바뀐 것처럼 보이지 않도록 LF를 고정한다.
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for r in merged:
            w.writerows([{c: r.get(c, "") for c in cols}])

    lv = Counter(r.get("gold_risk_level_candidate") or "(미상)" for r in merged)
    has_text = sum(bool(r.get("clause_text") or r.get("clause_text_candidate"))
                   for r in merged)
    print(f"파일 {len(files)}개 · 서술문 조각 {dropped}행 제외 "
          f"· 중복 제거 후 {len(merged)}행")
    print(f"저장: {out}\n")
    print(f"판정 후보 분포: {dict(lv)}")
    print(f"조항 문구 확보: {has_text}/{len(merged)} "
          f"({has_text / len(merged) * 100:.0f}%)")
    print(f"실제 검수 상태: {dict(Counter(r['review_status'] for r in merged))}")

    risky = lv.get("위험", 0) + lv.get("주의", 0)
    safe = lv.get("안전", 0)
    if risky and safe / max(risky, 1) < 0.5:
        print(f"\n⚠️ 균형 경고: 위험·주의 {risky} vs 안전 {safe}.")
        print("   이대로 골든셋에 넣으면 리콜은 부풀고 정밀도는 못 잰다.")
        print("   안전 표본을 더 모을 것:")
        print("     python collect_cases.py --target prec --query <검색어> "
              "--section 2 --verdict safe")
        print("   법원까지 갔는데 유효 판정을 받은 조항이 특히 값지다 —")
        print("   '위험해 보이지만 유효한 경계 사례'라 오탐 측정에 직접 쓰인다.")

    print("\n검수 우선순위 상위 (틀릴 가능성이 큰 것부터):")
    for r in merged[:5]:
        text = (r.get("clause_text") or r.get("clause_text_candidate") or "(문구 없음)")
        print(f"  [{r.get('opinion_source', '')[:16]:16s}] "
              f"{(r.get('gold_risk_level_candidate') or '?'):3s} {text[:56]}")


if __name__ == "__main__":
    main()
