"""Create the thesis tables from the completed question analysis.

Result tables use one merged group row per comparison (evaluation language
and base → applied condition) followed by the four question types and the
60-question total. The JSON definition and the XLSX workbook are written
together; the HWPX builder reads the workbook.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, Side

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "FINALDOCS/ANALYSIS"))
from analyze_questions import (  # noqa: E402
    QUALITY_COMPARISONS,
    SCD_COMPARISONS,
    TYPES,
)  # noqa: E402

DOC_SHORT = {
    "Mi:dm K 2.5 Pro Technical Report": "Mi:dm",
    "RAG Survey": "RAG Survey",
    "CAD": "CAD",
    "RAPTOR": "RAPTOR",
}


def build():
    path = ROOT / "FINALDOCS/DATA/THESIS_TABLES_60Q.json"
    existing = {t["sheet"]: t for t in json.loads(path.read_text(encoding="utf-8"))}
    full = pd.read_csv(ROOT / "FINALDOCS/ANALYSIS/QUESTION_TYPE_SUMMARY.csv")
    summary = full[full.grouping.isin(["question_type", "전체"])].replace(
        {"level": {"전체 60개": "전체"}}
    )
    output = [existing[k] for k in ["T2-1_Related_Work", "T4-1_Environment"]]

    def row_for(typ, base, applied, metric):
        rows = summary[
            (summary.level == typ)
            & (summary.base == base)
            & (summary.applied == applied)
            & (summary.metric == metric)
        ]
        assert len(rows) == 1
        return rows.iloc[0]

    def group_label(lang, base, applied, measure, excluded=None):
        factors = [(1, "HyDE"), (3, "CAD"), (5, "SCD")]
        before = [name for i, name in factors if base[i] == "1"]
        added = [name for i, name in factors if base[i] == "0" and applied[i] == "1"]
        assert len(added) == 1
        if before:
            title = f"{'와 '.join(before)}에 {added[0]}를 추가했을 때의 {measure}"
        else:
            title = f"기법 미적용 상태에서 {added[0]}만 적용했을 때의 {measure}"
        explanation = []
        if lang:
            explanation.append(
                "영어 근거로 평가하였다."
                if lang == "영어"
                else "한국어로 번역한 근거로 평가하였다."
            )
        if excluded is not None:
            explanation.append(f"관련성 0점이 있는 질문 {excluded}개를 제외하였다.")
        return title + ("\n" + " ".join(explanation) if explanation else "")

    def make(sheet, title, metric, pairs):
        time = metric == "duration_seconds"
        header = [
            "질문 유형",
            "질문 수",
            "적용 전 시간" if time else "적용 전 평균",
            "적용 후 시간" if time else "적용 후 평균",
            "평균 변화량",
            "증가/감소/비슷" if time else "개선/악화/비슷",
        ]
        rows, merges, bold, scopes = [header], [], [], []
        for lang, base, applied in pairs:
            excluded = None
            if metric == "answer_relevancy":
                excluded = int(
                    row_for("전체", base, applied, metric).relevancy_zero_excluded
                )
            measure = {
                "answer_relevancy": "답변 관련성",
                "faithfulness": "근거 충실도",
                "korean_ratio": "한국어 문자 비율",
                "duration_seconds": "처리 시간",
            }[metric]
            label = group_label(lang, base, applied, measure, excluded)
            rows.append([label] + [""] * (len(header) - 1))
            merges.append([len(rows) - 1, 0, len(rows) - 1, len(header) - 1])
            scope = []
            for typ in TYPES + ["전체"]:
                r = row_for(typ, base, applied, metric)
                dig, suffix = (1, "초") if time else (3, "")
                rows.append(
                    [
                        "전체 60개" if typ == "전체" else typ.replace(" 및 ", "·"),
                        str(r.n),
                        f"{r.base_mean:.{dig}f}{suffix}",
                        f"{r.applied_mean:.{dig}f}{suffix}",
                        f"{r.mean_delta:+.{dig}f}{suffix}",
                        f"{r.improved}/{r.worse}/{r.similar}",
                    ]
                )
                if typ != "전체":
                    scope.append(len(rows) - 1)
            maximum = max(float(rows[i][3].removesuffix("초")) for i in scope)
            bold += [
                [i, 3] for i in scope if float(rows[i][3].removesuffix("초")) == maximum
            ]
            scopes.append({"rows": scope, "column": 3})
        if time:
            note = "같은 질문의 적용 전후 평균 시간과 차이(초). 굵은 값은 같은 비교의 네 유형 중 가장 긴 적용 시간이며, 시간은 짧을수록 비용이 작다. 차이 >1초 증가, <−1초 감소, 나머지 비슷함."
        else:
            note = "같은 유효 질문의 적용 전후 평균이며, 변화량은 적용 후 평균에서 적용 전 평균을 뺀 값이다. 굵은 값은 같은 비교의 네 유형 중 적용 평균 최댓값(동률 모두)이다. 차이 >0.05 개선, <−0.05 악화, 나머지 비슷함."
            if metric == "answer_relevancy":
                note += " 두 조건 중 하나라도 답변 관련성이 0점으로 기록된 질문은 평균과 개수에서 제외하였다."
        output.append(
            {
                "sheet": sheet,
                "title": title,
                "rows": rows,
                "merges": merges,
                "bold_cells": bold,
                "bold_scopes": scopes,
                "numeric_columns": [1, 2, 3, 4, 5],
                "column_fractions": [0.22, 0.11, 0.16, 0.16, 0.17, 0.18],
                "note": note,
            }
        )

    make(
        "T5-1_HyDE_Relevance",
        "표 5-1 HyDE 적용 전후의 유형별 답변 관련성",
        "answer_relevancy",
        [QUALITY_COMPARISONS[i] for i in [0, 4]],
    )
    make(
        "T5-2_CAD_Faithfulness",
        "표 5-2 CAD 적용 전후의 유형별 근거 충실도",
        "faithfulness",
        [QUALITY_COMPARISONS[i] for i in [1, 5]],
    )
    make(
        "T5-3_Combinations",
        "표 5-3 복수 기법 조합의 유형별 답변 관련성",
        "answer_relevancy",
        [QUALITY_COMPARISONS[i] for i in [2, 3, 6, 7]],
    )

    # Retrieval metrics for the same HyDE comparisons.
    header = [
        "질문 유형",
        "질문 수",
        "정밀도 적용 전",
        "정밀도 적용 후",
        "재현율 적용 전",
        "재현율 적용 후",
    ]
    rows, merges, bold, scopes = [header], [], [], []
    for lang, base, applied in [QUALITY_COMPARISONS[i] for i in [0, 4]]:
        rows.append([group_label(lang, base, applied, "검색 지표")] + [""] * 5)
        merges.append([len(rows) - 1, 0, len(rows) - 1, 5])
        scope = []
        for typ in TYPES + ["전체"]:
            cp, cr = row_for(typ, base, applied, "context_precision"), row_for(
                typ, base, applied, "context_recall"
            )
            rows.append(
                [
                    "전체 60개" if typ == "전체" else typ.replace(" 및 ", "·"),
                    str(cp.n),
                    f"{cp.base_mean:.3f}",
                    f"{cp.applied_mean:.3f}",
                    f"{cr.base_mean:.3f}",
                    f"{cr.applied_mean:.3f}",
                ]
            )
            if typ != "전체":
                scope.append(len(rows) - 1)
        for col in [3, 5]:
            maximum = max(float(rows[i][col]) for i in scope)
            bold += [[i, col] for i in scope if float(rows[i][col]) == maximum]
            scopes.append({"rows": scope, "column": col})
    output.append(
        {
            "sheet": "T5-4_HyDE_Retrieval",
            "title": "표 5-4 HyDE 적용 전후의 유형별 검색 지표",
            "rows": rows,
            "merges": merges,
            "bold_cells": bold,
            "bold_scopes": scopes,
            "numeric_columns": [1, 2, 3, 4, 5],
            "column_fractions": [0.22, 0.11, 0.17, 0.17, 0.16, 0.17],
            "note": "정밀도는 문맥 정밀도, 재현율은 문맥 재현율의 평균이다. 굵은 값은 같은 비교·지표의 네 유형 중 적용 평균 최댓값(동률 모두)이다.",
        }
    )
    make(
        "T5-5_Korean",
        "표 5-5 SCD 적용 전후의 유형별 한국어 문자 비율",
        "korean_ratio",
        [(None, b, a) for b, a in SCD_COMPARISONS],
    )
    make(
        "T5-6_Time",
        "표 5-6 단일 기법 적용 전후의 유형별 처리 시간",
        "duration_seconds",
        [(None, "H0C0S0", a) for a in ["H0C1S0", "H1C0S0", "H0C0S1"]],
    )

    # Appendix A with short document and type labels.
    questions = json.loads(
        (ROOT / "FINALDOCS/DATA/QUESTIONS_60Q.json").read_text(encoding="utf-8")
    )
    rows = [["질문 ID", "한국어 질문", "문서", "유형", "쪽", "정답 근거 구간"]]
    for q in questions:
        rows.append(
            [
                q["query_id"],
                q["query"],
                DOC_SHORT[q["document_label"]],
                q["question_type"].replace(" 및 ", "·"),
                str(q["source_page"]),
                q["answer_span"],
            ]
        )
    output.append(
        {
            "sheet": "Appendix_Queries",
            "title": "표 A-1 60개 질문의 대상 문서·유형·정답 근거",
            "rows": rows,
            "numeric_columns": [4],
            "column_fractions": [0.165, 0.295, 0.11, 0.12, 0.05, 0.26],
        }
    )

    path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    write_xlsx(output)
    contract_path = ROOT / "FINALDOCS/DATA/REVISION_CONTRACT_20261015.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    contract.update(tables=len(output), sheets=[t["sheet"] for t in output])
    contract_path.write_text(
        json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"PASS: {len(output)} tables written to JSON and XLSX")
    return output


def write_xlsx(tables):
    wb = Workbook()
    wb.remove(wb.active)
    thin = Side(style="thin", color="777777")
    for t in tables:
        ws = wb.create_sheet(t["sheet"])
        ws.sheet_view.showGridLines = False
        ws.cell(1, 1, t["title"])
        ws.cell(
            2,
            1,
            "Source: stored 60-question observations; question-aligned valid pairs; no imputation",
        )
        numeric = set(t.get("numeric_columns", []))
        bold = {tuple(x) for x in t.get("bold_cells", [])}
        for r, row in enumerate(t["rows"]):
            for c, value in enumerate(row):
                cell = ws.cell(r + 3, c + 1, str(value))
                cell.font = Font(
                    name="Malgun Gothic", size=10, bold=r == 0 or (r, c) in bold
                )
                cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)
                horizontal = (
                    "center" if r == 0 else ("right" if c in numeric else "left")
                )
                cell.alignment = Alignment(
                    horizontal=horizontal, vertical="center", wrap_text=True
                )
        for r0, c0, r1, c1 in t.get("merges", []):
            ws.merge_cells(
                start_row=r0 + 3, start_column=c0 + 1, end_row=r1 + 3, end_column=c1 + 1
            )
        for c in range(len(t["rows"][0])):
            ws.column_dimensions[chr(65 + c)].width = 20
        ws.freeze_panes = "A4"
    wb.save(ROOT / "FINALDOCS/TABLES/TABLES_60Q.xlsx")


if __name__ == "__main__":
    build()
