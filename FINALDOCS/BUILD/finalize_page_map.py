"""Record the visual heading review of the initial 57-page Hancom PDF.

Overrides are release evidence, never page-zero/default substitutions.
Re-review and replace this evidence when input content/layout changes.
"""

import json
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "DELIVERY/PAGE_MAP_60Q.json"
data = json.loads(path.read_text(encoding="utf-8"))
if (
    data["pdf_sha256"]
    != "947461661d1656d21ee00ea32dfe0681ba7179f1c8a0657f118b9d33dbac40c9"
    or data["pdf_pages"] != 57
):
    raise ValueError(
        "These visual overrides apply only to the reviewed initial PDF; review a new export independently"
    )
reviewed = {
    "2.7 관련 연구와 본 연구의 위치": 17,
    "4.2 시스템 구성": 23,
    "4.3 시스템 구현": 24,
    "5.4 HyDE 결과 및 해석": 29,
    "5.6 SCD 출력 언어 결과 및 해석": 34,
    "5.9 연구의 한계": 41,
    "6. 결론": 42,
    "6.2 실험 설계가 제공한 의미": 42,
    "6.3 적용 시 실험 조건 선택": 43,
    "6.4 제한점과 후속 연구": 43,
    "참고문헌": 44,
    "B.2 문서별·질문 유형별 탐색 분석": 54,
    "부록 A~B": "46, 53",
}
data["pages"].update(reviewed)
data["unresolved"] = []
data["visual_overrides"] = reviewed
data["visual_review"] = (
    "All 57 rendered pages inspected on 2026-10-08; headings with missing PDF text mapping resolved visually"
)
path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
