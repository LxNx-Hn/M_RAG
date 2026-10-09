# 학교 제출 양식 재검증

이 보고서는 수정 전 검토 기록이다. 이후 적용 결과는 [2026 양식 최종 검증 보고서](FINAL_SCHOOL_TEMPLATE_2026_AUDIT.md)를 참조한다.

검토일: 2026-10-10. 대상 HEAD: `12205d6dd878106634b38faad656a6ab657d8a25`.

## 판정

**현재 논문과 포스터는 학교 제출 양식에 맞추는 수정이 필요하다.** 기존 검증은 2025 양식의 정의 보존과 논문 자료 정합성을 확인했다. 이번 검토에서는 학교의 최신 공식 공지와 2026 HWP 원본, 실제 문단 적용값, 쪽번호, 포스터의 물리 크기를 대조했다.

논문 본문과 최종 HWPX·PDF, 다운로드의 포스터는 이번 검토에서 수정하지 않았다.

## 공식 자료

- [학교 최신 졸업논문 제출 공지](https://ce.dongguk.ac.kr/HOME/computer/sub.htm?mode=view&mv_data=aWR4PTE5NzAmc3RhcnRQYWdlPTAmbGlzdE5vPTEwNDUmdGFibGU9ZXhfYmJzX2RhdGFfY29tcHV0ZXImbmF2X2NvZGU9Y29tMTU4NzUyMTE1MCZjb2RlPUZmeDNVZ1k1NHoyVCZzZWFyY2hfaXRlbT0mc2VhcmNoX29yZGVyPSZvcmRlcl9saXN0PSZsaXN0X3NjYWxlPSZ2aWV3X2xldmVsPSZ2aWV3X2NhdGU9JnZpZXdfY2F0ZTI9): 등록일 2026-09-01. 공지 첨부에서 2026 HWP, 심사 신청서, A1 PPTX, 포스터 예시 PDF를 받아 확인했다.
- [2026 스타일 수정본 공지](https://ce.dongguk.ac.kr/HOME/computer/sub.htm?mode=view&mv_data=aWR4PTE5Njkmc3RhcnRQYWdlPTE4MCZsaXN0Tm89ODY1JnRhYmxlPWV4X2Jic19kYXRhX2NvbXB1dGVyJm5hdl9jb2RlPWNvbTE1ODc1MjExNTAmY29kZT1GZngzVWdZNTR6MlQmc2VhcmNoX2l0ZW09JnNlYXJjaF9vcmRlcj0mb3JkZXJfbGlzdD0mbGlzdF9zY2FsZT0mdmlld19sZXZlbD0mdmlld19jYXRlPSZ2aWV3X2NhdGUyPQ%3D%3D): 2026년 적용할 수정 양식임을 명시한다.
- 로컬 다운로드: 2025 HWP 양식 2개, 작성 참고자료 PDF, 심사 신청서, `M_RAG_B1_PRINT.pdf`.
- 비교 근거: `tmp/submission_format_review/FORMAT_AUDIT_DATA.json`, `2026_template_text.txt`, `official_notice.txt`, `official_sources.json`, 렌더 PNG.

## 논문

| 항목 | 확인한 사실 | 판정 |
|---|---|---|
| 용지·여백·단 | 2025/2026 원본과 현재 문서의 pagePr·colPr 일치. A4, 좌우 약 30mm, 상하 약 20mm | 일치 |
| 원본 스타일 정의 | 현재 문서의 19개 정의는 2025 HWP와 일치 | 기존 기준 통과 |
| 최신 스타일 | 2026 원본은 22개. 소절·그림위치·표위치·리스트 등의 정의 추가. 기존 장·절·그림제목의 문단 설정에도 ID 이외의 차이 존재 | 최신 양식 재적용 필요 |
| 실제 문단 속성 | 상위 문단 261개가 지정 스타일의 기본 paraPrIDRef와 다른 값을 사용. 이 수에는 표지 배치 문단도 포함되므로 261개 전부를 위반으로 세지 않는다. 본문·장·절·캡션에는 조판 정책에서 추가한 간격과 분할 속성이 적용됨 | 엄격한 원본 적용 재검토 필요 |
| 본문 간격 예 | 2025/2026 본문 원본은 문단 아래 5pt. 현재 body 정책은 4pt | 차이 확인 |
| 쪽번호 | 2026 양식은 ‘서론부터 1페이지’. 실제 최종 PDF의 서론(물리 9쪽) 하단은 `- 9 -` | 수정 필요 |
| 장별 새 쪽 | 현재 1~6장 시작 물리 쪽은 9,11,18,21,25,40. 장 시작 쪽 나눔 적용 | 일치 |
| 참고문헌 번호 | 양식은 첫 인용부터 1,2,3… 순서. 본문 첫 등장 순서는 1,2,3,4,5,6,7,8,12,9,10,11,13… | 번호 및 대응 인용 재정렬 필요 |
| 표·그림·수식 | 현재 검증에서 17개·22개·10개 통과. 표 제목 위/그림 제목 아래 구조 유지 | 통과 |
| 평가 자료 | 60질의×8조건=480기록, 원자료 해시와 원고 정합성 검사 통과 | 통과 |
| 표지·인준 | 개인·소속·날짜 미입력. 현재 2쪽에는 ‘제출 페이지’·‘인준 페이지’라는 문구가 나타나며 영문 논문 제목과 구분된 주심·부심 칸이 없다. 2026 원본은 국문·영문 제목과 주심·부심 칸을 둠 | 원본 문구·입력 위치 복원, 정보·날인 필요 |

스타일 정의를 보존하는 검사만으로 실제 적용값까지 학교 양식과 동일하다고 판정할 수 없다. 2026 템플릿 재적용 시 원고·실험 수치는 유지하고, 본문 표시 쪽번호와 목차를 함께 재생성해야 한다. 물리 PDF 페이지 인덱스와 인쇄된 쪽번호는 별도로 기록해야 한다.

## 포스터

`C:/Users/KiKi/Downloads/M_RAG_B1_PRINT.pdf`를 사용자가 대상 파일로 확인했다. PDF 실제 크기는 **707×1000mm**, 세로 1쪽이다. 공식 공지는 A1 슬라이드 1장이며, 학교 첨부 PPTX의 실제 크기는 **593.99×840.98mm**로 A1이다. 현재 B1 파일은 크기를 수정해야 한다.

공식 제출 파일은 논문 PDF, 포스터 PPT, 포스터 PDF의 3개다. 다운로드 폴더에서 현재 포스터의 편집 원본 PPT/PPTX를 찾지 못했다. 학교에서 받은 PPTX는 빈 예시 양식이며 현재 포스터의 원본이 아니다.

제목·배경·목적·실험 구성·시스템 흐름·결과·결론·참고문헌이 보인다. 핵심 수치 +0.0805, +0.0288, +0.2182, 전체 +0.2289는 현재 논문과 일치한다. 현재 포스터에는 학생명·학번·지도교수·소속 식별값이 없다. 학교 예시의 저자·소속 표시를 참고하여 확정 정보로 추가하는 것이 적절하며, 공지 본문에서 그 개별 항목의 필수 여부를 별도로 열거하지는 않았다.

단순 A1 축소 시 크기 비율은 약 0.841이다. 현재 12.2pt 참고문헌은 약 10.3pt가 되므로 최종 A1 PDF에서 다시 판독성을 검사해야 한다. PDF 내 맑은 고딕 글꼴 포함을 확인했으며, 포스터 실제 인쇄 시험은 수행하지 않았다.

## 제출 절차와 확정 정보

학교 최신 공지에 따르면 신청서 접수는 **2026-11-02~06 15시**, 심사 및 최종 파일 제출은 **2026-11-09~13 17시**이다. 최종 제출 구간의 첫날에 공지가 ‘화’로도 표기한 부분이 있어 날짜와 요일 표기가 충돌한다. 11월 9일은 월요일이므로 날짜 구간을 위처럼 기록하고, 실제 접수는 학과 확인이 필요하다. 사용자의 졸업 대상 학기는 아직 확인되지 않았다.

신청서는 본인 이름·서명, 허가원은 지도교수 성명·서명, 실험보고요약문은 내용을 요구한다. 논문 PDF에는 심사위원 날인이 필요하다. 공지의 신청 기간은 논문 표지의 제출일·인준일로 자동 전용하지 않는다.

사용자에게 성명, 학번, 학과, 대학/캠퍼스, 지도교수, 제출일·연도, 인준일, 심사위원을 질문했다. 아직 확정 답변을 받지 않았다. 질문에 대한 값이 오면 표지·인준·포스터에 동일하게 적용하고, 주심·부심과 실제 날인은 별도로 확인한다. 논문의 국문·영문 제목은 포스터 및 제출 이메일 내용과 일치시켜야 한다.

## 이번 실행 검사

```powershell
.venv-hwpx/Scripts/python.exe -X utf8 FINALDOCS/BUILD/probe_hwpx.py --template <다운로드 2025 HWP>
.venv-hwpx/Scripts/python.exe -X utf8 FINALDOCS/BUILD/probe_hwpx.py --template <공식 2026 HWP>
.venv-hwpx/Scripts/python.exe -X utf8 FINALDOCS/BUILD/verify_thesis_hwpx.py
.venv-hwpx/Scripts/python.exe -X utf8 FINALDOCS/VALIDATION/verify_finaldocs_60q.py
.venv-hwpx/Scripts/python.exe -X utf8 tmp/submission_format_review/audit_formats.py
```

모두 종료 코드 0. HWP 변환 보고서에 미변환·누락 항목 없음. 학교 원본을 변환한 후 XML 구조와 실제 파일 크기를 비교했고, 작성 참고자료·논문 표지·서론·참고문헌과 포스터 렌더를 확인했다. 현재 검증기의 PASS는 기존 2025 정의 및 자료 보존에 관한 결과이며, 이번에 확인한 2026 적용·본문 시작 쪽번호·첫 인용 순서의 적합성까지 포함하지 않는다.

이번 범위는 읽기와 검증 보고서 작성이다. 논문 재조판·A1 포스터 제작·개인 정보 입력·새로운 GitHub CI 실행은 수행하지 않았다.
