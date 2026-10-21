import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const build=path.resolve(process.env.MRAG_POSTER_BUILD_DIR??path.join(root,'tmp/query-revision/poster'));
await fs.mkdir(build,{recursive:true});
const data=JSON.parse(await fs.readFile(path.join(root,'FINALDOCS/ANALYSIS/POSTER_DATA.json'),'utf8'));
const skill=process.env.PRESENTATIONS_SKILL_DIR;
if(!skill)throw new Error('Set PRESENTATIONS_SKILL_DIR to the installed presentations skill directory.');
const {applyPresentationChartFont,finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const W=594*96/25.4,H=841*96/25.4,F='Malgun Gothic',ink='#263044',purple='#695184';
const p=Presentation.create({slideSize:{width:W,height:H}}),s=p.slides.add();s.background.fill='#FFFFFF';
const scene=[],texts=[],svg=[];let vectorOnly=false;let tableIndex=0;
const esc=x=>String(x).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
function rect(x,y,w,h,fill='white',stroke='none',sw=0){if(!vectorOnly)s.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill,line:{fill:stroke,width:sw}});scene.push({kind:'rect',x,y,w,h,fill,stroke,sw});svg.push(`<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}"/>`);}
function text(v,x,y,w,h,pt=21,bold=false,color=ink,align='left'){
 let a; if(!vectorOnly){a=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0},name:v.slice(0,70)});a.text=v;a.text.style={typeface:F,fontSize:pt*4/3,bold,color,alignment:align,verticalAlignment:'top',wrap:'none',autoFit:'none',insets:0};a.text.insets=0;}
 scene.push({kind:'text',text:v,x,y,w,h,pt,bold,color,align});if(!vectorOnly)texts.push(v);
 const sz=pt*4/3;v.split('\n').forEach((line,i)=>svg.push(`<text x="${align==='center'?x+w/2:align==='right'?x+w:x}" y="${y+sz+i*sz*1.25}" font-family="${F}" font-size="${sz}" font-weight="${bold?700:400}" fill="${color}" text-anchor="${align==='center'?'middle':align==='right'?'end':'start'}">${esc(line)}</text>`));return a;
}
function heading(v,x,y,w){rect(x,y,w,51,purple);text(v,x+12,y+4,w-24,43,25,true,'#FFFFFF');}
function table(rows,x,y,w,rh,widths,bolds=[]){
 tableIndex++;const cols=rows[0].length;const cw=widths.map(a=>a*w);const t=s.tables.add({rows:rows.length,columns:cols,left:x,top:y,width:w,height:rh*rows.length,columnWidths:cw,values:rows});t.borders.assign({style:'solid',fill:'#777777',width:.7});
 let yy=y;for(let r=0;r<rows.length;r++){t.rows[r].height=rh;let xx=x;for(let c=0;c<cols;c++){
  const bold=r===0||bolds.some(([a,b])=>a===r&&b===c);const al=r===0?'center':tableIndex===1||c===0?'left':'right';const cell=t.getCell(r,c);cell.fill='#FFFFFF';cell.text.style={typeface:F,fontSize:19*4/3,bold,color:ink,alignment:al,verticalAlignment:'middle',wrap:'none',autoFit:'none',insets:4};
  const lines=String(rows[r][c]).split('\n'),sz=19*4/3,lh=sz,ty=yy+(rh-lines.length*lh)/2;
  scene.push({kind:'rect',x:xx,y:yy,w:cw[c],h:rh,fill:'white',stroke:'#777777',sw:.7});svg.push(`<rect x="${xx}" y="${yy}" width="${cw[c]}" height="${rh}" fill="white" stroke="#777777" stroke-width=".7"/>`);
  for(let i=0;i<lines.length;i++){const tx=al==='right'?xx+cw[c]-6:al==='center'?xx+cw[c]/2:xx+6;scene.push({kind:'text',text:lines[i],x:xx+6,y:ty+i*lh,w:cw[c]-12,h:lh,pt:19,bold,color:ink,align:al});svg.push(`<text data-table-cell="${tableIndex}:${r}:${c}:${i}" x="${tx}" y="${ty+sz+i*lh}" font-family="${F}" font-size="${sz}" font-weight="${bold?700:400}" fill="${ink}" text-anchor="${al==='right'?'end':al==='center'?'middle':'start'}">${esc(lines[i])}</text>`);}
  texts.push(String(rows[r][c]));xx+=cw[c];}yy+=rh;}return t;
}
const types=data.types;
const get=(type,base,applied,metric)=>{
 const rows=data.type_results.filter(z=>z.level===type&&z.base===base&&z.applied===applied&&z.metric===metric);
 if(rows.length!==1)throw new Error('Missing or duplicate paired type result');return rows[0];
};
const fmt=n=>Number(n).toFixed(2),signed=n=>(n>=0?'+':'')+fmt(n);
const L=72,G=64,C=(W-2*L-G)/2,R=L+C+G;
rect(0,0,W,302,purple);
text('한국어 질의로 영어 학술·기술 문서를 검색하는',L,45,W-2*L,80,49,true,'white','center');
text('RAG에서의 HyDE·CAD·SCD 조합 실험',L,137,W-2*L,80,49,true,'white','center');
text('질문 유형별 점수와 실제 검색·답변의 변화',L,239,W-2*L,45,25,false,'white','center');
heading('01 연구 배경과 목적',L,350,C);
text('- 한국어 질문으로 영어 근거를 찾고 한국어로 답하는 RAG\n- 검색 입력·근거 반영·출력 언어를 조정하는 세 기법 비교\n- 질문 유형별 점수와 실제 답변의 요구 정보 충족을 확인',L,426,C,130,21);
heading('02 파이프라인과 기법 적용 위치',L,579,C);
const nodes=[['한국어 질문','HyDE: 영어 번역·가상 문서로 밀집 검색 입력 구성'],['검색과 재정렬','BGE-M3 + BM25 → 가중 RRF → CrossEncoder'],['영어 검색 근거 + 질문','상위 5개 구간 · Mi:dm 2.0 Base Instruct'],['CAD · SCD → 생성 답변','CAD: 문맥 포함/제외 로짓 결합 · SCD: 언어별 조정']];
for(let i=0;i<nodes.length;i++){const y=656+i*115;rect(L,y,C,90,'white',purple,1.3);text(nodes[i][0],L+14,y+7,C-28,35,22,true);text(nodes[i][1],L+14,y+49,C-28,31,18);if(i<3)text('↓',L+C/2-20,y+90,40,25,18,true,purple,'center');}
text('- BM25·재정렬에는 한국어 원질의 사용\n- HyDE의 번역·가상 문서는 각 적용 조건에서 다시 생성',L,1122,C,82,20);
heading('03 질문·조건과 평가 지표',L,1234,C);
text('- 영어 문서 4종 · 문서별 15개 질문 = 60개\n- RAG Survey · CAD · RAPTOR · Mi:dm K 2.5\n- 사실·정의 8 / 방법·절차 29 / 결과·비교 20 / 목적·기여 3\n- 동일 질문 60개 × 8개 조건 = 생성 기록 480개',L,1310,C,140,20);
text('1 미적용 · 2 CAD · 3 HyDE · 4 HyDE+CAD\n5 SCD · 6 CAD+SCD · 7 HyDE+SCD · 8 HyDE+CAD+SCD',L,1454,C,82,19);
text('HyDE: Hypothetical Document Embeddings\nCAD: Context-Aware Decoding\nSCD: Soft Constrained Decoding',L,1554,C,115,19);
text('- 품질 평가: 조건 1~4 영어 근거 / 5~8 한국어 번역 근거\n- 답변 생성 근거와 참조 답변은 영어\n- 결측 충실도 5개는 해당 비교의 두 평균에서 함께 제외',L,1684,C,128,20);
table([['지표','측정하는 내용'],['근거 충실도','답변 주장이 입력 근거로 뒷받침되는 비율'],['답변 관련성','역생성 질문과 원질문의 임베딩 유사도'],['문맥 정밀도','유용한 검색 구간이 상위에 배치되는 정도'],['문맥 재현율','참조 답변의 근거가 검색 결과에 포함된 비율'],['한국어 문자 비율','한글 / (한글 + ASCII 영문자)']],L,1836,C,54,[.25,.75]);
text('- 관측 점수 0~1; 높을수록 각 측정값 증가\n- 관련성 이론 범위 -1~1; 회피·모호 응답 판정 시 0점\n- 문자 비율은 출력 문자의 구성, 충실도는 주장의 근거',L,2176,C,106,18);
text('단일 기법의 처리 시간 · 방법·절차 29개 질문',L,2300,C,36,20,true);
const timeRows=[['기법','기준(초)','적용(초)','평균 변화(초)']];
for(const applied of ['H0C1S0','H1C0S0','H0C0S1']){
 const z=get('방법 및 절차','H0C0S0',applied,'duration_seconds');
 const name=data.conditions.find(c=>c.code===applied).name;
 timeRows.push([name,fmt(z.base_mean),fmt(z.applied_mean),signed(z.mean_delta)]);
}
const maxTime=Math.max(...timeRows.slice(1).map(r=>Number(r[2])));
table(timeRows,L,2345,C,44,[.25,.23,.23,.29],timeRows.slice(1).flatMap((r,i)=>Number(r[2])===maxTime?[[i+1,2]]:[]));
text('기준: 미적용 · 굵은 값: 가장 긴 적용 시간 · 짧을수록 비용 감소',L,2526,C,34,16);
heading('04 점수와 실제 답변의 내용',L,2582,C);
for(const [i,c] of data.cases.entries()){
 const fa=c.scores.faithfulness,ar=c.scores.answer_relevancy;
 text(`${c.title}\n- 요구: ${c.required_information}\n- ${c.poster_observation}\n- 관련성 ${fmt(ar.base)}→${fmt(ar.applied)} / 충실도 ${fmt(fa.base)}→${fmt(fa.applied)}`,L,2656+i*136,C,128,18);
}
heading('05 질문 유형별 핵심 비교',R,350,C);
function typeTable(base,applied,metric,y){
 const rows=[['질문 유형','n','기준\n평균','적용\n평균','평균\n변화량','개선/악화/비슷']];
 for(const t of types){const z=get(t,base,applied,metric);rows.push([t.replace(' 및 ','·'),String(z.n),fmt(z.base_mean),fmt(z.applied_mean),signed(z.mean_delta),`${z.improved}/${z.worse}/${z.similar}`]);}
 const max=Math.max(...rows.slice(1).map(r=>Number(r[3])));
 table(rows,R,y,C,55,[.26,.07,.12,.12,.14,.29],rows.slice(1).flatMap((r,i)=>Number(r[3])===max?[[i+1,3]]:[]));
}
text('답변 관련성 · 기준 미적용 → 적용 HyDE · 영어 근거 평가',R,426,C,36,20,true);
typeTable('H0C0S0','H1C0S0','answer_relevancy',475);
text('- 방법·절차의 평균 변화 +0.17 · 개선 14 / 악화 3 / 비슷 12\n- 0점에서 양수가 된 6개 질문에 근거 회복과 원문 이어 쓰기 포함',R,765,C,64,18);
text('답변 관련성 · 기준 SCD → 적용 HyDE+SCD · 한국어 번역 평가',R,850,C,36,19,true);
typeTable('H0C0S1','H1C0S1','answer_relevancy',900);
text('- 방법·절차의 평균 변화 +0.16 · 개선 12 / 악화 7 / 비슷 10\n- 사실·정의의 평균 상승 +0.09에는 한 질문의 큰 상승 포함',R,1190,C,64,18);
text('한국어 문자 비율 · 기준 HyDE → 적용 HyDE+SCD',R,1274,C,36,20,true);
typeTable('H1C0S0','H1C0S1','korean_ratio',1324);
text('주: 차이 >0.05 개선, <-0.05 악화, 나머지 비슷함\n굵은 값: 같은 비교의 네 유형 중 적용 평균 최댓값(동률 모두)',R,1615,C,66,17);
heading('06 전체 질문의 원점수 평행좌표',R,1710,C);
const metricKeys=['faithfulness','answer_relevancy','context_precision','context_recall','korean_ratio'];
const categories=['근거\n충실도','답변\n관련성','문맥\n정밀도','문맥\n재현율','한국어\n문자 비율'];
const typeColors=['#8C510A','#2166AC','#B2182B','#1B7837'];
function tint(hex){const rgb=[1,3,5].map(k=>Math.round(parseInt(hex.slice(k,k+2),16)*.38+255*.62));return '#'+rgb.map(v=>v.toString(16).padStart(2,'0')).join('');}
const chartSeries=[];
function parallel(code,top){
 const observations=data.question_scores.filter(z=>z.condition===code);
 if(observations.length!==60)throw new Error('A parallel panel must include all 60 questions');
 const series=observations.map(r=>{const color=tint(typeColors[types.indexOf(r.question_type)]);return {name:r.short_title,values:metricKeys.map(m=>r[m]===null?null:Number(fmt(r[m]))),fill:color,line:{fill:color,width:1.3,style:'solid'}};});
 chartSeries.push({condition:code,series});
 text((code==='H0C0S0'?'미적용':'HyDE')+' · 영어 근거 평가 · 60개 질문',R,top,C,31,18,true);
 const chart=s.charts.add('line',{position:{left:R,top:top+38,width:C,height:228},categories,series,lineOptions:{smooth:false},hasLegend:false,xAxis:{tickLabelPosition:'low',textStyle:{fontSize:20},majorGridlines:{fill:'#BBBBBB',width:.6}},yAxis:{min:0,max:1,majorUnit:.5,numberFormatCode:'0.0',textStyle:{fontSize:20},majorGridlines:{fill:'#DDDDDD',width:.6}},displayBlanksAs:'gap',dataLabels:{showValue:false}});
 applyPresentationChartFont(chart,{fontFamily:F});
 vectorOnly=true;
 const cx=R+54,cy=top+58,cw=C-73,ch=148;
 for(const tick of [0,.5,1]){const yy=cy+(1-tick)*ch;rect(cx,yy,cw,1,'#DDDDDD');text(tick.toFixed(1),R,yy-13,44,28,15,false,ink,'right');}
 for(let i=0;i<5;i++){const xx=cx+i*cw/4;rect(xx,cy,1,ch,'#BBBBBB');text(categories[i],xx-58,cy+ch+12,116,55,15,false,ink,'center');}
 for(const z of series){let points=[];const flush=()=>{if(points.length>1){svg.push(`<polyline points="${points.map(v=>v.join(',')).join(' ')}" fill="none" stroke="${z.fill}" stroke-width="1.3"/>`);scene.push({kind:'polyline',points,color:z.fill,width:1.3,dash:[]});}points=[];};z.values.forEach((v,k)=>{if(v===null)flush();else points.push([cx+k*cw/4,cy+(1-v)*ch]);});flush();}
 vectorOnly=false;
}
parallel('H0C0S0',1780);parallel('H1C0S0',2070);
for(let i=0;i<types.length;i++){const x=R+(i%2)*C/2,y=2360+Math.floor(i/2)*34;rect(x,y+12,24,4,typeColors[i]);text(types[i].replace(' 및 ','·'),x+35,y,C/2-35,32,17);}
text('- 선 하나는 질문 하나 · 다섯 축은 0~1의 관측 원점수\n- 결측은 해당 축에서 선을 끊어 표시',R,2445,C,66,17);
heading('07 결과와 결론',R,2542,C);
text('- 방법·절차: HyDE 추가 후 두 평가 언어의 관련성 평균 상승\n- 실제 출력에는 근거 회복·다른 주제의 설명·표 행 오인이 공존\n- 네 유형 모두 SCD 추가 후 한국어 문자 비율 평균 상승\n- 질문이 요구한 정보와 실제 검색·답변을 적용 결과에 연결',R,2615,C,170,20);
text('- 관측 범위: 영어 문서 4종 · 한국어 질문 60개\n- 질문·조건별 한 번 생성·평가 · 목적·기여 3개\n- 후속 비교: 질문 구성의 균형, 반복 평가와 사람의 요구 항목 검토',R,2805,C,115,18);
heading('핵심 참고문헌',L,2952,W-2*L);
text('[1] Lewis et al. RAG. NeurIPS, 2020.  [2] Gao et al. HyDE. ACL, 2023.\n[3] Shi et al. Context-Aware Decoding. NAACL, 2024.\n[4] Li et al. Language Drift and SCD. AAAI, 2026.  [10] Es et al. RAGAs. EACL, 2024.',L,3023,W-2*L,100,18);
s.speakerNotes.text='Data: FINALDOCS/ANALYSIS/POSTER_DATA.json. Complete 60-question analysis precedes case selection. Five native tables and two editable parallel-coordinate panels. Null scores remain gaps. Quality comparisons stay within an evaluation language; time includes only individual techniques. No original run or score changed.';
await fs.writeFile(path.join(build,'scene.json'),JSON.stringify({width:W,height:H,ops:scene,texts,chartSeries},null,2));
await fs.writeFile(path.join(build,'poster.svg'),`<svg xmlns="http://www.w3.org/2000/svg" width="594mm" height="841mm" viewBox="0 0 ${W} ${H}"><rect width="${W}" height="${H}" fill="white"/>${svg.join('')}</svg>`);
await(await PresentationFile.exportPptx(p)).save(path.join(build,'candidate.pptx'));
await fs.writeFile(path.join(build,'native.png'),new Uint8Array(await(await s.export({format:'png',scale:.55})).arrayBuffer()));
console.log('BUILT',build);
if(process.argv.includes('--finalize')){
 if(!process.env.PYTHON_EXECUTABLE)throw new Error('Set PYTHON_EXECUTABLE for presentation validation.');
 const revision=process.env.QUESTION_POSTER_REVISION;
 if(!revision)throw new Error('Set QUESTION_POSTER_REVISION to a new review revision.');
 const final=path.join(root,'tmp/query-revision/poster-final',revision,'M_RAG_A1_FINAL_EDITABLE.pptx');await fs.mkdir(path.dirname(final),{recursive:true});
 await finalizePresentation({workspaceDir:root,candidatePath:path.join(build,'candidate.pptx'),finalPath:final,pythonExecutable:process.env.PYTHON_EXECUTABLE,integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','21384000,30276000','--validate-heading-fit','--require-native-table-slide','1'],explicitTotalSlideCount:1,requiredNativeTableOwnerSlides:[1],requiredNativeChartOwnerSlides:[1],materializeLiteralChartWorkbooks:true,fontPolicy:{basis:'design',families:[F]},verifyArtifactToolImport:true,receiptPath:path.join(build,'FINALIZATION.'+revision+'.json')});
 console.log('FINALIZED',final);
}
