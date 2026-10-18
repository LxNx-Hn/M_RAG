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
const stats=JSON.parse(await fs.readFile(root+'/FINALDOCS/DATA/TTEST_ANOVA_60Q.json','utf8'));
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
  text('HyDE: 가상 문서 임베딩(Hypothetical Document Embeddings)\n가상 문서 검색 입력 구성[2]\nCAD: 문맥 인식 디코딩(Context-Aware Decoding)\n검색 근거의 영향 조정[3]\nSCD: 소프트 제약 디코딩(Soft Constrained Decoding)\n출력 언어 제어[4]',L,494,C,180,18);
  text('한국어 질의–영어 문서 RAG는 검색 어휘 차이, 근거 반영,\n영어 출력(언어 이탈)의 문제를 함께 겪는다. 세 기법의\n단독 효과와 조합 효과를 같은 파이프라인에서 비교하였다.',L,678,C,90,18,true);
  heading('02 Paper-RAG 구조와 기법 적용 위치',L,773,C);
  text('Paper-RAG는 실험에 사용한 고정 검색·생성 파이프라인이다.',L,837,C,36,18);
  const b=(C-44)/2;
  box('한국어 질의\nHyDE OFF: 원질의\nHyDE ON: 영어 번역·가상 문서',L,894,b,118,blue);
  box('BM25 희소 검색[6]\n한국어 원질의 사용',L+b+44,894,b,118);
  box('BGE-M3 밀집 검색[5]',L,1046,b,64,blue);
  box('가중 RRF[7]\n0.6 / 0.4, k=60',L+b+44,1046,b,78);
  arrow(L+b/2-9,1018,18,22,90);arrow(L+b+8,1062,28,20);
  arrow(L+b+44+b/2-9,1018,18,22,90);
  box('원질의·구간 쌍 CrossEncoder 재정렬[8][M2]\n상위 5개 구간 선택·입력 길이 관리',L,1156,C,84);
  box('Mi:dm 2.0 Base Instruct[M1]\nCAD 로짓 결합 후 SCD 언어별 조정, 최종 답변 생성',L,1274,C,83,green);
  arrow(L+C/2-9,1131,18,18,90);arrow(L+C/2-9,1248,18,18,90);
  heading('03 3요인 완전요인 실험 설계',L,1390,C);
  text('H=HyDE, C=CAD, S=SCD   0=미적용, 1=적용',L,1450,C,36,18);
  const conditions=Object.keys(stats.descriptives);
  table([['조건','H','C','S'],...conditions.map(z=>[z,z[1],z[3],z[5]])],L,1497,C,36,[.46,.18,.18,.18],['code','code','code','code']);
  text('같은 질의 60개 × 8조건 반복측정 = 480개 생성 기록',L,1840,C,34,18,true);
  text('생성 512토큰, CAD α=0.5, SCD α=1.1·β=0.9·Tstart=5',L,1884,C,34,18);
  text('문서마다 주요 내용을 15개 단위로 요약해 단위별 질의를 작성하고,\n총 60개 질의의 원문 페이지·정답 근거·답변 가능성을 확인',L,1930,C,62,18);
  heading('04 평가 지표 및 실험·통계 방법',L,2010,C);
  text('근거 충실도: 높을수록 검색 결과가 뒷받침하는 답변 주장 비율이 크다.\n답변 관련성: 높을수록 답변 기반 질문과 원질문의 의미가 가깝다.\n문맥 정밀도: 높을수록 참조 답변에 유용한 구간이 상위에 놓인다.\n문맥 재현율: 높을수록 검색 근거가 포괄하는 참조 답변 비중이 크다.\n한국어 비율: 한글 / (한글 + ASCII 영문자), 높을수록 한글 비중이 크다.',L,2070,C,150,18);
  text('품질 관측값은 0~1이다. 차이는 ON−OFF 평균 차이다.\n한국어 비율 0.700은 70.0%, 차이 +0.218은 +21.8%p다.',L,2225,C,90,18);
  text('평가 예시  ext_raptor_011, H0C0S0',L,2320,C,30,18,true);
  text('질문: Cinderella 사례의 정성 분석에서 RAPTOR의 tree-based\nretrieval이 DPR보다 주제형·멀티홉 질문에 유리했던 이유는 무엇입니까?',L,2352,C,60,18);
  text('검색 근거(PDF p.9): “By providing both the original text and higher-level summaries\nfor retrieval, RAPTOR can effectively handle a wider range of\nquestions, from higher-order thematic queries to detail-oriented questions.”',L,2414,C,90,18);
  text('참조 답변 요지(PDF p.20): RAPTOR는 이야기의 주요 부분을,\nDPR은 이야기의 좁은 일부를 자세히 검색한다.',L,2507,C,60,18);
  text('생성 답변 발췌: “질문의 요구사항에 따라 서로 다른\n층위(layer)에서 노드를 선택할 수 있습니다.”',L,2569,C,60,18);
  text('충실도 1.000: 추출된 답변 주장을 검색 결과가 모두 지지\n관련성 0.937: 답변 기반 질문과 원질문의 평균 의미 유사도',L,2632,C,60,18);
  text('평가: RAGAS 0.2.15[10]·gpt-4o·BGE-M3, 저장 답변 평가\n평가 언어: S0 영어 / S1 한국어 번역, 생성 입력은 모두 영어',L,2695,C,60,18);
  text('반복측정 분산분석(ANOVA)·대응 t-검정, 양측 α=0.05\n품질: SCD 상태별 H×C / 한국어 비율·시간: H×C×S, SCD 대응쌍은 질의별 평균(n=60)',L,2760,C,60,18,true);
  heading('05 조합별 결과와 통계 검정',R,365,C);
  text('HyDE·CAD·SCD 8조합의 품질·한국어 비율·시간 평균(SD)',R,430,C,36,18,true);
  const mets=['faithfulness','answer_relevancy','context_precision','context_recall','korean_ratio','duration_seconds'];
  const meanrows=[['조건','근거\n충실도','답변\n관련성','문맥\n정밀도','문맥\n재현율','한국어\n비율','실행\n시간'],...conditions.toSorted((a,b)=>a[5].localeCompare(b[5])||a.localeCompare(b)).map(z=>[z,...mets.map(m=>{const a=stats.descriptives[z][m];return f(a.mean)+'\n('+f(a.sd)+')';})])];
  table(meanrows,R,484,C,72,[.16,.14,.14,.14,.14,.14,.14],['code','number','number','number','number','number','number']);
  rect(R,484+72*5-1.5,C,3,purple); // Editable separator between S0 and S1 groups.
  text('S0: 영어로 평가 / S1: 한국어 번역으로 평가\n충실도 H0C1S0 n=58, H0C0S1 n=57, 나머지 n=60\n한국어 비율·시간(초)은 답변과 실행 시간에서 직접 계산',R,1151,C,96,18);
  text('3요인 반복측정 ANOVA  ·  각 효과 df=(1,59)',R,1272,C,34,18,true);
  const effects=['H','C','S','H×C','H×S','C×S','H×C×S'];
  const ar=[['요인','한국어 비율\nF','p','실행 시간\nF','p'],...effects.map(e=>{const l=stats.rm_anova.korean_ratio.find(z=>z.effect===e),t=stats.rm_anova.duration_seconds.find(z=>z.effect===e);return[e,f(l.F),p(l.p),f(t.F),p(t.p)];})];
  table(ar,R,1323,C,51,[.19,.22,.18,.22,.19],['code','number','number','number','number']);
  text('p<0.05: 한국어 비율 S·H×C* / 실행 시간 H·C·S*·C×S (*유의수준 근처의 탐색적 결과)\nRAGAS H×C 검정은 평가 언어별로 수행했으며,\n품질 4지표 24검정의 p는 모두 0.05 이상이었다.',R,1760,C,96,18);
  text('기법별 대응 비교  ·  질의별 평균 차이, 양측 검정',R,1870,C,36,18,true);
  const selected=['RQ1_HyDE_answer_relevancy','RQ2_CAD_faithfulness','RQ3_SCD_korean_ratio_H0'].map(k=>stats.primary_paired_t[k]);
  table([['비교','차이\n(SD)','t(df)','p','dz'],...selected.map((z,i)=>[['HyDE\n답변 관련성','CAD\n근거 충실도','SCD H0\n한국어 비율'][i],f(z.mean_diff)+'\n('+f(z.sd_diff)+')',f(z.t)+'\n('+z.df+')',p(z.p),f(z.dz)])],R,1923,C,84,[.25,.23,.2,.16,.16],['description','number','number','number','number']);
  text('HyDE: C0S0, CAD: H0S0, SCD: H0의 CAD 상태 평균\np: 다중비교 보정 없는 양측 p, dz: 차이 평균/차이 SD\n평균표 SD는 점수의 산포, 대응표 SD는 ON−OFF 차이의 산포',R,2264,C,90,18);
  heading('06 결과 해석',R,2365,C);
  text('HyDE: 기본 조건에서 관련성이 유의하게 높았고(p=0.029),\nSCD 적용 조건의 추가 비교에서는 p=0.114였다.\nCAD: 충실도 차이는 작았고(p=0.393), 실행 시간은 약 2.9배였다.\nSCD: 네 조합 모두에서 한국어 문자 비율이 높았고, CAD와 함께\n쓰면 CAD의 추가 시간이 약 9초 줄었다(C×S, p<0.001).',R,2420,C,150,18);
  heading('07 결론',R,2582,C);
  text('한국어 답변이 필요하면 SCD가 비용이 작은 선택이었다.\nHyDE의 관련성 향상은 기본 조건(C0S0)에서 관측되었고,\n이 차이에는 질의 번역과 가상 문서 생성이 함께 포함되었다.\nCAD는 충실도 차이가 작고 실행 시간이 약 2.9배로 늘었다\n(SCD 미적용 3.1배, 적용 2.7배).\n후속 실험: 번역 단독 조건, 반복 생성·평가, 한국어 사람 평가.',R,2645,C,182,18);
  heading('08 주요 참고문헌',L,2840,W-2*L);
  text('[1] Lewis et al. RAG. NeurIPS, 2020.\n[2] Gao et al. HyDE. ACL, 2023.\n[3] Shi et al. Context-Aware Decoding. NAACL, 2024.',L,2904,C,99,16);
  text('[4] Li et al. Language Drift and SCD. AAAI, 2026.\n[5] Chen et al. M3-Embedding. ACL Findings, 2024.\n[10] Es et al. RAGAs. EACL Demonstrations, 2024.',R,2904,C,99,16);
  text('[6] Robertson et al. Okapi at TREC-3. NIST, 1995.\n[7] Cormack et al. Reciprocal Rank Fusion. SIGIR, 2009.',L,3010,C,60,16);
  text('[8] MacAvaney et al. CEDR. SIGIR, 2019.\n공식 모델  [M1] KT Mi:dm 2.0 / [M2] MiniLM CrossEncoder',R,3010,C,60,16);
  text('전체 참고문헌 22편과 모델·자료 출처는 논문의 참고문헌에 수록',L,3082,W-2*L,30,16);
  text('영어 문서 4종 · 질의 60개 · 생성 모델 1종 · 질의별 반복측정',L,3115,W-2*L,26,14,false,purple);
  text('A1 594 × 841 mm',L,3138,W-2*L,24,10.5,false,purple,'right');
  sl.speakerNotes.text='Research sources and full statistics: FINALDOCS/DATA/TTEST_ANOVA_60Q.json; FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md. The exploratory analysis uses query-level paired t-tests and repeated-measures ANOVA with two-sided alpha 0.05 and no multiplicity adjustment. Editable tables follow explicit data-type alignment. Reference [4] https://ojs.aaai.org/index.php/AAAI/article/view/40417; [8] https://doi.org/10.1145/3331184.3331317 is conceptual ranking background, not the implemented CEDR architecture. [M1] https://huggingface.co/K-intelligence/Midm-2.0-Base-Instruct; [M2] https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2. The English case evidence is a contiguous saved context excerpt (PDF p.9), reference evidence is on PDF p.20. References follow manuscript numbering.';
  await (await PresentationFile.exportPptx(pres)).save(out+'/candidate.pptx');
  await fs.writeFile(out+'/M_RAG_A1_FINAL_EDITABLE.svg',`<svg xmlns="http://www.w3.org/2000/svg" width="594mm" height="841mm" viewBox="0 0 ${W} ${H}"><rect width="${W}" height="${H}" fill="white"/>${svg.join('')}</svg>`);
  await fs.writeFile(out+'/scene_text.json',JSON.stringify(texts,null,2));
  await fs.writeFile(out+'/scene_geometry.json',JSON.stringify(geometry,null,2));
  await fs.writeFile(out+'/native_render.png',new Uint8Array(await (await sl.export({format:'png',scale:.7})).arrayBuffer()));
  await fs.writeFile(out+'/native_layout.json',new Uint8Array(await (await sl.export({format:'layout'})).arrayBuffer()));
  console.log('created native editable A1',out);
}
