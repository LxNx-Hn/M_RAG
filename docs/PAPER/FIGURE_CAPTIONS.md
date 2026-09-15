# Evidence Figure Captions

These captions describe retained results only. The PNGs are deterministic
renderings of `cli/evidence_replay.py show <id> --figure`; no model, retrieval,
generation, or judge is executed during rendering.

## MAIN_BODY_RECOMMENDED

### Figure 1. Normal cross-lingual QA replay

- **file:** `figures/evidence/E01_normal_qa.png`
- **evidence id:** E01
- **query_id:** `track1_0027`
- **config:** `hyde_on__no_decoder_control`
- **1-sentence purpose:** A stored Korean question, English-paper evidence, and Korean answer are shown together.
- **draft caption:** M-RAG의 정상적인 한국어 질의–영어 논문 근거 기반 응답 예시.

### Figure 2. Language-drift replay

- **file:** `figures/evidence/E02_language_drift.png`
- **evidence id:** E02
- **query_id:** `track1_0009`
- **config:** `hyde_on__cad_only` (SCD off)
- **1-sentence purpose:** An unchanged stored response with a zero Korean-character ratio demonstrates observed language drift.
- **draft caption:** SCD 미적용 조건에서 한국어 질의에도 영어로 이탈한 저장 응답 사례.

### Figure 3. Matched-context SCD rescue

- **file:** `figures/evidence/E03_scd_rescue.png`
- **evidence id:** E03
- **query_id:** `track1_0035`
- **config:** `hyde_off__cad_only` versus `hyde_off__cad_scd`
- **1-sentence purpose:** The two configurations retain identical stored contexts, retrieved IDs, and reranked IDs while the Korean-character ratio changes by +0.7092.
- **draft caption:** 동일 retrieval 조건에서 SCD 적용에 따른 한국어 출력 유지 개선 사례.

### Figure 4. HyDE retrieval reformulation

- **file:** `figures/evidence/E04_hyde_retrieval_change.png`
- **evidence id:** E04
- **query_id:** `track1_0010`
- **config:** `hyde_off__no_decoder_control` versus `hyde_on__no_decoder_control`
- **1-sentence purpose:** The stored HyDE document and changed retrieval IDs make the retrieval-side intervention visible.
- **draft caption:** HyDE 적용 전후의 가상 문서와 검색 결과 ID 변화 예시.

### Figure 5. Low-faithfulness review candidate

- **file:** `figures/evidence/E06_low_faithfulness.png`
- **evidence id:** E06
- **query_id:** `track1_0009`
- **config:** `hyde_off__scd_only`
- **1-sentence purpose:** The question, stored context, answer, and faithfulness score are presented for qualitative review.
- **draft caption:** 낮은 faithfulness 점수를 보인 저장 응답의 질문·근거·응답 비교 사례.

## APPENDIX_RECOMMENDED

### Figure A1. CAD identical-context control

- **file:** `figures/evidence/E05_cad_identical_context.png`
- **evidence id:** E05
- **query_id:** `track1_0012`
- **config:** `hyde_off__no_decoder_control` versus `hyde_off__cad_only`
- **1-sentence purpose:** Context and retrieval identity separate the stored CAD comparison from retrieval changes.
- **draft caption:** 동일한 검색 근거에서 CAD 적용에 따른 생성 결과 비교 조건.

### Figure A2. Symmetric-normalization input audit

- **file:** `figures/evidence/E07_translation_confound.png`
- **evidence id:** E07
- **query_id:** not applicable (76-row panel)
- **config:** HyDE-off identical-context SCD pairs
- **1-sentence purpose:** The retained audit records normalization policy, panel counts, hashes, and interpretation limits.
- **draft caption:** 생성 후 언어 정규화 평가의 입력 검증과 해석상 제한.

### Figure A3. Cross-judge sensitivity result

- **file:** `figures/evidence/E08_symmetric_cross_judge.png`
- **evidence id:** E08
- **query_id:** not applicable (38 paired contrasts per language)
- **config:** HyDE-off matched-context symmetric panel
- **1-sentence purpose:** The stored gpt-4o and fixed gpt-4.1 results show that a nonzero quality effect is not cross-judge robust.
- **draft caption:** 대칭 평가에서 두 judge 결과를 비교한 교차 검증 요약.

## Rendering note

The figures use a white background, black Korean-capable text, stable margins,
and source-string truncation marked in the output. They are suitable for
grayscale printing. E03 is the clearest direct visual for the language-control
claim; E05, E07, and E08 are recommended as appendix/supporting figures because
they document controls and interpretation boundaries rather than standalone
headline effects.
