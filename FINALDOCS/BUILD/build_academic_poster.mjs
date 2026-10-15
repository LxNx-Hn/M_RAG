import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const outputArg=process.argv.indexOf('--output');
if(outputArg<0 || !process.argv[outputArg+1]) throw new Error('--output directory is required');
const tmp=path.resolve(process.argv[outputArg+1]);
const fieldsArg=process.argv.indexOf('--personal-fields');
const fields=fieldsArg<0?null:JSON.parse(await fs.readFile(process.argv[fieldsArg+1],'utf8'));
const stats=JSON.parse(await fs.readFile(root+'/FINALDOCS/DATA/FACTORIAL_STATISTICS_60Q.json','utf8'));
const data=JSON.parse(await fs.readFile(root+'/FINALDOCS/DATA/THESIS_TABLES_60Q.json','utf8'));
const title=JSON.parse(await fs.readFile(root+'/FINALDOCS/DATA/REVISION_CONTRACT_20261015.json','utf8')).title;
const W=594*96/25.4,H=841*96/25.4, font='Malgun Gothic';
const purple='#695184',ink='#24324A',line='#D8CFE4',blue='#2F6DF6',green='#16846F',orange='#CF6800';
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const f=x=>Number(x).toFixed(3), p=x=>x<.001?'<0.001':f(x);
for(const personal of fields?[false,true]:[false]) {
  const out=tmp+(personal?'/poster_submission':'/poster_public'); await fs.mkdir(out,{recursive:true});
  const pres=Presentation.create({slideSize:{width:W,height:H}});
  const sl=pres.slides.add(); sl.background.fill='#FFFFFF';
  const svg=[]; const texts=[]; const geometry=[]; let tableIndex=0;
  function rect(x,y,w,h,fill,stroke='none',sw=0) {
    const shape=sl.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill,line:{fill:stroke,width:sw,style:'solid'}});
    svg.push(`<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}"/>`);return shape;
  }
  function text(s,x,y,w,h,pt=18,bold=false,color=ink,align='left') {
    const sh=sl.shapes.add({geometry:'textbox',name:s.replaceAll('\n',' ').slice(0,65),position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
    sh.text=s; sh.text.style={typeface:font,fontSize:pt*4/3,bold,color,alignment:align,verticalAlignment:'top',autoFit:'none',wrap:'none',insets:0};
    sh.text.insets=0;
    const fs=pt*4/3, lh=fs*1.25;
    for(const [i,t] of s.split('\n').entries()) svg.push(`<text x="${align==='center'?x+w/2:align==='right'?x+w:x}" y="${y+fs+i*lh}" font-family="Malgun Gothic,NanumGothic,sans-serif" font-size="${fs}" font-weight="${bold?700:400}" fill="${color}" text-anchor="${align==='center'?'middle':align==='right'?'end':'start'}">${esc(t)}</text>`);
    texts.push(s);geometry.push({text:s,x,y,w,h,pt});return sh;
  }
  function heading(s,x,y,w) {rect(x,y,w,46,purple);text(s,x+10,y+3,w-20,40,24,false,'#FFFFFF');}
  function arrow(x,y,w,h,rotate=0) {
    sl.shapes.add({geometry:'rightArrow',position:{left:x,top:y,width:w,height:h,rotation:rotate},fill:ink,line:{fill:ink,width:0}});
    if(rotate===0)svg.push(`<path d="M${x},${y+h*.35}h${w*.6}v${-h*.35}l${w*.4},${h*.5}l${-w*.4},${h*.5}v${-h*.35}h${-w*.6}z" fill="${ink}"/>`);
    else svg.push(`<path d="M${x+w*.35},${y}v${h*.6}h${-w*.35}l${w*.5},${h*.4}l${w*.5},${-h*.4}h${-w*.35}v${-h*.6}z" fill="${ink}"/>`);
  }
  function box(s,x,y,w,h,stroke=purple) {rect(x,y,w,h,'#FBFAFD',stroke,2);text(s,x+8,y+12,w-16,h-12,18,false,ink,'center');}
  function table(values,x,y,w,rowH,widths,columnTypes,pt=18) {
    tableIndex++;
    const n=values.length,c=values[0].length;
    if(columnTypes.length!==c || columnTypes.some(t=>!['code','number','description'].includes(t))) throw new Error('Explicit table column types required');
    const cw=(widths??Array(c).fill(1/c)).map(z=>z*w);
    const rowHeights=Array(n).fill(rowH);
    if(rowH<64 && values[0].some(v=>String(v).includes('\n')))rowHeights[0]=64;
    const tb=sl.tables.add({rows:n,columns:c,left:x,top:y,width:w,height:rowHeights.reduce((a,b)=>a+b,0),columnWidths:cw,values});
    tb.borders.assign({style:'solid',fill:line,width:0.7});
    let rowY=y;
    for(let r=0;r<n;r++) {
      const currentH=rowHeights[r];
      tb.rows[r].height=currentH;
      let xx=x;
      for(let col=0;col<c;col++) {
        const cell=tb.getCell(r,col);cell.fill=r===0?'#EAE4F1':r%2?'#FFFFFF':'#F8F6FA';
        cell.text.style={typeface:font,fontSize:pt*4/3,bold:r===0,color:ink,alignment:r===0?'center':columnTypes[col]==='number'?'right':columnTypes[col]==='description'?'left':'center',verticalAlignment:'middle',insets:4,autoFit:'none',wrap:'none'};
        const alignment=r===0?'center':columnTypes[col]==='number'?'right':columnTypes[col]==='description'?'left':'center';
        const lines=String(values[r][col]).split('\n'),fs=pt*4/3,lh=fs*1.25;
        svg.push(`<rect x="${xx}" y="${rowY}" width="${cw[col]}" height="${currentH}" fill="${r===0?'#EAE4F1':r%2?'#FFFFFF':'#F8F6FA'}" stroke="${line}" stroke-width="0.7"/>`);
        const yy=rowY+(currentH-lines.length*lh)/2;
        for(let k=0;k<lines.length;k++)svg.push(`<text data-table-cell="${tableIndex}:${r}:${col}:${k}" x="${alignment==='left'?xx+6:alignment==='right'?xx+cw[col]-6:xx+cw[col]/2}" y="${yy+fs+k*lh}" font-family="Malgun Gothic,NanumGothic,sans-serif" font-size="${fs}" font-weight="${r===0?700:400}" fill="${ink}" text-anchor="${alignment==='left'?'start':alignment==='right'?'end':'middle'}">${esc(lines[k])}</text>`);
        xx+=cw[col];
      }
      rowY+=currentH;
    }
    texts.push(...values.flat().map(String));return tb;
  }
  rect(0,0,W,322,purple);
  text('한국어 질의로 영어 학술·기술 문서를 검색하는',56,46,W-112,90,52,false,'#FFFFFF','center');
  text('RAG에서의 HyDE·CAD·SCD 조합 실험',56,143,W-112,90,52,false,'#FFFFFF','center');
  const identity=personal?`${fields.name} ${fields.student_id}`:'문종건';
  if(personal && (!fields.name || !fields.student_id)) throw new Error('Personal fields require name and student_id');
  text(identity+' · 동국대학교 WISE캠퍼스 컴퓨터공학과 · 지도교수 김진석 · 2026.10.15',56,261,W-112,36,20,false,'#FFFFFF','center');
  const L=74,G=54,C=(W-2*L-G)/2,R=L+C+G;
  heading('01 연구 배경과 목적',L,365,C);
  text('검색 증강 생성(Retrieval-Augmented Generation, RAG)은\n관련 문서 구간을 검색하고 그 텍스트로 답변을 생성한다[1].',L,430,C,68,18);
  text('HyDE(Hypothetical Document Embeddings): 가상 문서 검색[2]\nCAD(Context-Aware Decoding): 검색 근거의 영향 조정[3]\nSCD(Soft Constrained Decoding): 출력 언어 제어[4]',L,515,C,102,18);
  text('한국어 질문에 맞는 영어 근거를 찾고 한국어로 답변하는\n과정에서는 검색 관련성과 근거 활용·출력 언어를 함께\n평가할 필요가 있다. 본 연구는 같은 파이프라인에서\n세 기법의 적용 여부와 조합에 따른 결과를 비교한다.',L,634,C,128,18,true);
  heading('02 Paper-RAG 구조와 기법 적용 위치',L,773,C);
  text('Paper-RAG는 본 연구의 고정 검색·생성 파이프라인이다.',L,837,C,36,18);
  const b=(C-44)/2;
  box('한국어 질의\nHyDE OFF: 원질의\nHyDE ON: 영어 번역·가상 문서',L,894,b,118,blue);
  box('BM25 희소 검색[6]\n한국어 원질의 사용',L+b+44,894,b,118);
  box('BGE-M3 밀집 검색[5]',L,1046,b,64,blue);
  box('가중 RRF[7]\n0.6 / 0.4, k=60',L+b+44,1046,b,78);
  arrow(L+b/2-9,1018,18,22,90);arrow(L+b+8,1062,28,20);
  arrow(L+b+44+b/2-9,1018,18,22,90);
  box('원질의 기반 CrossEncoder 재정렬[8]\n상위 5개 구간 선택·문맥 길이 관리',L,1156,C,84);
  box('Mi:dm 2.0 Base Instruct[18]\nCAD 로짓 결합 후 SCD 언어별 조정, 최종 답변 생성',L,1274,C,83,green);
  arrow(L+C/2-9,1131,18,18,90);arrow(L+C/2-9,1248,18,18,90);
  heading('03 3요인 완전요인 실험 설계',L,1390,C);
  text('H=HyDE, C=CAD, S=SCD   0=미적용, 1=적용',L,1450,C,36,18);
  const conditions=Object.keys(stats.descriptives);
  table([['조건','H','C','S'],...conditions.map(z=>[z,z[1],z[3],z[5]])],L,1497,C,36,[.46,.18,.18,.18],['code','code','code','code']);
  text('영어 문서 4종 × 15개 질의 × 8조건 = 480개 생성 기록',L,1840,C,34,18,true);
  text('생성 512토큰, CAD α=0.5, SCD α=1.1·β=0.9·Tstart=5',L,1884,C,34,18);
  text('문서 요약을 15개 내용 단위로 나누어 질의를 작성하고,\n총 60개 질의의 원문 페이지·정답 근거·답변 가능성을 확인',L,1930,C,62,18);
  heading('04 평가 지표 및 실험·통계 방법',L,2010,C);
  text('근거 충실도: 답변 주장 중 검색 근거가 뒷받침하는 비율\n답변 관련성: 답변에서 만든 질문과 원질문의 의미 유사도\n문맥 정밀도: 참조 답변에 유용한 구간의 상위 배치 정도\n문맥 재현율: 참조 답변 주장을 검색 문맥이 포괄하는 비율\n한국어 비율: 한글 / (한글 + ASCII 영문자)',L,2070,C,150,18);
  text('품질 관측값은 0~1이며, 높은 값은 각 측정 특성이 큼을 뜻한다.\n관련성 +0.080은 적용−미적용 평균 대응 점수 차이다.\n한국어 비율 0.700은 70.0%, 차이 +0.218은 +21.8%p다.',L,2230,C,90,18);
  text('평가 예시  ext_raptor_011, H0C0S0',L,2326,C,30,18,true);
  text('질문: Cinderella 사례의 정성 분석에서 RAPTOR의\ntree-based retrieval이 DPR보다 주제형·멀티홉\n질문에 유리했던 이유는 무엇입니까?',L,2360,C,90,18);
  text('근거 발췌: “RAPTOR selects nodes from different layers”\n답변 발췌: “질문의 요구사항에 따라 서로 다른\n층위(layer)에서 노드를 선택할 수 있습니다.”',L,2460,C,90,18);
  text('충실도 1.000: 평가자가 추출한 주장을 검색 문맥이 지지\n관련성 0.937: 답변 기반 질문과 원질문의 평균 의미 유사도',L,2560,C,60,18);
  text('평가: RAGAS 0.2.15[10], gpt-4o, BGE-M3 임베딩\nS0: 영어 문맥 / S1: 한국어 번역 평가 문맥\n생성에는 영어 문맥 사용, 저장 답변은 그대로 평가',L,2630,C,90,18);
  text('3요인 반복측정 분산분석(ANOVA)·대응 t-검정, Holm·α=0.05\n질의 60개, 품질 S별 H×C / 문자 비율·시간 H×C×S\nSCD 120·240쌍은 질의별 평균 차이 60개로 검정',L,2730,C,90,18,true);
  heading('05 조합별 결과와 통계 검정',R,365,C);
  text('HyDE·CAD·SCD 8조합의 품질·한국어 비율·시간 평균(SD)',R,430,C,36,18,true);
  const mets=['faithfulness','answer_relevancy','context_precision','context_recall','korean_ratio','duration_seconds'];
  const meanrows=[['조건','근거\n충실도','답변\n관련성','문맥\n정밀도','문맥\n재현율','한국어\n비율','실행\n시간'],...conditions.toSorted((a,b)=>a[5].localeCompare(b[5])||a.localeCompare(b)).map(z=>[z,...mets.map(m=>{const a=stats.descriptives[z][m];return f(a.mean)+'\n('+f(a.sd)+')';})])];
  table(meanrows,R,484,C,72,[.16,.14,.14,.14,.14,.14,.14],['code','number','number','number','number','number','number']);
  rect(R,484+72*5-1.5,C,3,purple); // Editable separator between S0 and S1 groups.
  text('S0: 영어 평가 문맥 / S1: 한국어 번역 평가 문맥\n충실도 H0C1S0 n=58, H0C0S1 n=57, 나머지 n=60\n한국어 비율·시간(초)은 생성 기록에서 직접 계산',R,1151,C,96,18);
  text('3요인 반복측정 ANOVA  ·  각 효과 df=(1,59)',R,1272,C,34,18,true);
  const effects=['H','D','S','H:D','H:S','D:S','H:D:S'];
  const ar=[['요인','한국어 비율\nF','보정 p','실행 시간\nF','보정 p'],...effects.map(e=>{const l=stats.anova.find(z=>z.metric==='korean_ratio'&&z.effect===e),t=stats.anova.find(z=>z.metric==='duration_seconds'&&z.effect===e);return[e.replaceAll('D','C').replaceAll(':','×'),f(l.F),p(l.p_holm),f(t.F),p(t.p_holm)];})];
  table(ar,R,1323,C,51,[.19,.22,.18,.22,.19],['code','number','number','number','number']);
  text('문자 비율·시간은 각각 7검정에 Holm 보정.\nRAGAS H×C 검정은 평가 문맥 언어별로 수행했으며,\n전체 24검정의 Holm 보정 p는 모두 0.05 이상이었다.',R,1760,C,96,18);
  text('기법별 대응 비교  ·  질의별 평균 차이, 양측 검정',R,1870,C,36,18,true);
  const selected=[stats.paired.find(z=>z.factor==='HyDE'&&z.metric==='answer_relevancy'),stats.paired.find(z=>z.factor==='CAD'&&z.metric==='faithfulness'),stats.paired.find(z=>z.factor==='SCD_H0_same_context')];
  table([['비교','차이\n(SD)','t(df)','보정 전\np','보정 후\np'],...selected.map((z,i)=>[['HyDE\n답변 관련성','CAD\n근거 충실도','SCD H0\n한국어 비율'][i],f(z.mean)+'\n('+f(z.sd)+')',f(z.t)+'\n('+z.df+')',p(z.p),p(z.p_holm)])],R,1923,C,84,[.25,.23,.2,.16,.16],['description','number','number','number','number']);
  text('HyDE: C0S0, CAD: H0S0, SCD: H0의 CAD 상태 평균\n보정: HyDE·CAD 각 4지표, SCD 주·전체 비교 2검정\nSCD 차이 +0.218은 한글 비중 +21.8%p에 해당',R,2276,C,95,18);
  heading('06 결과 해석',R,2395,C);
  text('HyDE의 양의 관련성 차이는 다중비교 보정 결과와 함께 해석한다.\nCAD는 질의별 충실도 변동과 추가 실행 시간을 함께 비교한다.\nSCD의 효과는 생성 답변에서 한글이 차지하는 비중의 증가다.\n시간의 C×S 상호작용은 SCD별 CAD 시간 증가가 다름을 뜻한다.',R,2450,C,128,18);
  heading('07 결론',R,2592,C);
  text('답변 품질은 평균 대응 차이와 보정 검정 결과로 판단한다.\n한국어 사용 비중을 높이는 목적에는 SCD 결과를 참고한다.\nCAD 적용은 질의별 충실도와 추가 실행 시간을 함께 검토한다.\nHyDE 적용은 번역·가상 문서 생성과 검색 결과를 함께 비교한다.\n최종 조합은 목표 언어·품질·허용 시간을 기준으로 선택한다.',R,2655,C,160,18);
  heading('08 주요 참고문헌',L,2840,W-2*L);
  text('[1] Lewis et al. RAG. NeurIPS, 2020.\n[2] Gao et al. HyDE. ACL, 2023.\n[3] Shi et al. Context-Aware Decoding. NAACL, 2024.',L,2904,C,99,16);
  text('[4] Li et al. Language Drift and SCD. AAAI, 2026.\n[5] Chen et al. M3-Embedding. ACL Findings, 2024.\n[10] Es et al. RAGAs. EACL Demonstrations, 2024.',R,2904,C,99,16);
  text('전체 22편과 통계 상세표·결측·민감도 분석은 동봉 자료에 수록',L,3035,W-2*L,32,16);
  text('영어 문서 4종 · 질의 60개 · 생성 모델 1종 · 질의별 반복측정',L,3090,W-2*L,30,14,false,purple);
  text('A1 594 × 841 mm',L,3138,W-2*L,24,10.5,false,purple,'right');
  sl.speakerNotes.text='Research sources and full statistics: FINALDOCS/DATA/FACTORIAL_STATISTICS_60Q.json; FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md. The exploratory analysis uses query-level repeated measures and Holm-adjusted hypothesis families. Editable tables follow explicit data-type alignment. Reference [4] https://arxiv.org/abs/2511.09984; references follow manuscript numbering.';
  await (await PresentationFile.exportPptx(pres)).save(out+'/candidate.pptx');
  await fs.writeFile(out+'/M_RAG_A1_FINAL_EDITABLE.svg',`<svg xmlns="http://www.w3.org/2000/svg" width="594mm" height="841mm" viewBox="0 0 ${W} ${H}"><rect width="${W}" height="${H}" fill="white"/>${svg.join('')}</svg>`);
  await fs.writeFile(out+'/scene_text.json',JSON.stringify(texts,null,2));
  await fs.writeFile(out+'/scene_geometry.json',JSON.stringify(geometry,null,2));
  await fs.writeFile(out+'/native_render.png',new Uint8Array(await (await sl.export({format:'png',scale:.7})).arrayBuffer()));
  await fs.writeFile(out+'/native_layout.json',new Uint8Array(await (await sl.export({format:'layout'})).arrayBuffer()));
  console.log('created native editable A1',out);
}
