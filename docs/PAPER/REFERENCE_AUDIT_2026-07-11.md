# 참고문헌 정확성 감사 — 2026-07-11

## 판정

`THESIS.md`의 [1]–[20]은 모두 본문에서 사용되며, 제목·저자·출판처·연도와 기재된
권호·쪽·DOI를 1차 출처에 대조했다. 확인할 수 없는 쪽수나 DOI는 만들지 않았다.

이번 감사에서 실제로 고친 항목은 다음과 같다.

- [2]: 최신 arXiv v5 저자 목록으로 갱신
- [3]: 초기 arXiv 제목 대신 ACL 2024 정식판 제목·쪽·DOI 사용
- [5], [8]–[10], [12]–[14], [16]: 쪽수·DOI 또는 저자 표기 보강
- [15]: 약한 GitHub 기술보고서 표기를 2026년 정식 arXiv 판으로 교체
- [18]: 공식 HCLT-KACL 2024 행사명으로 정리
- [19], [20]: 실제 `gpt-4o` 사용과 다국어 LLM judge 한계를 뒷받침하도록 추가

## 전수 대조표

| 번호 | 판정 | 1차 출처 | 확인 내용 |
|---:|---|---|---|
| [1] | 정확 | [NeurIPS](https://proceedings.neurips.cc/paper/2020/hash/6b493230-Abstract.html) | 제목, 12명 저자, NeurIPS 2020 |
| [2] | 정확·최신판 | [arXiv v5](https://arxiv.org/abs/2312.10997) | 제목, 10명 저자, arXiv 번호 |
| [3] | 정확·정식판 | [ACL Anthology](https://aclanthology.org/2024.findings-acl.137/) | 정식 제목, 저자, pp. 2318–2335, DOI |
| [4] | 정확 | [NIST TREC-3](https://pages.nist.gov/trec-browser/trec3/adhoc/proceedings/) | 제목, 저자, TREC-3, 1994 |
| [5] | 정확 | [DOI](https://doi.org/10.1145/1571941.1572114) | 제목, 저자, SIGIR 2009, pp. 758–759, DOI |
| [6] | 정확 | [arXiv](https://arxiv.org/abs/1901.04085) | 제목, 저자, arXiv 번호, 2019 |
| [7] | 정확 | [arXiv](https://arxiv.org/abs/1611.09268) | 제목, 저자, arXiv 번호, 2016 |
| [8] | 정확 | [ACL Anthology](https://aclanthology.org/2023.acl-long.99/) | 제목, 저자, pp. 1762–1777, DOI |
| [9] | 정확 | [ACL Anthology](https://aclanthology.org/2024.naacl-short.69/) | 제목, 저자, pp. 783–791, DOI |
| [10] | 정확 | [ACL Anthology](https://aclanthology.org/2023.acl-long.687/) | 제목, 저자, pp. 12286–12312, DOI |
| [11] | 정확 | [AAAI](https://ojs.aaai.org/index.php/AAAI/article/view/40417) | 제목, 3명 저자, vol. 40 no. 37, pp. 31519–31526, DOI |
| [12] | 정확 | [ACL Anthology](https://aclanthology.org/2024.eacl-demo.16/) | `L. Espinosa Anke` 저자 표기, pp. 150–158, DOI |
| [13] | 정확 | [ACL Anthology](https://aclanthology.org/2024.tacl-1.9/) | 제목, 저자, vol. 12, pp. 157–173, DOI |
| [14] | 정확 | [ACL Anthology](https://aclanthology.org/2024.findings-emnlp.449/) | 제목, 저자, pp. 7640–7663, DOI |
| [15] | 정확·최신판 | [arXiv](https://arxiv.org/abs/2601.09066) | 정식 제목, Donghoon Shin et al., 2026 |
| [16] | 정확 | [KCI](https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearchBean.artiId=ART003200663) | 저자, vol. 18 no. 2, pp. 143–154, DOI |
| [17] | 정확 | [KCI](https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearchBean.artiId=ART003208016) | 저자, vol. 27 no. 2, pp. 127–148, DOI |
| [18] | 확인 가능한 범위 정확 | [HCLT-KACL 2024](https://sites.google.com/view/hclt2024) | 제목, 저자, 공식 행사명, 연도; 확인되지 않은 쪽·DOI는 미기재 |
| [19] | 정확 | [arXiv](https://arxiv.org/abs/2410.21276) | `GPT-4o System Card`, OpenAI, 2024 |
| [20] | 정확 | [ACL Anthology](https://aclanthology.org/2025.findings-emnlp.587/) | 제목, 2명 저자, pp. 11040–11053, DOI |

## 인용 범위 주의

- [5]는 기본 RRF의 근거다. dense 0.6 / BM25 0.4는 이 프로젝트가 적용한 가중치이지
  원 논문의 고정값이 아니다.
- [11]은 `reference_scd` 방법과 언어 이탈 배경의 근거다. 이 프로젝트의 RAGAS
  품질 효과를 대신 증명하지 않는다.
- [19]는 사용한 judge/번역 모델의 모델 문서다. 평가 타당성 보증 문헌은 아니다.
- [20]은 다국어 judge의 일반적 신뢰성 한계를 뒷받침하며, 이 프로젝트의 특정 점수
  오류율을 직접 추정하지 않는다.

## 2026-07-12 교차 judge 보충 판정

고정 모델 ID `gpt-4.1-2025-04-14`는 후속 민감도 평가의 실행 provenance이며,
새로운 이론·방법 근거로 사용하지 않는다. 모델 ID, judge provider, 입력 해시와 점수는
공식 score artifact에 직접 기록되어 있으므로 별도 학술문헌을 만들어 넣지 않았다.
본문의 평가 신뢰성 한계는 이미 [19]의 OpenAI 모델 문서와 [20]의 다국어 judge
신뢰성 연구가 뒷받침한다. 따라서 참고문헌은 [1]–[20]으로 연속·완결 상태다.
