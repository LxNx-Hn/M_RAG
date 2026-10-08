# 졸업논문 최종 제출 감사

검토일: 2026-10-09 (KST). 시작 HEAD: `edde589b8434b3ecea919ba1143600326a10a4a6`. `git fetch origin` 후 main과 origin/main이 이 SHA에서 일치함을 확인했다. 논문 본문·실험 결과를 보존하고 문헌 그림의 출처·재사용 근거, 명확한 문장 오류, 실제 웹한글 조판을 검토하였다.

## Git 확정 기록

논문 산출물 확정·전체 CI 검증 HEAD: `150353a7129dc6c62206ded4f085f8f2e5ae7b81`. 아래 실행은 이 SHA를 정확히 대상으로 모두 성공했다. 보고서 자체의 커밋 SHA는 파일 내용에 자기 자신의 SHA를 넣을 수 없으므로 `git log -1 --format=%H -- FINALDOCS/VALIDATION/FINAL_SUBMISSION_AUDIT.md`로 식별한다. 마지막 저장소 HEAD는 최종 사용자 보고와 `git rev-parse HEAD`로 확인한다. 보고서 확정 커밋은 논문 산출물 바이트를 변경하지 않는다.

## 문헌 그림 6개

| 그림 | 저자·정확한 버전·원 객체 | 최종 상태 | 사용 파일 |
|---|---|---|---|
| 2-1 | Patrick Lewis 외 / NeurIPS 2020, concept reference only / Figure 1 (concept only) | INDEPENDENT_DIAGRAM | [fig2_1_rag_independent.png](../FIGURES/LITERATURE/fig2_1_rag_independent.png) |
| 2-2 | Nelson F. Liu 외 / TACL 2024, 12:157–173; PDF page 2 (printed 158) / Figure 1 | CC_BY_4_0 | [fig2_2_lost_middle_tacl.png](../FIGURES/LITERATURE/fig2_2_lost_middle_tacl.png) |
| 2-3 | Luyu Gao 외 / ACL 2023, 1762–1777; PDF page 2 (printed 1763) / Figure 1 | CC_BY_4_0_ADAPTED | [fig2_3_hyde_acl_no_logo.png](../FIGURES/LITERATURE/fig2_3_hyde_acl_no_logo.png) |
| 2-4 | Weijia Shi 외 / NAACL 2024 short, PDF page 1 / Figure 1 | CC_BY_4_0 | [fig2_4_cad_original.png](../FIGURES/LITERATURE/fig2_4_cad_original.png) |
| 2-5 | Bo Li 외 / arXiv:2511.09984v1, PDF page 1 / Figure 1 | CC_BY_4_0_ADAPTED | [fig2_5_scd_no_logos.png](../FIGURES/LITERATURE/fig2_5_scd_no_logos.png) |
| 2-6 | Shahul Es 외 / arXiv:2309.15217v2, PDF page 8 / Table 2 | CC_BY_4_0 | [fig2_6_ragas_faithfulness_original.png](../FIGURES/LITERATURE/fig2_6_ragas_faithfulness_original.png) |

RAG는 NeurIPS 공식 원고와 [저작권 안내](https://neurips.cc/FAQ)를 조사했으나 원 그림 재사용 허락을 확인하지 못했다. 저자가 권리를 보유한다는 안내와 arXiv 배포 허락을 제3자의 그림 재사용 허락으로 간주하지 않았다. 원 그림을 재사용하지 않는 독립 데이터 흐름 도식으로 교체하였다. 기존 발췌 파일은 이력으로 보존한다.

Lost in the Middle은 TACL 정식 출판본(동일 DOI `10.1162/tacl_a_00638`)의 ACL 공식 PDF 첫 쪽에 CC BY 4.0을 확인했다. MIT Press 상세 페이지는 도구에서 열리지 않아 페이지 확인 완료로 표시하지 않았다. ACL 공식 출판본과 기존 arXiv 그림을 나란히 대조하여 20개 문서 위치, 두 곡선·범례·축·닫힌 책 기준선이 일치함을 확인했다. 파일 바이트는 다른 출판본·발췌 범위 때문에 다르다.

HyDE는 ACL 2023 정식 PDF의 저작권·CC BY 4.0 문구를 확인했다. 기존 arXiv와 도식의 질의·가상 문서·Contriever·실제 문서·범례가 일치한다. 원 영문 설명에는 arXiv의 GPT-3와 정식 출판본의 InstructGPT 차이가 있어 설명 문단을 제외한 도식 영역만 사용했다. 제3자 OpenAI 로고는 생략하고 GPT 글자와 흐름은 유지했다. SCD에는 확대 검토에서 OpenAI·Ollama 로고가 확인되어 두 로고만 생략하고 모델 라벨·흐름·예시를 유지했다.

CAD는 NAACL 2024 정식 PDF, SCD는 arXiv:2511.09984v1, RAGAS는 arXiv:2309.15217v2의 표 2를 사용했다. 각 정확한 버전의 CC BY 4.0을 확인했다. RAGAS 원 객체는 그림이 아닌 표 2임을 유지한다. [ACL 저작권 안내](https://aclanthology.org/faq/copyright/)의 제3자 자료 예외를 반영하여 로고에 본문 라이선스를 일괄 적용하지 않았다. 본문 출처는 저자·참고문헌 번호·PDF URL·[CC BY 4.0 링크](https://creativecommons.org/licenses/by/4.0/)·발췌 및 생략 내역을 표시한다.

정확한 PDF SHA-256, PNG SHA-256, 출처 문단, 라이선스 근거 URL은 [SUBMISSION_PROVENANCE.json](../FIGURES/LITERATURE/SUBMISSION_PROVENANCE.json)에 있다. 기존 Lost/HyDE 비교 이미지는 [LITERATURE_COMPARISON](LITERATURE_COMPARISON/)에 있다. 사용한 6개 그림의 권리 검토는 이 파일·버전·변경 범위에 한정한다. 이전에 사용하지 않게 된 RAG 발췌의 허락은 미확정 이력으로 남기며 현재 제출 그림의 미해결 항목으로 세지 않는다.

## 학술 문장과 주장 검토

국문초록·영문초록, 1~6장 전체와 캡션·출처·참고문헌·부록을 독해했다. 영어 논문에 한국어로 질문할 때 생기는 문제를 출발점으로 삼으며 HyDE·CAD·SCD는 기존 기법의 적용·비교 실험으로 유지한다. 신규 알고리즘 제안이나 모든 평가 지표의 보편적 개선으로 확대하지 않았다.

HyDE 정의는 질의를 바탕으로 가상 문서를 생성하고 그 임베딩을 검색에 활용하는 방법으로 명료화했다. 5.5의 CAD 주어·서술어 불일치는 동일 문맥의 근거 충실도·답변 관련성 평균 차이와 질의별 분포를 분석했다는 문장으로 교정했다. 그림 5-1 설명의 `분석함`은 `분석하였다`로 고쳤다. 그림 제목의 정식 제목·본문·목차 동일성을 유지하고 출처를 별도 문단으로 두었다. 실제 수정 19개는 [SUBMISSION_EDIT_LOG.json](SUBMISSION_EDIT_LOG.json)에 전후 문장과 이유를 기록했다. Lewis·Shi·Li 외의 인용번호 뒤 주제 조사 `은` 3곳은 모음으로 끝나는 `외`에 맞춰 `는`으로 교정했다. 그 밖의 문장은 근거 없는 표현 변경을 하지 않았다.

결과 보존: HyDE 답변 관련성 +0.0805, CAD 동일 문맥 유효 58쌍의 근거 충실도 +0.0288·95% CI [-0.0367, +0.0934], SCD 주 120쌍 +0.2182 및 전체 240쌍 +0.2289를 유지했다. CAD 신뢰구간에 0이 포함되므로 유의한 일반 개선으로 단정하지 않는다. SCD 출력 언어 지표와 RAG 품질을 구분했다. 재생성·재평가·모델/API 호출은 수행하지 않았다.

## 개인 정보와 학교 양식

이번 요청에 실제 개인정보가 제공되지 않아 학생명·학번·소속 학과·대학 및 캠퍼스·지도교수·제출일·인준일·심사위원·제출연도를 임의 입력하지 않았다. 양식 예시의 대학·학과·캠퍼스를 실제 소속으로 확정하지 않고 명시적 입력 자리로 바꿨다. 계정명과 다른 파일에 표시된 개인정보를 전용하지 않았다. [단일 입력 체크리스트](SUBMISSION_PERSONAL_FIELDS.md)의 1~2쪽 반복 위치를 모두 입력·확인해야 한다. 학교가 요구하는 서명·날인·위원 수도 사용자 확인 사항이다.

학교 양식 스타일 19개, A4·1단, 본문 10pt·160%, 여백 및 두 표지 배치표의 구조·치수·스타일을 독립 검증했다. 표지 문구의 placeholder가 길어지는 위치도 PDF 1~2쪽에서 확인했다. 실제 값을 입력하면 해당 페이지의 줄바꿈을 재확인해야 한다.

## HWPX와 실제 웹한글 PDF

원고와 1,092개 표 셀을 다시 넣어 HWPX를 생성하고 추출 텍스트·문단 순서·그림 바이트·수식·스타일을 독립 대조했다. 최종 로컬 HWPX와 같은 바이트의 업로드 복사본 `GRADUATION_REPORT_60Q_FINAL_AUDITED.hwpx`를 [실제 웹한글 문서](https://webhwp.hancomdocs.com/webhwp/?mode=HWP_EDITOR&docId=cXDPsWoYzSd7vTcYnQt2rRaJuHd3d7rO&lang=ko_KR)에서 열었다. 파일명은 기존 열린 문서의 잠금 충돌을 피한 별도 업로드 이름이다. 편집 메뉴와 편집 영역 활성, 최종 목차 표시와 PDF 내보내기를 확인했다. 문단·표 셀 편집·저장·재열기 증거는 이전 2026-10-08 시험본을 보존했고 이번에 모든 개별 편집 대화상자를 다시 시험했다고 주장하지 않는다.

새 PDF는 실제 웹한글 `파일 → PDF로 다운로드` 결과이며 54쪽이다. 기존 55쪽을 인위적으로 유지하지 않고 출처 수정·발췌 범위 변경 후 실제 페이지에 맞췄다. 모든 54쪽을 1.5배 PNG와 5개 접촉 시트로 렌더링하여 검토했고 표지, 문헌 그림·수식, 장 시작, 목차를 확대 검토했다. 이미지·캡션·출처가 겹치거나 잘린 부분, 절 제목만 쪽 끝에 남는 문제를 발견하지 않았다. 부록 A는 43~49쪽에 60개 질의를 보존하며 머리글과 분할 셀의 이어지는 내용을 확인했다. B.2 표는 52~54쪽에 이어진다. 대형 사례 그림의 세부 글자는 확대하여 읽는다.

| 위치 | 이전 55쪽 PDF | 최종 54쪽 PDF |
|---|---|---|
| 1. 서론 | 9 | 9 |
| 2. 이론적 배경 | 11 | 11 |
| 3. 시스템 설계 | 19 | 18 |
| 4. 프로그램 구현 | 22 | 21 |
| 5. 실험 | 25 | 24 |
| 6. 결론 | 40 | 39 |
| 참고문헌 | 42 | 41 |
| 부록 A. 60개 질의 목록 | 44 | 43 |
| 부록 B. 추가 사례 및 탐색 분석 | 51 | 50 |

목차는 5~6쪽, 그림목차는 7쪽, 표목차는 8쪽이며 모든 항목을 새 본문 위치와 대조했다. 일부 학교 글꼴의 PDF 텍스트 매핑 때문에 16개 제목은 이미지로 확인하고 부록 통합 목차 `43, 50`과 함께 `PAGE_MAP_60Q.json`에 기록했다. 미확정 쪽번호는 없으며 실패를 0쪽으로 치환하지 않았다. 목차 적용 전 PDF SHA와 최종 PDF SHA를 구분한다. 최종 재출력의 54쪽 모두 렌더링했고 목차 5~8쪽 외 50쪽은 적용 전 PDF와 픽셀이 동일했다. [픽셀 비교 기록](../DELIVERY/LOGS/submission_pdf_comparison.json)과 [웹한글 화면 증거](../DELIVERY/WEB_SUBMISSION_AUDIT.png)를 보존한다. PDF 텍스트 추출만으로 모든 글자의 동일성을 주장하지 않는다.

## 구조·원자료·실행 검증

17개 본문 표·1,092개 셀, 22개 그림·22개 본문 캡션, 네이티브 수식 10개, 참고문헌 22편, 부록 A 60개 질의, 8개 조건별 60개씩 총 480개 생성 기록을 검증했다. 표지 배치표 2개는 논문 표 17개와 별도다. HWPX 문단은 표지 9개와 본문 309개로 총 318개다. 원자료 manifest의 해시가 모두 일치하며 Git LF/Windows CRLF의 동일 텍스트는 LF 정규화 해시로 확인하고 임의 값을 받아들이지 않는다.

시작 커밋의 원자료·표·기존 그림·실험 결과 268개 파일 및 원고의 원문 블록 28개를 대조하여 보존을 확인했다. 새 문헌 PNG 4개를 추가하고 이전 PNG는 삭제·변조하지 않았다. backend/frontend/experiments의 변경은 없다. [보존 감사](SUBMISSION_DATA_PRESERVATION.json)를 참조한다.

다음 실제 실행은 모두 종료 0이다. 상세 명령·종료 코드와 로그는 [submission_results.json](../DELIVERY/LOGS/submission_results.json)에 있다. 로컬 Python 3.12.7, Ruff 0.13.0, Black 26.3.1을 사용했다.

| 검증 명령 | 결과 |
|---|---|
| `python -X utf8 FINALDOCS/VALIDATION/verify_finaldocs_60q.py` | PASS |
| `python -X utf8 FINALDOCS/BUILD/verify_thesis_hwpx.py` | PASS |
| `python -X utf8 -m unittest discover -s FINALDOCS/VALIDATION -p 'test_*.py'` | 9시험 PASS |
| `python -X utf8 -m unittest discover -s FINALDOCS/BUILD -p 'test_*.py'` | 6시험 PASS |
| 변경 Python의 compileall / Ruff / Black | PASS |
| 기존 backend의 CI 버전 Ruff / Black | PASS |
| `git diff --check` | PASS |

잘못된 문헌 버전·해시·출처·라이선스·로고 변경 고지·중복 기록과 기존 문단·셀·수식·그림·쪽나눔 변조가 실패하는 회귀 검증을 포함한다. 서비스 코드를 수정하지 않아 새 서비스 동작 시험은 추가하지 않았다. GitHub의 최종 커밋 CI와 Thesis HWPX validation에서 기존 서비스 검사 및 Linux 재생성·독립 재검사 결과를 아래 확정 기록에 남긴다.

## 최종 파일

| 경로 | SHA-256 | bytes |
|---|---|---|
| `FINALDOCS/DELIVERY/GRADUATION_REPORT_60Q_FINAL.hwpx` | `474e60b787b354c8a6be75106d371035e671201dd7d18da1912fbf86e7fb54d4` | 5,015,719 |
| `FINALDOCS/DELIVERY/GRADUATION_REPORT_60Q_FINAL.pdf` | `09d43099d3bcb7deb1ea5346b2a181b46579d0824ba7e246e6948167c2a75005` | 5,578,069 |

추가 파일의 해시는 [DELIVERY_FILES_SHA256.json](../DELIVERY/DELIVERY_FILES_SHA256.json), HWPX 독립 결과는 [HWPX_STRUCTURAL_QA.json](../DELIVERY/HWPX_STRUCTURAL_QA.json)에 있다. 이전 55쪽 HWPX/PDF/원고/페이지 지도를 로컬 `DELIVERY/versions/submission_audit_20261009/`에 보존했다. 생성기의 추가 버전 보존도 유지한다. 기존 사용자 미추적 DOCX·제작 스크립트·tmp 파일은 삭제하거나 Git에 포함하지 않는다.

## 사용자에게 남은 사항

문헌 출처 정리·문장 교정·양식·데이터 보존·HWPX 생성·실제 54쪽 PDF 검증은 완료했다. 개인 정보와 서명·인준은 실제 값이 제공되지 않아 미입력 상태다. 체크리스트 9개 항목 입력 후 저장·재열기·PDF 내보내기 및 1~2쪽을 확인한다. 편집으로 본문 쪽이 이동하면 목차도 재갱신한다. 현재 파일은 웹한글에서 열어 검토하고 제출 준비를 할 수 있는 본문 확정본이며 개인정보·학교 인준까지 완료된 행정 제출본으로 표시하지 않는다.

## GitHub Actions 확정 기록

검증한 논문 산출물 HEAD: `150353a7129dc6c62206ded4f085f8f2e5ae7b81`. 이후 보고서·CI 기록만 추가하는 확정 커밋의 최종 HEAD는 위 식별 명령 및 완료 응답에서 제공한다. HWPX·PDF·원고·표·그림은 이 검증 HEAD와 바이트가 같다.

| Workflow | 결과 | 실행 |
|---|---|---|
| Thesis HWPX validation | success | [#37810805882](https://github.com/LxNx-Hn/M_RAG/actions/runs/37810805882) |
| Publish Backend Image | success | [#37810805899](https://github.com/LxNx-Hn/M_RAG/actions/runs/37810805899) |
| CI | success | [#37810805852](https://github.com/LxNx-Hn/M_RAG/actions/runs/37810805852) |

Thesis HWPX validation은 저장된 패키지 검사, 9개 문헌·학술 회귀 시험, 6개 HWPX 훼손 시험, Linux 양식 재생성과 재검사·컴파일까지 통과했다. CI의 frontend 린트·타입 검사·빌드·이미지 빌드, backend Ruff·Black·pytest·이미지 빌드가 모두 성공했다. Publish Backend Image도 성공했다. 실행 HEAD와 결과 원문은 `../DELIVERY/LOGS/submission_ci_artifact.json`에 보존했다. 보고서 확정 커밋에서 새로 발생하는 동일 workflow도 완료 응답 전 확인한다.
