# 포스터 통계 상세표

기준: 최종 60개 질의 × 8조건의 저장된 생성 480건. 통계량은 FACTORIAL_STATISTICS_60Q.json에서 계산하였다. 반복측정 단위는 질의이며, SCD 120·240쌍도 질의별 평균 차이 60개로 검정한다.

품질 지표는 S0 영어 평가 문맥과 S1 한국어 번역 평가 문맥을 나눠 H×CAD를 분석했다. 24개 품질 요인 검정 전체에 Holm 보정을 적용했다. 한국어 문자 비율과 실행 시간은 각각 7개 요인 검정을 보정했다. HyDE·CAD의 단순 비교는 각각 4지표, SCD 비교는 2개를 보정했다. 추가 분석은 기존 결과를 확인한 뒤 수행한 탐색적 재분석이다.

## 표 5-1 평가 문맥 언어별 8조건의 품질 및 한국어 문자 비율 평균(SD)

| 조건 | 충실도 | 관련성 | 정밀도 | 재현율 | 한국어 비율 |
|---|---|---|---|---|---|
| H0C0S0 | 0.791 (0.260) | 0.683 (0.282) | 0.749 (0.302) | 0.933 (0.252) | 0.494 (0.265) |
| H0C0S1 | 0.787 (0.254) | 0.637 (0.296) | 0.763 (0.300) | 0.900 (0.303) | 0.699 (0.329) |
| H0C1S0 | 0.839 (0.201) | 0.675 (0.261) | 0.740 (0.302) | 0.917 (0.279) | 0.488 (0.245) |
| H0C1S1 | 0.777 (0.270) | 0.600 (0.321) | 0.752 (0.301) | 0.850 (0.360) | 0.719 (0.218) |
| H1C0S0 | 0.834 (0.186) | 0.763 (0.209) | 0.714 (0.296) | 0.933 (0.252) | 0.556 (0.213) |
| H1C0S1 | 0.822 (0.218) | 0.710 (0.272) | 0.743 (0.281) | 0.900 (0.303) | 0.807 (0.200) |
| H1C1S0 | 0.860 (0.181) | 0.705 (0.248) | 0.736 (0.271) | 0.900 (0.303) | 0.503 (0.229) |
| H1C1S1 | 0.831 (0.253) | 0.667 (0.286) | 0.754 (0.267) | 0.917 (0.279) | 0.731 (0.209) |

## 표 5-2 8조건의 질의별 조건 실행 시간 평균과 표준편차

| 조건 | 평균(초) | SD(초) |
|---|---|---|
| H0C0S0 | 20.792 | 23.404 |
| H0C0S1 | 18.898 | 5.085 |
| H0C1S0 | 63.867 | 25.312 |
| H0C1S1 | 55.159 | 26.465 |
| H1C0S0 | 23.440 | 4.707 |
| H1C0S1 | 24.892 | 5.196 |
| H1C1S0 | 73.532 | 21.584 |
| H1C1S1 | 64.125 | 21.675 |

## 표 5-3 SCD OFF 영어 평가 문맥의 품질 지표 H×C 반복측정 ANOVA

| 지표 | 효과 | df | F | p | 보정 p | 부분 η² |
|---|---|---|---|---|---|---|
| 근거 충실도 | H | 1, 57 | 1.162 | 0.286 | 1.000 | 0.020 |
| 근거 충실도 | C | 1, 57 | 1.034 | 0.313 | 1.000 | 0.018 |
| 근거 충실도 | H×C | 1, 57 | 0.073 | 0.789 | 1.000 | 0.001 |
| 답변 관련성 | H | 1, 59 | 2.844 | 0.097 | 1.000 | 0.046 |
| 답변 관련성 | C | 1, 59 | 1.498 | 0.226 | 1.000 | 0.025 |
| 답변 관련성 | H×C | 1, 59 | 1.185 | 0.281 | 1.000 | 0.020 |
| 문맥 정밀도 | H | 1, 59 | 0.496 | 0.484 | 1.000 | 0.008 |
| 문맥 정밀도 | C | 1, 59 | 0.226 | 0.636 | 1.000 | 0.004 |
| 문맥 정밀도 | H×C | 1, 59 | 1.567 | 0.216 | 1.000 | 0.026 |
| 문맥 재현율 | H | 1, 59 | 0.039 | 0.843 | 1.000 | 0.001 |
| 문맥 재현율 | C | 1, 59 | 1.000 | 0.321 | 1.000 | 0.017 |
| 문맥 재현율 | H×C | 1, 59 | 0.109 | 0.742 | 1.000 | 0.002 |

## 표 5-4 SCD ON 한국어 번역 평가 문맥의 품질 지표 H×C 반복측정 ANOVA

| 지표 | 효과 | df | F | p | 보정 p | 부분 η² |
|---|---|---|---|---|---|---|
| 근거 충실도 | H | 1, 56 | 2.434 | 0.124 | 1.000 | 0.042 |
| 근거 충실도 | C | 1, 56 | 0.137 | 0.713 | 1.000 | 0.002 |
| 근거 충실도 | H×C | 1, 56 | 0.188 | 0.666 | 1.000 | 0.003 |
| 답변 관련성 | H | 1, 59 | 3.012 | 0.088 | 1.000 | 0.049 |
| 답변 관련성 | C | 1, 59 | 2.628 | 0.110 | 1.000 | 0.043 |
| 답변 관련성 | H×C | 1, 59 | 0.011 | 0.917 | 1.000 | 0.000 |
| 문맥 정밀도 | H | 1, 59 | 0.158 | 0.693 | 1.000 | 0.003 |
| 문맥 정밀도 | C | 1, 59 | 0.000 | 0.994 | 1.000 | 0.000 |
| 문맥 정밀도 | H×C | 1, 59 | 0.823 | 0.368 | 1.000 | 0.014 |
| 문맥 재현율 | H | 1, 59 | 0.529 | 0.470 | 1.000 | 0.009 |
| 문맥 재현율 | C | 1, 59 | 0.396 | 0.532 | 1.000 | 0.007 |
| 문맥 재현율 | H×C | 1, 59 | 2.744 | 0.103 | 1.000 | 0.044 |

## 표 5-5 한국어 문자 비율의 H×C×S 반복측정 ANOVA

| 효과 | df | F | p | 보정 p | 부분 η² |
|---|---|---|---|---|---|
| H | 1, 59 | 2.924 | 0.093 | 0.370 | 0.047 |
| C | 1, 59 | 3.365 | 0.072 | 0.358 | 0.054 |
| S | 1, 59 | 341.302 | <0.001 | <0.001 | 0.853 |
| H×C | 1, 59 | 4.417 | 0.040 | 0.239 | 0.070 |
| H×S | 1, 59 | 0.771 | 0.384 | 0.940 | 0.013 |
| C×S | 1, 59 | 0.006 | 0.939 | 0.940 | 0.000 |
| H×C×S | 1, 59 | 1.035 | 0.313 | 0.940 | 0.017 |

## 표 5-6 조건 실행 시간의 H×C×S 반복측정 ANOVA

| 효과 | df | F | p | 보정 p | 부분 η² |
|---|---|---|---|---|---|
| H | 1, 59 | 16.362 | <0.001 | <0.001 | 0.217 |
| C | 1, 59 | 423.765 | <0.001 | <0.001 | 0.878 |
| S | 1, 59 | 6.097 | 0.016 | 0.066 | 0.094 |
| H×C | 1, 59 | 2.262 | 0.138 | 0.414 | 0.037 |
| H×S | 1, 59 | 0.401 | 0.529 | 0.976 | 0.007 |
| C×S | 1, 59 | 12.080 | <0.001 | 0.005 | 0.170 |
| H×C×S | 1, 59 | 0.487 | 0.488 | 0.976 | 0.008 |

## 표 5-7 HyDE·CAD 단순 비교의 품질 대응 점수 차이와 검정 결과

| 요인·지표 | n | 평균 차이(SD) | t(df) | p | 보정 p | dz |
|---|---|---|---|---|---|---|
| HyDE 근거 충실도 | 60 | 0.044 (0.281) | 1.200 (59) | 0.235 | 0.705 | 0.155 |
| HyDE 답변 관련성 | 60 | 0.080 (0.279) | 2.236 (59) | 0.029 | 0.117 | 0.289 |
| HyDE 문맥 정밀도 | 60 | -0.034 (0.234) | -1.134 (59) | 0.261 | 0.705 | -0.146 |
| HyDE 문맥 재현율 | 60 | 0.000 (0.368) | 0.000 (59) | 1.000 | 1.000 | 0.000 |
| CAD 근거 충실도 | 58 | 0.029 (0.255) | 0.862 (57) | 0.393 | 1.000 | 0.113 |
| CAD 답변 관련성 | 60 | -0.007 (0.313) | -0.181 (59) | 0.857 | 1.000 | -0.023 |
| CAD 문맥 정밀도 | 60 | -0.009 (0.077) | -0.930 (59) | 0.356 | 1.000 | -0.120 |
| CAD 문맥 재현율 | 60 | -0.017 (0.129) | -1.000 (59) | 0.321 | 1.000 | -0.129 |

## 표 5-8 SCD 한국어 문자 비율의 질의별 평균 대응 차이(%p)와 검정 결과

| 요인·지표 | n | 평균 차이(SD) | t(df) | p | 보정 p | dz |
|---|---|---|---|---|---|---|
| HyDE OFF 동일 문맥 | 60 | 21.822 (12.117) | 13.951 (59) | <0.001 | <0.001 | 1.801 |
| 전체 H·C 상태 일치 | 60 | 22.894 (9.599) | 18.474 (59) | <0.001 | <0.001 | 2.385 |

## 실행 시간 상호작용 후속 비교

| 비교 | n | 평균 차이(초) | SD | t | df | 보정 p |
|---|---:|---:|---:|---:|---:|---:|
| CAD_simple_effect_S0_averaged_over_H | 60 | 46.583 | 18.937 | 19.054 | 59 | 1.3773816e-26 |
| CAD_simple_effect_S1_averaged_over_H | 60 | 37.747 | 18.405 | 15.886 | 59 | 5.5824971e-23 |

## 결측과 민감도 분석

근거 충실도 5개 셀이 결측이다. 해당 조건과 지표의 완전 대응 질의만 사용했으며 대체값을 넣지 않았다. 숫자만 생성한 답변 1건의 기존 한국어 비율 0 기록을 유지하고, 해당 질의를 제외한 민감도 분석을 함께 제공한다.

HyDE 답변 관련성은 대응 t 검정의 보정 p=0.117, 평균 차이에 대한 부호 순열검정의 보정 p=0.112, Wilcoxon 부호순위 검정의 보정 p=0.012다. 검정 대상과 가정이 다르므로 결과를 구분한다. 네 문서에서 작성한 질의에 대한 결과이며 문서 모집단 일반화는 후속 평가 대상이다.

### 전체 민감도·결측 기록

```json
{
  "missing_cells": [
    {
      "query_id": "ext_rag_003",
      "condition": "H0C1S0",
      "metric": "faithfulness"
    },
    {
      "query_id": "ext_rag_006",
      "condition": "H0C1S0",
      "metric": "faithfulness"
    },
    {
      "query_id": "ext_rag_003",
      "condition": "H0C0S1",
      "metric": "faithfulness"
    },
    {
      "query_id": "ext_rag_005",
      "condition": "H0C0S1",
      "metric": "faithfulness"
    },
    {
      "query_id": "ext_rag_006",
      "condition": "H0C0S1",
      "metric": "faithfulness"
    }
  ],
  "zero_denominator_answers": [
    {
      "query_id": "track1_0035",
      "condition": "H1C0S1",
      "existing_rule": "existing korean_ratio returns 0; not a new imputation"
    }
  ],
  "paired": [
    {
      "factor": "HyDE",
      "metric": "faithfulness",
      "on": "H1C0S0",
      "off": "H0C0S0",
      "n": 60,
      "mean": 0.04357166666666667,
      "sd": 0.28134436230456966,
      "df": 59,
      "zero_differences": 14,
      "difference_quantiles": [
        -0.6429,
        -0.10439999999999999,
        0.0,
        0.16047500000000003,
        0.7778
      ],
      "status": "estimated",
      "t": 1.1996141524514914,
      "p": 0.23508452099201838,
      "dz": 0.1548695211439784,
      "wilcoxon_p": 0.32543176632303417,
      "sign_flip_p": 0.23706762932370676,
      "sign_flip_draws": 100000,
      "shapiro_difference_p": 0.04286175044297694,
      "p_holm": 0.7052535629760551,
      "wilcoxon_p_holm": 0.6508635326460683,
      "sign_flip_p_holm": 0.7112028879711203
    },
    {
      "factor": "HyDE",
      "metric": "answer_relevancy",
      "on": "H1C0S0",
      "off": "H0C0S0",
      "n": 60,
      "mean": 0.08049500000000001,
      "sd": 0.2788115951100251,
      "df": 59,
      "zero_differences": 5,
      "difference_quantiles": [
        -0.8714,
        -0.007050000000000001,
        0.009350000000000025,
        0.12107499999999999,
        0.8947
      ],
      "status": "estimated",
      "t": 2.236318717877859,
      "p": 0.029125256359383164,
      "dz": 0.288707505038429,
      "wilcoxon_p": 0.0030168177116113213,
      "sign_flip_p": 0.028089719102808972,
      "sign_flip_draws": 100000,
      "shapiro_difference_p": 2.0131022414452884e-08,
      "p_holm": 0.11650102543753266,
      "wilcoxon_p_holm": 0.012067270846445285,
      "sign_flip_p_holm": 0.11235887641123589
    },
    {
      "factor": "HyDE",
      "metric": "context_precision",
      "on": "H1C0S0",
      "off": "H0C0S0",
      "n": 60,
      "mean": -0.03430833333333334,
      "sd": 0.23438555610879563,
      "df": 59,
      "zero_differences": 20,
      "difference_quantiles": [
        -0.675,
        -0.17362499999999997,
        0.0,
        0.0791,
        0.6667000000000001
      ],
      "status": "estimated",
      "t": -1.1338207510914662,
      "p": 0.26145580340953745,
      "dz": -0.14637562955205446,
      "wilcoxon_p": 0.21116093059998187,
      "sign_flip_p": 0.26350736492635074,
      "sign_flip_draws": 100000,
      "shapiro_difference_p": 0.025899718130150056,
      "p_holm": 0.7052535629760551,
      "wilcoxon_p_holm": 0.6334827917999456,
      "sign_flip_p_holm": 0.7112028879711203
    },
    {
      "factor": "HyDE",
      "metric": "context_recall",
      "on": "H1C0S0",
      "off": "H0C0S0",
      "n": 60,
      "mean": 0.0,
      "sd": 0.3682298471593293,
      "df": 59,
      "zero_differences": 52,
      "difference_quantiles": [
        -1.0,
        0.0,
        0.0,
        0.0,
        1.0
      ],
      "status": "estimated",
      "t": 0.0,
      "p": 1.0,
      "dz": 0.0,
      "wilcoxon_p": 1.0,
      "sign_flip_p": 1.0,
      "sign_flip_draws": 100000,
      "shapiro_difference_p": 6.457890134920486e-13,
      "p_holm": 1.0,
      "wilcoxon_p_holm": 1.0,
      "sign_flip_p_holm": 1.0
    },
    {
      "factor": "CAD",
      "metric": "faithfulness",
      "on": "H0C1S0",
      "off": "H0C0S0",
      "n": 58,
      "mean": 0.028837931034482754,
      "sd": 0.2548931257479084,
      "df": 57,
      "zero_differences": 12,
      "difference_quantiles": [
        -1.0,
        -0.07140000000000002,
        0.0,
        0.12079999999999999,
        0.7693
      ],
      "status": "estimated",
      "t": 0.8616283352356126,
      "p": 0.39250241627708504,
      "dz": 0.11313734315064945,
      "wilcoxon_p": 0.5773778081556041,
      "sign_flip_p": 0.3980460195398046,
      "sign_flip_draws": 100000,
      "shapiro_difference_p": 5.633565500048125e-06,
      "p_holm": 1.0,
      "wilcoxon_p_holm": 0.9676797027871364,
      "sign_flip_p_holm": 1.0
    },
    {
      "factor": "CAD",
      "metric": "answer_relevancy",
      "on": "H0C1S0",
      "off": "H0C0S0",
      "n": 60,
      "mean": -0.00733500000000001,
      "sd": 0.31315874234448515,
      "df": 59,
      "zero_differences": 2,
      "difference_quantiles": [
        -0.9001,
        -0.07620000000000002,
        -0.012999999999999956,
        0.03692499999999996,
        0.8905
      ],
      "status": "estimated",
      "t": -0.1814308783574135,
      "p": 0.856651247086036,
      "dz": -0.023422625678868204,
      "wilcoxon_p": 0.22268489540586955,
      "sign_flip_p": 0.8572714272857271,
      "sign_flip_draws": 100000,
      "shapiro_difference_p": 4.92584005049047e-08,
      "p_holm": 1.0,
      "wilcoxon_p_holm": 0.8907395816234782,
      "sign_flip_p_holm": 1.0
    },
    {
      "factor": "CAD",
      "metric": "context_precision",
      "on": "H0C1S0",
      "off": "H0C0S0",
      "n": 60,
      "mean": -0.009234999999999997,
      "sd": 0.0768867113443925,
      "df": 59,
      "zero_differences": 52,
      "difference_quantiles": [
        -0.41669999999999996,
        0.0,
        0.0,
        0.0,
        0.16670000000000007
      ],
      "status": "estimated",
      "t": -0.930381871634936,
      "p": 0.35596469958189725,
      "dz": -0.12011178314851313,
      "wilcoxon_p": 0.4838398513935682,
      "sign_flip_p": 0.4015559844401556,
      "sign_flip_draws": 100000,
      "shapiro_difference_p": 4.0946414664186924e-14,
      "p_holm": 1.0,
      "wilcoxon_p_holm": 0.9676797027871364,
      "sign_flip_p_holm": 1.0
    },
    {
      "factor": "CAD",
      "metric": "context_recall",
      "on": "H0C1S0",
      "off": "H0C0S0",
      "n": 60,
      "mean": -0.016666666666666666,
      "sd": 0.12909944487358058,
      "df": 59,
      "zero_differences": 59,
      "difference_quantiles": [
        -1.0,
        0.0,
        0.0,
        0.0,
        0.0
      ],
      "status": "estimated",
      "t": -1.0,
      "p": 0.3213942797694451,
      "dz": -0.12909944487358055,
      "wilcoxon_p": 0.31731050786291415,
      "sign_flip_p": 1.0,
      "sign_flip_draws": 100000,
      "shapiro_difference_p": 3.0999278785527514e-17,
      "p_holm": 1.0,
      "wilcoxon_p_holm": 0.9519315235887424,
      "sign_flip_p_holm": 1.0
    },
    {
      "factor": "SCD_H0_same_context",
      "metric": "korean_ratio",
      "raw_pairs": 120,
      "n": 60,
      "mean": 0.2182239417373891,
      "sd": 0.12116563540481372,
      "df": 59,
      "zero_differences": 0,
      "difference_quantiles": [
        -0.08708016121809227,
        0.12281496516576686,
        0.205853799218781,
        0.29204340269531825,
        0.5037953084797353
      ],
      "status": "estimated",
      "t": 13.95078215483972,
      "p": 2.4352330212143443e-20,
      "dz": 1.8010382317420621,
      "wilcoxon_p": 2.2059707532770726e-11,
      "sign_flip_p": 9.99990000099999e-06,
      "sign_flip_draws": 100000,
      "shapiro_difference_p": 0.17198902268753785,
      "p_holm": 2.4352330212143443e-20,
      "wilcoxon_p_holm": 3.428298796343233e-11,
      "sign_flip_p_holm": 1.999980000199998e-05
    },
    {
      "factor": "SCD_all_states",
      "metric": "korean_ratio",
      "raw_pairs": 240,
      "n": 60,
      "mean": 0.22894148599301442,
      "sd": 0.09599102576064793,
      "df": 59,
      "zero_differences": 0,
      "difference_quantiles": [
        -0.03556918167351556,
        0.17183976984327995,
        0.20525989302521577,
        0.28128095224321226,
        0.47373570377763174
      ],
      "status": "estimated",
      "t": 18.474363733081926,
      "p": 3.294334053374131e-26,
      "dz": 2.385030102333486,
      "wilcoxon_p": 1.7141493981716166e-11,
      "sign_flip_p": 9.99990000099999e-06,
      "sign_flip_draws": 100000,
      "shapiro_difference_p": 0.11774935092303651,
      "p_holm": 6.588668106748262e-26,
      "wilcoxon_p_holm": 3.428298796343233e-11,
      "sign_flip_p_holm": 1.999980000199998e-05
    }
  ],
  "runtime_followups": [
    {
      "metric": "duration_seconds",
      "comparison": "CAD_simple_effect_S0_averaged_over_H",
      "n": 60,
      "mean": 46.58316666666667,
      "sd": 18.937362389423757,
      "df": 59,
      "zero_differences": 0,
      "difference_quantiles": [
        -5.238499999999995,
        31.858375000000002,
        48.69975,
        61.555375,
        80.204
      ],
      "status": "estimated",
      "t": 19.053955350652643,
      "p": 6.886907824595335e-27,
      "dz": 2.4598550584152465,
      "wilcoxon_p": 1.8030386309636688e-11,
      "sign_flip_p": 9.99990000099999e-06,
      "sign_flip_draws": 100000,
      "shapiro_difference_p": 0.061754884860160515,
      "p_holm": 1.377381564919067e-26,
      "wilcoxon_p_holm": 3.6060772619273376e-11,
      "sign_flip_p_holm": 1.999980000199998e-05
    },
    {
      "metric": "duration_seconds",
      "comparison": "CAD_simple_effect_S1_averaged_over_H",
      "n": 60,
      "mean": 37.74690833333333,
      "sd": 18.40484670795032,
      "df": 59,
      "zero_differences": 0,
      "difference_quantiles": [
        -14.889500000000002,
        27.98975,
        38.29425,
        50.315875,
        68.5235
      ],
      "status": "estimated",
      "t": 15.88637489522443,
      "p": 5.582497085957244e-23,
      "dz": 2.0509221800270603,
      "wilcoxon_p": 2.980572902364543e-11,
      "sign_flip_p": 9.99990000099999e-06,
      "sign_flip_draws": 100000,
      "shapiro_difference_p": 0.014867989153701725,
      "p_holm": 5.582497085957244e-23,
      "wilcoxon_p_holm": 3.6060772619273376e-11,
      "sign_flip_p_holm": 1.999980000199998e-05
    }
  ],
  "leave_one_document_out": [
    {
      "omitted_paper": "paper_midm",
      "factor": "HyDE",
      "metric": "faithfulness",
      "n": 45,
      "mean": 0.05786222222222222,
      "sd": 0.3046899200893269
    },
    {
      "omitted_paper": "paper_midm",
      "factor": "HyDE",
      "metric": "answer_relevancy",
      "n": 45,
      "mean": 0.07418444444444446,
      "sd": 0.29165732769464203
    },
    {
      "omitted_paper": "paper_midm",
      "factor": "HyDE",
      "metric": "context_precision",
      "n": 45,
      "mean": -0.04092666666666667,
      "sd": 0.23477499808811142
    },
    {
      "omitted_paper": "paper_midm",
      "factor": "HyDE",
      "metric": "context_recall",
      "n": 45,
      "mean": -0.044444444444444446,
      "sd": 0.3665288997383894
    },
    {
      "omitted_paper": "paper_midm",
      "factor": "CAD",
      "metric": "faithfulness",
      "n": 43,
      "mean": 0.036081395348837204,
      "sd": 0.279612118457843
    },
    {
      "omitted_paper": "paper_midm",
      "factor": "CAD",
      "metric": "answer_relevancy",
      "n": 45,
      "mean": -0.021086666666666674,
      "sd": 0.2983386754558102
    },
    {
      "omitted_paper": "paper_midm",
      "factor": "CAD",
      "metric": "context_precision",
      "n": 45,
      "mean": -0.012313333333333329,
      "sd": 0.08881501613414867
    },
    {
      "omitted_paper": "paper_midm",
      "factor": "CAD",
      "metric": "context_recall",
      "n": 45,
      "mean": -0.022222222222222223,
      "sd": 0.14907119849998599
    },
    {
      "omitted_paper": "paper_midm",
      "factor": "SCD_H0_same_context",
      "metric": "korean_ratio",
      "n": 45,
      "mean": 0.21221252105278268,
      "sd": 0.12198859269684881
    },
    {
      "omitted_paper": "paper_midm",
      "factor": "SCD_all_states",
      "metric": "korean_ratio",
      "n": 45,
      "mean": 0.21261720868208242,
      "sd": 0.09088194030815959
    },
    {
      "omitted_paper": "paper_nlp_cad",
      "factor": "HyDE",
      "metric": "faithfulness",
      "n": 45,
      "mean": 0.07444666666666665,
      "sd": 0.284033790083312
    },
    {
      "omitted_paper": "paper_nlp_cad",
      "factor": "HyDE",
      "metric": "answer_relevancy",
      "n": 45,
      "mean": 0.10796,
      "sd": 0.2736243911908174
    },
    {
      "omitted_paper": "paper_nlp_cad",
      "factor": "HyDE",
      "metric": "context_precision",
      "n": 45,
      "mean": -0.01830222222222222,
      "sd": 0.24382873878726002
    },
    {
      "omitted_paper": "paper_nlp_cad",
      "factor": "HyDE",
      "metric": "context_recall",
      "n": 45,
      "mean": 0.022222222222222223,
      "sd": 0.3982284000242305
    },
    {
      "omitted_paper": "paper_nlp_cad",
      "factor": "CAD",
      "metric": "faithfulness",
      "n": 43,
      "mean": 0.01574186046511628,
      "sd": 0.2650456809078104
    },
    {
      "omitted_paper": "paper_nlp_cad",
      "factor": "CAD",
      "metric": "answer_relevancy",
      "n": 45,
      "mean": -0.006484444444444441,
      "sd": 0.35554644048764483
    },
    {
      "omitted_paper": "paper_nlp_cad",
      "factor": "CAD",
      "metric": "context_precision",
      "n": 45,
      "mean": 0.006082222222222226,
      "sd": 0.039175945129220284
    },
    {
      "omitted_paper": "paper_nlp_cad",
      "factor": "CAD",
      "metric": "context_recall",
      "n": 45,
      "mean": 0.0,
      "sd": 0.0
    },
    {
      "omitted_paper": "paper_nlp_cad",
      "factor": "SCD_H0_same_context",
      "metric": "korean_ratio",
      "n": 45,
      "mean": 0.21235736624428503,
      "sd": 0.12901803177295815
    },
    {
      "omitted_paper": "paper_nlp_cad",
      "factor": "SCD_all_states",
      "metric": "korean_ratio",
      "n": 45,
      "mean": 0.2361555118313934,
      "sd": 0.09680229458770757
    },
    {
      "omitted_paper": "paper_nlp_rag",
      "factor": "HyDE",
      "metric": "faithfulness",
      "n": 45,
      "mean": 0.00560666666666666,
      "sd": 0.24232319459012508
    },
    {
      "omitted_paper": "paper_nlp_rag",
      "factor": "HyDE",
      "metric": "answer_relevancy",
      "n": 45,
      "mean": 0.06351333333333337,
      "sd": 0.3120227676716148
    },
    {
      "omitted_paper": "paper_nlp_rag",
      "factor": "HyDE",
      "metric": "context_precision",
      "n": 45,
      "mean": -0.046948888888888894,
      "sd": 0.22774736264536452
    },
    {
      "omitted_paper": "paper_nlp_rag",
      "factor": "HyDE",
      "metric": "context_recall",
      "n": 45,
      "mean": -0.022222222222222223,
      "sd": 0.39822840002423043
    },
    {
      "omitted_paper": "paper_nlp_rag",
      "factor": "CAD",
      "metric": "faithfulness",
      "n": 45,
      "mean": 0.049182222222222224,
      "sd": 0.2065171369610422
    },
    {
      "omitted_paper": "paper_nlp_rag",
      "factor": "CAD",
      "metric": "answer_relevancy",
      "n": 45,
      "mean": 0.023671111111111108,
      "sd": 0.3075719247902707
    },
    {
      "omitted_paper": "paper_nlp_rag",
      "factor": "CAD",
      "metric": "context_precision",
      "n": 45,
      "mean": -0.014784444444444442,
      "sd": 0.08118802239122457
    },
    {
      "omitted_paper": "paper_nlp_rag",
      "factor": "CAD",
      "metric": "context_recall",
      "n": 45,
      "mean": -0.022222222222222223,
      "sd": 0.14907119849998599
    },
    {
      "omitted_paper": "paper_nlp_rag",
      "factor": "SCD_H0_same_context",
      "metric": "korean_ratio",
      "n": 45,
      "mean": 0.22832555920212738,
      "sd": 0.10818862441685405
    },
    {
      "omitted_paper": "paper_nlp_rag",
      "factor": "SCD_all_states",
      "metric": "korean_ratio",
      "n": 45,
      "mean": 0.23694463463947824,
      "sd": 0.09643119029610034
    },
    {
      "omitted_paper": "paper_nlp_raptor",
      "factor": "HyDE",
      "metric": "faithfulness",
      "n": 45,
      "mean": 0.036371111111111104,
      "sd": 0.2889203709283472
    },
    {
      "omitted_paper": "paper_nlp_raptor",
      "factor": "HyDE",
      "metric": "answer_relevancy",
      "n": 45,
      "mean": 0.07632222222222224,
      "sd": 0.23300836591388424
    },
    {
      "omitted_paper": "paper_nlp_raptor",
      "factor": "HyDE",
      "metric": "context_precision",
      "n": 45,
      "mean": -0.03105555555555556,
      "sd": 0.23253655094469025
    },
    {
      "omitted_paper": "paper_nlp_raptor",
      "factor": "HyDE",
      "metric": "context_recall",
      "n": 45,
      "mean": 0.044444444444444446,
      "sd": 0.29814239699997197
    },
    {
      "omitted_paper": "paper_nlp_raptor",
      "factor": "CAD",
      "metric": "faithfulness",
      "n": 43,
      "mean": 0.013399999999999999,
      "sd": 0.26550632581469513
    },
    {
      "omitted_paper": "paper_nlp_raptor",
      "factor": "CAD",
      "metric": "answer_relevancy",
      "n": 45,
      "mean": -0.02544,
      "sd": 0.2880452705896955
    },
    {
      "omitted_paper": "paper_nlp_raptor",
      "factor": "CAD",
      "metric": "context_precision",
      "n": 45,
      "mean": -0.015924444444444442,
      "sd": 0.08625172239533317
    },
    {
      "omitted_paper": "paper_nlp_raptor",
      "factor": "CAD",
      "metric": "context_recall",
      "n": 45,
      "mean": -0.022222222222222223,
      "sd": 0.14907119849998599
    },
    {
      "omitted_paper": "paper_nlp_raptor",
      "factor": "SCD_H0_same_context",
      "metric": "korean_ratio",
      "n": 45,
      "mean": 0.22000032045036125,
      "sd": 0.12508681888029666
    },
    {
      "omitted_paper": "paper_nlp_raptor",
      "factor": "SCD_all_states",
      "metric": "korean_ratio",
      "n": 45,
      "mean": 0.23004858881910362,
      "sd": 0.09871582812823515
    }
  ],
  "zero_denominator_sensitivity": [
    {
      "protocol": "exclude_zero_denominator_query",
      "metric": "korean_ratio",
      "effect": "H",
      "n": 59,
      "df1": 1,
      "df2": 58,
      "F": 2.940438684230774,
      "p": 0.0917263601007527,
      "partial_eta_squared": 0.04825102588228751,
      "contrast_mean": 0.05027407396362768,
      "contrast_sd": 0.22519773686043656,
      "status": "estimated",
      "sign_flip_p": 0.0921890781092189,
      "shapiro_difference_p": 3.1631757679922906e-06,
      "crosscheck": "statsmodels.AnovaRM versus orthogonal contrast t squared",
      "p_holm": 0.3669054404030108
    },
    {
      "protocol": "exclude_zero_denominator_query",
      "metric": "korean_ratio",
      "effect": "D",
      "n": 59,
      "df1": 1,
      "df2": 58,
      "F": 5.832990910431345,
      "p": 0.018901003731100617,
      "partial_eta_squared": 0.091378937869542,
      "contrast_mean": -0.03512013186226069,
      "contrast_sd": 0.11169571019059746,
      "status": "estimated",
      "sign_flip_p": 0.018099819001809982,
      "shapiro_difference_p": 0.026404766788986518,
      "crosscheck": "statsmodels.AnovaRM versus orthogonal contrast t squared",
      "p_holm": 0.1134060223866037
    },
    {
      "protocol": "exclude_zero_denominator_query",
      "metric": "korean_ratio",
      "effect": "S",
      "n": 59,
      "df1": 1,
      "df2": 58,
      "F": 332.9714919870023,
      "p": 1.0451418392572442e-25,
      "partial_eta_squared": 0.8516515879323289,
      "contrast_mean": 0.22692227258998493,
      "contrast_sd": 0.09552116356699877,
      "status": "estimated",
      "sign_flip_p": 9.99990000099999e-06,
      "shapiro_difference_p": 0.0770075758510703,
      "crosscheck": "statsmodels.AnovaRM versus orthogonal contrast t squared",
      "p_holm": 7.315992874800709e-25
    },
    {
      "protocol": "exclude_zero_denominator_query",
      "metric": "korean_ratio",
      "effect": "H:D",
      "n": 59,
      "df1": 1,
      "df2": 58,
      "F": 4.3909327597754775,
      "p": 0.04050619179937505,
      "partial_eta_squared": 0.070377738648049,
      "contrast_mean": -0.03616533692665324,
      "contrast_sd": 0.13256843457472683,
      "status": "estimated",
      "sign_flip_p": 0.037009629903700964,
      "shapiro_difference_p": 0.0007488106673686024,
      "crosscheck": "statsmodels.AnovaRM versus orthogonal contrast t squared",
      "p_holm": 0.20253095899687523
    },
    {
      "protocol": "exclude_zero_denominator_query",
      "metric": "korean_ratio",
      "effect": "H:S",
      "n": 59,
      "df1": 1,
      "df2": 58,
      "F": 0.7865409995703344,
      "p": 0.37881085301016937,
      "partial_eta_squared": 0.013379610131783109,
      "contrast_mean": 0.011009987636793417,
      "contrast_sd": 0.09535690664928902,
      "status": "estimated",
      "sign_flip_p": 0.38031619683803164,
      "shapiro_difference_p": 0.5403504699851228,
      "crosscheck": "statsmodels.AnovaRM versus orthogonal contrast t squared",
      "p_holm": 0.9525416574135926
    },
    {
      "protocol": "exclude_zero_denominator_query",
      "metric": "korean_ratio",
      "effect": "D:S",
      "n": 59,
      "df1": 1,
      "df2": 58,
      "F": 0.14535102513327186,
      "p": 0.7044113186564998,
      "partial_eta_squared": 0.0024997875594635934,
      "contrast_mean": -0.004828860471599419,
      "contrast_sd": 0.0972885236510699,
      "status": "estimated",
      "sign_flip_p": 0.7045629543704562,
      "shapiro_difference_p": 0.13209889489201826,
      "crosscheck": "statsmodels.AnovaRM versus orthogonal contrast t squared",
      "p_holm": 0.9525416574135926
    },
    {
      "protocol": "exclude_zero_denominator_query",
      "metric": "korean_ratio",
      "effect": "H:D:S",
      "n": 59,
      "df1": 1,
      "df2": 58,
      "F": 1.0166039954131088,
      "p": 0.3175138858045309,
      "partial_eta_squared": 0.017225728466045274,
      "contrast_mean": -0.012558094374610342,
      "contrast_sd": 0.09566957445386343,
      "status": "estimated",
      "sign_flip_p": 0.3209767902320977,
      "shapiro_difference_p": 0.4919559558462308,
      "crosscheck": "statsmodels.AnovaRM versus orthogonal contrast t squared",
      "p_holm": 0.9525416574135926
    }
  ]
}
```
