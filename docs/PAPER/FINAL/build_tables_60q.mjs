import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..", "..", "..");
const generated = path.join(here, "generated");
const csvOut = path.join(here, "tables_60q_csv");
const output = path.join(here, "TABLES_60Q.xlsx");
const runtimeModules = "C:/Users/KiKi/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules";
const pkg = JSON.parse(await fs.readFile(path.join(runtimeModules, "@oai/artifact-tool/package.json"), "utf8"));
const entry = typeof pkg.exports?.["."] === "string" ? pkg.exports["."] : pkg.exports?.["."]?.default ?? pkg.main;
const { SpreadsheetFile, Workbook } = await import(pathToFileURL(path.join(runtimeModules, "@oai/artifact-tool", entry)).href);

function parseCsv(text) {
  const lines = text.trim().split(/\r?\n/);
  const cells = (line) => {
    const result = []; let current = ""; let quoted = false;
    for (let i = 0; i < line.length; i += 1) {
      const ch = line[i];
      if (ch === '"' && line[i + 1] === '"') { current += '"'; i += 1; }
      else if (ch === '"') quoted = !quoted;
      else if (ch === "," && !quoted) { result.push(current); current = ""; }
      else current += ch;
    }
    result.push(current); return result;
  };
  const [headers, ...rows] = lines.map(cells);
  return rows.map((row) => Object.fromEntries(headers.map((header, i) => [header, row[i] ?? ""])));
}

async function csv(name) { return parseCsv(await fs.readFile(path.join(generated, name), "utf8")); }
function number(value) { const parsed = Number(value); return Number.isFinite(parsed) ? parsed : value; }
function configLabel(value) { return value.replace("hyde_", "H").replace("__", " / ").replace("no_decoder_control", "C0 S0").replace("cad_only", "C1 S0").replace("scd_only", "C0 S1").replace("cad_scd", "C1 S1").replace("off", "0").replace("on", "1"); }
function csvText(rows) { return rows.map((row) => row.map((cell) => `"${String(cell ?? "").replaceAll('"', '""')}"`).join(",")).join("\r\n") + "\r\n"; }

const tables = [];
function add(name, title, headers, rows, source) { tables.push({ name, title, headers, rows, source }); }

add("T3-1_Requirements", "표 3-1. 연구 및 실험 요구사항", ["요구사항", "확인 기준", "값"], [
  ["한국어 질의 기반 영문 문서 QA", "질의와 대상 문서 연결", "60개 질의-문서 쌍"],
  ["실험 요인", "HyDE·CAD·SCD ON/OFF", "2×2×2, 8개 조건"],
  ["생성 기록", "조건별 저장 record", "480개, 조건별 60개"],
  ["출력 언어", "한국어 문자 비율", "SCD ON/OFF 240개 대응쌍"],
  ["추적성", "source hash와 generation record", "검증 보고서에 기록"],
], "generated/EXPERIMENT_60_VALIDATION.md");

const configRows = (await csv("rag_cube_config_scores_60q.csv")).map((r) => [configLabel(r.config), r.config.includes("hyde_on") ? "ON" : "OFF", r.config.includes("cad") ? "ON" : "OFF", r.config.includes("scd") ? "ON" : "OFF", number(r.n_generations)]);
add("T3-2_RAG-Cube", "표 3-2. RAG-Cube 8개 조건", ["조건", "HyDE", "CAD", "SCD", "생성 수"], configRows, "generated/rag_cube_config_scores_60q.csv");
add("T3-3_Factor_Position", "표 3-3. 실험 요인별 적용 위치와 비교 단위", ["요인", "적용 위치", "주 비교", "주 지표"], [
  ["HyDE", "검색 표현 확장", "CAD OFF·SCD OFF의 60 대응쌍", "RAGAS 4개 품질 지표"],
  ["CAD", "문맥 기반 decoding", "동일 문맥 60 대응쌍, faithfulness 58 완결쌍", "RAGAS 4개 품질 지표"],
  ["SCD", "출력 token logit 제어", "동일 query·HyDE·CAD의 240 ON/OFF쌍", "한국어 문자 비율"],
], "generated/EXPERIMENT_60_VALIDATION.md");
add("T4-1_Environment", "표 4-1. 실험 실행 환경", ["구성", "저장 record 기준 값"], [
  ["생성 모델", "K-intelligence/Midm-2.0-Base-Instruct"], ["디코딩", "deterministic greedy"],
  ["검색 backend", "BGE-M3 dense + BM25 sparse + RRF + CrossEncoder rerank"], ["retrieval pool / rerank", "8 / 8"], ["문맥 수", "5"],
], "60-query generation record fields");
add("T4-2_Backbone", "표 4-2. 고정 Paper-RAG backbone", ["단계", "고정 구성"], [
  ["입력", "한국어 질의와 지정 대상 문서"], ["검색", "BGE-M3 dense retrieval + BM25 sparse retrieval"],
  ["결합", "weighted Reciprocal Rank Fusion"], ["재정렬", "CrossEncoder reranking"], ["생성", "Mi:dm 2.0 Base Instruct, max_new_tokens=512"],
], "60-query generation record fields");
const runtime = (await csv("runtime_summary_60q.csv")).map((r) => [configLabel(r.config), number(r.n_generations), number(r.duration_mean_seconds), number(r.duration_median_seconds)]);
add("T4-3_Runtime", "표 4-3. 조건별 평균 생성시간", ["조건", "생성 수", "평균 초", "중앙값 초"], runtime, "generated/runtime_summary_60q.csv");
add("T4-4_Record_Fields", "표 4-4. generation record 주요 필드", ["구분", "필드"], [
  ["식별", "query_id, paper, config_name, status"], ["요인", "use_hyde, use_cad, use_scd, parameter fields"],
  ["검색", "retrieved_chunk_ids, reranked_chunk_ids, contexts"], ["생성", "generated_answer, duration_seconds, decoding_mode"], ["재현", "generation_model, retrieval backend, context count"],
], "60-query generation record schema");
add("T5-1_Dataset", "표 5-1. 4개 문서 × 15개 질의", ["대상 문서", "질의 수"], [["RAG Survey", 15], ["CAD", 15], ["RAPTOR", 15], ["Mi:dm K 2.5 Pro Technical Report", 15], ["합계", 60]], "generated/QUERY_60_AUDIT.md");
const scoreRows = (await csv("rag_cube_config_scores_60q.csv")).map((r) => [configLabel(r.config), number(r.n_generations), ...["faithfulness_mean", "answer_relevancy_mean", "context_precision_mean", "context_recall_mean", "korean_ratio_mean"].map((key) => number(r[key]))]);
add("T5-2_Config_Scores", "표 5-2. 8개 config 평균 품질", ["조건", "생성 수", "Faithfulness", "Answer relevancy", "Context precision", "Context recall", "Korean ratio"], scoreRows, "generated/rag_cube_config_scores_60q.csv");
function primaryRows(name) { return csv(name).then((rows) => rows.map((r) => [r.metric, number(r.mean_delta_on_minus_off), r.bootstrap_mean_95_ci, number(r["wins_gt_0.01"]), number(r["losses_lt_neg_0.01"]), number(r["ties_abs_le_0.01"]), number(r.n_queries)])); }
add("T5-3_HyDE", "표 5-3. HyDE primary 통제 비교", ["지표", "평균 변화 ON-OFF", "95% CI", "Win", "Loss", "Tie", "n"], await primaryRows("hyde_primary_60q.csv"), "generated/hyde_primary_60q.csv");
add("T5-4_CAD", "표 5-4. CAD primary 동일 문맥 비교", ["지표", "평균 변화 ON-OFF", "95% CI", "Win", "Loss", "Tie", "n"], await primaryRows("cad_primary_60q.csv"), "generated/cad_primary_60q.csv");
const scdRows = (await csv("scd_language_summary_60q.csv")).map((r) => [configLabel(r.off_config), configLabel(r.on_config), number(r.n_pairs), number(r.mean_delta), number(r.ci95_lower), number(r.ci95_upper), number(r.increases_gt_0_02), number(r.decreases_lt_neg_0_02), number(r.ties_abs_le_0_02)]);
add("T5-5_SCD_Config", "표 5-5. SCD configuration별 언어 결과", ["SCD OFF", "SCD ON", "쌍 수", "평균 변화", "CI 하한", "CI 상한", "증가", "감소", "동률"], scdRows, "generated/scd_language_summary_60q.csv");
add("T5-6_SCD_Paired", "표 5-6. SCD matched-pair 요약", ["비교", "쌍 수", "한국어 문자 비율 평균 변화", "95% CI", "증가/감소/동률"], [
  ["전체 ON/OFF 대응", 240, 0.2289, "[+0.2051, +0.2532]", "219 / 10 / 11"], ["HyDE OFF 동일 문맥", 120, 0.2182, "[+0.1880, +0.2487]", "see analysis artifact"],
], "generated/RESULT_REVIEW_60Q.md");
const paper = (await csv("paper_level_exploratory_60q.csv")).map((r) => [r.group, r.factor, r.metric, number(r.n_queries), number(r.mean_delta)]);
const type = (await csv("query_type_exploratory_60q.csv")).map((r) => [r.group, r.factor, r.metric, number(r.n_queries), number(r.mean_delta)]);
add("Appendix_Paper", "부록 표. 문서별 탐색 분석", ["대상 문서", "요인", "지표", "n", "평균 변화"], paper, "generated/paper_level_exploratory_60q.csv");
add("Appendix_QueryType", "부록 표. 질문 유형별 탐색 분석", ["질문 유형", "요인", "지표", "n", "평균 변화"], type, "generated/query_type_exploratory_60q.csv");

await fs.mkdir(csvOut, { recursive: true });
for (const table of tables) await fs.writeFile(path.join(csvOut, `${table.name}.csv`), csvText([table.headers, ...table.rows]), "utf8");

const wb = Workbook.create();
for (const table of tables) {
  const sheet = wb.worksheets.add(table.name); sheet.showGridLines = false;
  const cols = table.headers.length;
  sheet.getRangeByIndexes(1, 0, 1, cols).merge();
  sheet.getCell(1, 0).values = [[table.title]];
  sheet.getCell(1, 0).format = { font: { name: "Arial", size: 14, bold: true, color: "#222222" } };
  sheet.getCell(2, 0).values = [[`출처: ${table.source}`]];
  sheet.getCell(2, 0).format = { font: { name: "Arial", size: 9, italic: true, color: "#555555" } };
  const values = [table.headers, ...table.rows];
  const range = sheet.getRangeByIndexes(4, 0, values.length, cols); range.values = values;
  sheet.getRangeByIndexes(4, 0, 1, cols).format = { fill: "#334155", font: { name: "Arial", size: 10, bold: true, color: "#FFFFFF" }, horizontalAlignment: "center", verticalAlignment: "center", wrapText: true };
  const body = sheet.getRangeByIndexes(5, 0, Math.max(values.length - 1, 1), cols);
  body.format = { font: { name: "Arial", size: 10, color: "#222222" }, verticalAlignment: "center", wrapText: true, borders: { preset: "insideHorizontal", style: "thin", color: "#D9D9D9" } };
  range.format.borders = { preset: "outside", style: "thin", color: "#94A3B8" };
  range.format.autofitColumns(); range.format.autofitRows();
  for (let c = 0; c < cols; c += 1) { const col = sheet.getRangeByIndexes(4, c, values.length, 1); if (col.format.columnWidth > 36) col.format.columnWidth = 36; if (col.format.columnWidth < 12) col.format.columnWidth = 12; }
  sheet.getRangeByIndexes(5, 0, Math.max(values.length - 1, 1), 1).format.horizontalAlignment = "left";
  sheet.freezePanes.freezeRows(5);
  sheet.tables.add(sheet.getRangeByIndexes(4, 0, values.length, cols).address, true, `${table.name.replaceAll(/[^A-Za-z0-9]/g, "")}Table`);
}
wb.recalculate();
const inspect = await wb.inspect({ kind: "workbook,sheet,table", maxChars: 8000, tableMaxRows: 6, tableMaxCols: 10 });
console.log(inspect.ndjson);
const errors = await wb.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!", options: { useRegex: true, maxResults: 100 }, summary: "formula errors" });
console.log(errors.ndjson);
const preview = await wb.render({ sheetName: "T5-2_Config_Scores", autoCrop: "all", scale: 1, format: "png" });
await fs.writeFile(path.join(here, "TABLES_60Q_preview.png"), new Uint8Array(await preview.arrayBuffer()));
const xlsx = await SpreadsheetFile.exportXlsx(wb); await xlsx.save(output);
console.log(JSON.stringify({ output, sheets: tables.map((t) => t.name), csvOut }, null, 2));
