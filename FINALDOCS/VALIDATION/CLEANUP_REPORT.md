# 최종 제출 패키지 정리 결과

## A. 정리 이전 저장소

기준 HEAD `86a4a8d623201ee4bf925ae873513e8797b1dbd7`, 복구 annotated tag `pre-finaldocs-cleanup-20261018`. 원격에 복구 태그를 보존했다. main은 유지하며 `codex/finaldocs-cleanup-20261017`을 PR로 제출한다. 원래 추적 파일 1,242개, 297,192,456바이트(283.42MiB), VALIDATION 547개, BUILD 21개다. BUILD·VALIDATION 직접 Python 검사/생성 스크립트 24개, 테스트 파일 9개·테스트 메서드 68개였다. HISTORY 199개·41,585,622바이트와 검증 이미지 246개를 조사했다. 용량은 추적 작업 파일의 실제 바이트 합계이며 Git 객체·미추적 캐시는 제외한다.

## B. 실제 삭제 및 처리 결과

원본 1,242행 전수 감사는 [CLEANUP_FILES.csv](CLEANUP_FILES.csv)에 있다. 원래 SHA·역할·최근 Git 변경·참조/호출 위치·동일 해시 중복·처리·최종 위치·복구 커밋을 기록했다. 분류: DELETE 566개, GENERATE 70개, KEEP 577개, MERGE 29개. 아래 삭제 수는 이동 후 보존된 파일을 제외한 원본 경로 수다. MERGE와 GENERATE도 원본 중복 파일은 실제 삭제했다.

|경로|처리|삭제 파일 수|원본 바이트|근거|복구|
|---|---|---:|---:|---|---|
| `.github/workflows/` | 삭제/통합/재생성 | 4 | 11,481 | 파일별 의존성과 삭제 근거는 CLEANUP_FILES.csv 참조 | 복구 태그 |
| `FINALDOCS/BUILD/` | 삭제/통합/재생성 | 4 | 13,661 | 파일별 의존성과 삭제 근거는 CLEANUP_FILES.csv 참조 | 복구 태그 |
| `FINALDOCS/DELIVERY/` | 삭제/통합/재생성 | 73 | 1,764,553 | 파일별 의존성과 삭제 근거는 CLEANUP_FILES.csv 참조 | 복구 태그 |
| `FINALDOCS/FIGURES/` | 삭제/통합/재생성 | 16 | 2,516,040 | 파일별 의존성과 삭제 근거는 CLEANUP_FILES.csv 참조 | 복구 태그 |
| `FINALDOCS/MANUSCRIPT/` | 삭제/통합/재생성 | 2 | 26,174 | 파일별 의존성과 삭제 근거는 CLEANUP_FILES.csv 참조 | 복구 태그 |
| `FINALDOCS/POSTER/` | 삭제/통합/재생성 | 27 | 27,217,764 | 파일별 의존성과 삭제 근거는 CLEANUP_FILES.csv 참조 | 복구 태그 |
| `FINALDOCS/VALIDATION/` | 삭제/통합/재생성 | 339 | 46,280,645 | 파일별 의존성과 삭제 근거는 CLEANUP_FILES.csv 참조 | 복구 태그 |
| `FINALDOCS/VALIDATION/HISTORY/` | 삭제/통합/재생성 | 198 | 41,551,620 | Git 복구 가능한 중복 이력 | 복구 태그 |
| `cli/add_literature_figures_60q.py/` | 삭제/통합/재생성 | 1 | 25,330 | 파일별 의존성과 삭제 근거는 CLEANUP_FILES.csv 참조 | 복구 태그 |
| `cli/finalize_thesis_figures.py/` | 삭제/통합/재생성 | 1 | 18,337 | 파일별 의존성과 삭제 근거는 CLEANUP_FILES.csv 참조 | 복구 태그 |

이전 47·48·54쪽/중간 보고서·초록 유지·main 미병합 기록을 제거하고 현재 49쪽 판정만 CURRENT_AUDIT.md에 남겼다. 최신49쪽의 중복 PNG도 제거했으며 실제 PDF·해시·페이지지도와 render_pdf_qa.py는 보존했다. 과거 보고서 고유 전사·A→B·객체 매핑·문헌 검증·질의 작성 이력은 최종 근거 문서로 통합했다. 구 복사붙이기 TXT의 CRAG/BEIR20/MTEB21은 현재 원고의 Adaptive-RAG/BEIR19/MTEB20과 달라 삭제하고 원고 안의 표·수식 블록을 사용한다.

한 파일만 복구하려면 `git show pre-finaldocs-cleanup-20261018:<원래경로>`로 확인한 뒤 `git restore --source pre-finaldocs-cleanup-20261018 -- <원래경로>`를 실행한다. 복구 시 CSV의 원래 SHA와 대조한다. Git 이력 재작성·강제 푸시·git clean은 사용하지 않았다.

## C. 검증 코드와 테스트 통합

|기존|최종|보존 기능·중복 제거|검증|
|---|---|---|---|
|academic_language_checks, prose_audit_checks, submission_audit_checks|manuscript_checks.py|문장 승인·캡션/목록·상호참조·독립 도식 저자/출처·실제 삽입/해시 공통 모듈|통합 test_manuscript.py의 원래 변조 검사 유지|
|professor_acceptance_checks|manuscript_checks.py + ../BUILD/poster_checks.py|논문 초록 금지·S0/S1 순서·본문 인용 / 포스터 선택 초록·출처·프로토콜 책임 분리|초록 재삽입·그룹 혼합·인용 누락 검출|
|4개 문체/교수/학술/출처 테스트 파일|test_manuscript.py|4개 클래스 병합, 과거63항목 JSON 모양 검사 1개만 제거|기준 테스트 메서드 집합과 AST 직접 대조|
|분산 수동 명령|validate_all.py|8단계 실행·실패 종료1·단일 결과 JSON·추가 수동 확인 분리|70개 회귀 테스트 및 전체8단계 통과|
|기존 파일 SHA 목록·옛 보고서|ARTIFACT_MANIFEST.json + package_checks.py|317개 연구자료/마스터 무변경·실제49쪽 지도·A1 규격|해시·페이지지도·PPTX 크기 변조3개 추가|
|probe_hwpx, 57쪽 finalize_page_map, 옛 문헌/라벨 CLI|현재 verifier, map_pdf_pages, 교수 도식 생성기|학교 양식/목차/그림 실검사 보존, 오래된 보정 제거|템플릿으로 HWPX 재생성 후 재검사|

테스트 메서드 집합: 전 68, 후 70. 제거는 `ProfessorAcceptanceTests.test_63_manual_criteria_are_traceable` 하나이며 기존 교수 지시63개의 실제 문구와 출처는 PROFESSOR_FEEDBACK.md에 보존한다. 추가는 PackageMutationTests.test_a1_size_changed, PackageMutationTests.test_changed_file_hash, PackageMutationTests.test_page_map_caption_moved. 테스트 파일 9→7. 표값·숫자·그림·수식·참고번호·질의 누락/중복·통계 변조·해시·페이지지도·A1·숫자 정렬·초록 재삽입 검출을 유지한다. unittest의 표준 발견 방식으로 실행하며 오류를 0으로 대체하지 않는다.

일회성 workflow4개 삭제: final-thesis-validator-once(최근 성공2026-09-22/run35677607555), finalize-thesis-figures-once(성공/run35676658786), finalize-thesis-workbook-once(성공/run35677464801; 구17시트), thesis_literature_figures(실패2026-09-18/run35306356304). CI·HWPX·최종A1·서비스 이미지 게시4개는 유지한다. HWPX CI가 단일 통합 검증 후 임시 HWPX를 재생성해 검사하고 결과 JSON을 artifact로 제공한다.

## D. 최종 구조

```text
FINALDOCS/
  README.md
  MANUSCRIPT/  원고·한컴 전송 안내
  TABLES/      TABLES_60Q.xlsx
  DATA/        최종 통계 JSON·CSV
  FIGURES/     실제13그림·SVG·생성 출처
  EVIDENCE/    6실제 사례·원본 대응
  APPENDIX/    60질의·원문 증빙
  POSTER/FINAL/ PPTX·SVG·PDF·재생성 코드
  DELIVERY/    HWPX·49쪽 PDF·2026학교HWP/HWPX·페이지지도
  BUILD/       현재 생성기·학교/인쇄/정렬 검사
  VALIDATION/  통합 검사·핵심 테스트
    CURRENT_AUDIT.md / PROFESSOR_FEEDBACK.md
    REFERENCES.md / REFERENCES.json / RESEARCH_PROVENANCE.md
    ARTIFACT_MANIFEST.json / TEXT_REVIEW.json
    CLEANUP_REPORT.md / CLEANUP_FILES.csv
tmp/            재생성 로그·PNG·XLSX·HWPX·포스터ZIP (Git 제외)
```

`python -m FINALDOCS.VALIDATION.validate_all`이 단일 진입점이다. 재생성은 BUILD/README.md와 POSTER/FINAL/README.md를 따른다. 생성기 기본 출력은 tmp이며 최종 제출 원본을 덮어쓰지 않는다. .gitignore에 tmp·node_modules·렌더폰트·검사 sidecar·과거 로컬 캐시를 추가했다.

## E. 연구 원자료 보존

ARTIFACT_MANIFEST.json의 317개를 기준 전 raw SHA와 확인하고, Git의 CRLF 변환에 영향받는 텍스트는 LF 정규화 해시도 기록했다. 315개는 기준 해시와 같고, 학교2026 HWP 원본1개를 추가했으며, DATA/EXPERIMENT_60_VALIDATION.md 1개만 통합 문서의 경로를 수정했다(수치·원자료 변경 없음). 이 변경의 전후 해시와 사유도 manifest에 보존했다. experiments/results 249개·140,023,482바이트, source_papers 9개·21,171,523바이트 및 실제 실험 PDF4종이 모두 보존됐다. 질의60×8조건=480기록, RAGAS1915/1920 유효·5결측을 재검증했다. 주요 대응차이 HyDE +0.080495, CAD +0.028838, SCD 주비교 +0.218224/전체 +0.228941 및 38요인검정·10대응비교·SD·Holm·효과크기를 원정밀도에서 독립 재현했다. 동일영문 문맥 주비교120쌍과 전체240쌍의 독립 단위는 모두 질의60이다.

현재 XLSX14시트를 임시 경로로 재생성해 원본과 시트 순서·모든 비어있지 않은 1257개 셀 값/형식상 자료형·셀 범위·병합을 직접 대조했다. 6사례 그림·7개 교수 도식·포스터도 임시 출력으로 재생성 성공했다. 제출 PDF의 6사례는 현재 원본 픽셀과 일치하며 최소9pt, 부록60행360셀과 반복 머리글 검사를 통과했다. 새 생성/평가 모델 호출은 없다.

## F. 제출 산출물

아래 파일은 경로 정리 외 내용 변경이 없으며 정리 전 raw SHA-256과 일치한다. 원고·모든 사용 그림·편집 수식11개도 보존했다.

|경로|SHA-256|
|---|---|
| `FINALDOCS/DELIVERY/GRADUATION_REPORT_60Q_FINAL.hwpx` | `9d06b46ff158442623a626f77236a5f50f9a5d7cf326f0d0452e2053b1ad6af0` |
| `FINALDOCS/DELIVERY/GRADUATION_REPORT_60Q_FINAL.pdf` | `9025c6901914d00d0b0ce624f01d8d9d50026af787815827d7c62164dbab5b8d` |
| `FINALDOCS/TABLES/TABLES_60Q.xlsx` | `b08d0cb615d35d68a780239f3cea9c39d91aa9d07ae4e04521ba49070e761fb6` |
| `FINALDOCS/POSTER/FINAL/M_RAG_A1_FINAL_EDITABLE.pptx` | `b82a8c8b3a6e8419dff094e9c2d415ba78f42830b83b03467bb31d6b0b2ee2ce` |
| `FINALDOCS/POSTER/FINAL/M_RAG_A1_FINAL_EDITABLE.svg` | `d2c643dab302070a33564993b5d911935acb219ae6fb4c59d4ba901fbeff5ecb` |
| `FINALDOCS/POSTER/FINAL/M_RAG_A1_FINAL_PRINT.pdf` | `2400bad9fd9533c7f8154df7c1bc70545c2f5545bc7728d2629f8da524be8ed7` |

논문49쪽·표14/1229셀·그림13·수식11·문헌22편·모델M1/M2·문서D1~D4·학교2026양식22개 명명 스타일·서론1쪽 시작이 유지된다. 포스터594×841mm·PPTX1슬라이드4편집표·159셀/88숫자 정렬·209텍스트의 PPTX/SVG/PDF 일치 및 참고문헌을 확인했다. 학교2026 HWP 원본도 기존 검증된 로컬 원본에서 추가했다.

## G. 교수 피드백과 추가 확인

PROFESSOR_FEEDBACK.md에 시간별 실제 전사와 추가 지시·관찰/추론을 구분하고 A→B36개·이전39/현재27객체·질문18개를 통합했다. 논문 국·영문초록 삭제 필수와 포스터 선택 초록을 구분한다. 배경/필요성·질의작성 근거·전체결과·평균SD·대응t/ANOVA·가독성·정식출판 검증은 현재 원고/자료 위치로 추적한다. 질의초안/LLM요약의 보존 한계와 최종60질의/원문 대조 증빙은 RESEARCH_PROVENANCE.md에 구분했다. 그림5-2 RAPTOR의 질문·검색·답변·점수는 원자료와 일치해 수정하지 않았다.

개인 제출본은 저장소 외부에 유지한다. 인준일·주심·부심·서명·날인은 미정이므로 빈칸이며 제출일2026.10.15는 유지한다. 실물 인쇄·A1 거리/색상·설치형PowerPoint 실행은 추가 확인 필요다. 한컴독스 웹에서 이미 확정한 제출 원본은 이번 정리에서 재조판하지 않았다.

기존 미추적 `VALIDATION/build_hwp_transfer_docx.py`·폰트/inspect 캐시는 사용자 파일로 REVIEW이며 커밋하지 않는다. HISTORY의 미추적 node_modules 캐시 재귀 삭제는 자동 승인 검토가 정책상 거부했고 상세 사유는 제공되지 않았다. 우회하지 않고 로컬에 남겼다. 따라서 추적 HISTORY 복사본 삭제와 로컬 디스크 캐시 정리를 구분한다.

## H. 검증과 CI

로컬 명령: `python -m FINALDOCS.VALIDATION.validate_all`(8단계·70테스트), 템플릿 HWPX 재생성/검사, 포스터 rebuild_exports.py 임시 재생성, BUILD/VALIDATION Python 컴파일·Ruff·Black, 두 MJS 문법검사, 경로/import 참조 검사를 수행한다. 결과 JSON은 tmp/finaldocs/validation에 생성하고 CI에서는 submission-validation artifact로 제공한다.

정리 커밋의 CI 결과는 이 브랜치의 PR과 정확한 HEAD에서 확인한다: [브랜치 PR 찾기](https://github.com/LxNx-Hn/M_RAG/pulls?q=is%3Apr+head%3Acodex%2Ffinaldocs-cleanup-20261017), [해당 브랜치 Actions](https://github.com/LxNx-Hn/M_RAG/actions?query=branch%3Acodex%2Ffinaldocs-cleanup-20261017). 본 문서는 자기 커밋 SHA를 고정할 수 없으므로 확정 SHA·각 run URL·성공 여부는 최종 전달 기록에 제공한다. main86a4의 이전 성공을 정리 커밋 성공으로 사용하지 않는다. main 병합은 이번 요청 범위가 아니다.

## I. 정리 효과

|지표|전|후|감소|
|---|---:|---:|---:|
|추적 파일 수|1242|594|648|
|파일 바이트 합계|297,192,456|179,661,309|117,531,147|
|VALIDATION 파일|547|25|522|
|검증 PNG/JPG|246|0|246|
|직접 Python 검사/생성 스크립트|24|19|5|
|테스트 파일|9|7|2|
|실제 테스트 메서드|68|70|핵심 보존·변조3개 추가|
|연구 원자료·제출 원본|317보호파일|315동일해시+1학교원본추가+1문서경로수정|0연구자료손실|

통계는 최종 문서 자체 크기가 안정화된 후 재측정했다. 파일별 복구는 CSV 하나로 찾고, 현재 판정·교수대응·출처·연구경계를 각각 한 문서로 관리한다. 단일 검증 명령과 임시 출력으로 중복 보고서 및 생성물의 재추적을 줄였다. 서비스 코드·생성/검색/평가 실행 경로는 보존한다.
