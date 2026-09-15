# 한글 그림 일괄 삽입 안내

## 그림 폴더

모든 본문 그림과 부록 그림은 `INSERT_READY_FIGURES` 폴더에 PNG 형식으로 모았다. 파일명의 앞자리 `01`부터 `13`까지가 본문 삽입 순서이며, `03B`는 그림 2-1 바로 다음에 넣는 그림 2-2, `A1`과 `A2`는 부록 삽입 순서이다.

## 본문 삽입 순서

| 순서 | 논문 번호 | 삽입 위치 | 파일 | 역할 |
|---:|---|---|---|---|
| 01 | 그림 1-1 | 1.1 연구배경 및 목적 | `01_그림1-1_연구환경.png` | 한국어 질의-영어 문서-한국어 답변의 연구 환경 |
| 02 | 그림 1-2 | 그림 1-1 다음 | `02_그림1-2_언어이탈_사례.png` | 한국어 문자 비율 0.0000의 실제 언어 이탈 record |
| 03 | 그림 2-1 | 2.5 SCD 설명 다음 | `03_그림2-1_언어이탈_사례.png` | SCD 적용 조건에서 한국어 문자 비율 0.0000으로 저장된 언어 이탈 record |
| 03B | 그림 2-2 | 그림 2-1 다음 | `03B_그림2-2_언어이탈_Midm_사례.png` | Mi:dm 질의의 SCD 미적용 언어 이탈 record, 한국어 문자 비율 0.0000 |
| 04 | 그림 3-1 | 3.1 여덟 실험 조건 다음 | `04_그림3-1_RAG-Cube.png` | HyDE-CAD-SCD의 2x2x2 구성 |
| 05 | 그림 4-1 | 4.2 시스템 구성 첫 문단 다음 | `05_그림4-1_시스템구성.png` | 검색-문맥 구성-생성-평가 시스템 흐름 |
| 06 | 그림 5-1 | 5.1 대응쌍 설명 다음 | `06_그림5-1_평가설계.png` | 요인별 비교 단위와 평가 지표 |
| 07 | 그림 5-2 | 5.3 요구사항별 실행 결과 | `07_그림5-2_정상응답_사례.png` | 정상 한국어 답변과 영어 근거의 연결 |
| 08 | 그림 5-3 | 그림 5-2 다음 | `08_그림5-3_HyDE_검색변화.png` | HyDE 적용 전후 검색 ID와 답변 변화 |
| 09 | 그림 5-4 | 그림 5-3 다음 | `09_그림5-4_CAD_동일문맥.png` | 동일 문맥의 CAD OFF-ON 비교 |
| 10 | 그림 5-5 | 그림 5-4 다음 | `10_그림5-5_SCD_언어개선.png` | 동일 문맥의 한국어 문자 비율 0.0007-0.7099 변화 |
| 11 | 그림 5-6 | 5.4 HyDE와 CAD 결과 | `11_그림5-6_HyDE_CAD_품질.png` | 품질 지표 평균 차이와 95% 신뢰구간 |
| 12 | 그림 5-7 | 5.5 SCD 출력 언어 결과 | `12_그림5-7_SCD_언어통계.png` | 76개 대응쌍의 문자 비율과 언어 이탈 수 |
| 13 | 그림 5-8 | 5.6 SCD 대칭 품질 평가 | `13_그림5-8_SCD_대칭품질.png` | 평가 언어와 평가 모델별 품질 차이 |

## 부록 삽입 순서

| 순서 | 논문 번호 | 파일 | 역할 |
|---:|---|---|---|
| A1 | 그림 A-1 | `A1_부록_대칭평가_입력검증.png` | 38개 동일 문맥 대응쌍과 정규화 panel 입력 검증 |
| A2 | 그림 A-2 | `A2_부록_평가모델_교차검증.png` | gpt-4o와 gpt-4.1 평가 결과 교차 검증 |

## 응답 화면 재현 확인

2026년 9월 15일에 `cli/evidence_replay.py show <E01-E09> --figure`를 실행하여 아홉 증빙 화면이 저장된 최종 artifact에서 재현되는 것을 확인하였다.

| Evidence ID | 핵심 확인값 |
|---|---|
| E01 | query `track1_0027`, 한국어 문자 비율 0.6637, faithfulness 1.0000 |
| E02 | query `track1_0009`, 한국어 문자 비율 0.0000 |
| E03 | 동일 context-retrieved-reranked ID, 한국어 문자 비율 0.0007에서 0.7099, 차이 +0.7092 |
| E04 | query `track1_0010`, HyDE 적용에 따라 context-retrieved-reranked ID 변화 |
| E05 | query `track1_0012`, 동일 context-retrieved-reranked ID의 CAD 대응 비교 |
| E06 | query `track1_0009`, SCD 적용 조건의 한국어 문자 비율 0.0000 |
| E07 | 대칭 평가 입력 구성과 번역 적용 수 검증 |
| E08 | 두 평가 모델의 대칭 평가 결과 비교 |
| E09 | query `track1_0035`, Mi:dm 질의의 한국어 문자 비율 0.0000 |

재현 명령은 다음과 같다.

```powershell
python -X utf8 cli/evidence_replay.py list
python -X utf8 cli/evidence_replay.py show E01 --figure
python -X utf8 cli/evidence_replay.py show E02 --figure
python -X utf8 cli/evidence_replay.py show E03 --figure
python -X utf8 cli/evidence_replay.py show E04 --figure
python -X utf8 cli/evidence_replay.py show E05 --figure
python -X utf8 cli/evidence_replay.py show E06 --figure
python -X utf8 cli/evidence_replay.py show E07 --figure
python -X utf8 cli/evidence_replay.py show E08 --figure
python -X utf8 cli/evidence_replay.py show E09 --figure
```

## 한글 삽입 방법

1. 원고의 `[그림 삽입: ...]` 표시를 찾는다.
2. 표시된 파일을 `INSERT_READY_FIGURES` 폴더에서 선택한다.
3. 한글의 그림 넣기 기능으로 원본 비율을 유지하여 삽입한다.
4. 본문 폭에 맞춰 너비를 조정하고 가운데 정렬한다.
5. 바로 아래의 캡션에 `그림제목` 스타일을 적용한다.
6. 조판을 마친 뒤 그림 목차의 페이지 번호를 갱신한다.
