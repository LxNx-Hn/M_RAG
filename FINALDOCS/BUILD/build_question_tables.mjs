import fs from 'node:fs/promises';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../../',import.meta.url));
const tables=JSON.parse(await fs.readFile(root+'/FINALDOCS/DATA/THESIS_TABLES_60Q.json','utf8'));
const wb=Workbook.create();
for(const t of tables){
 const sh=wb.worksheets.add(t.sheet);sh.showGridLines=false;
 sh.getCell(0,0).values=[[t.title]];sh.getCell(1,0).values=[['Source: stored 60-query observations; question-aligned valid pairs; no imputation']];
 const n=t.rows.length,c=t.rows[0].length,rg=sh.getRangeByIndexes(2,0,n,c);rg.values=t.rows;
 rg.format.font={name:'Malgun Gothic',size:10,bold:false};rg.format.fill='#FFFFFF';
 rg.format.wrapText=true;rg.format.verticalAlignment='center';rg.format.columnWidth=20;rg.format.rowHeight=36;
 rg.format.borders={preset:'all',style:'thin',color:'#777777'};
 sh.getRangeByIndexes(2,0,1,c).format.font={name:'Malgun Gothic',size:10,bold:true};
 for(let j=0;j<c;j++){
  const h=t.rows[0][j];const al=t.numeric_columns?(t.numeric_columns.includes(j)?'right':'left'):['질문 수','기준 점수','적용 점수','기준 시간','적용 시간','평균 변화량','개선/악화/비슷','증가/감소/비슷','원문 페이지'].includes(h)?'right':h==='비교 조건'?'center':'left';
  sh.getRangeByIndexes(3,j,n-1,1).format.horizontalAlignment=al;
 }
 for(const [r,c] of t.bold_cells??[])sh.getCell(r+2,c).format.font={name:'Malgun Gothic',size:10,bold:true};
 if(t.sheet==='Appendix_Queries'){sh.getRange('B:B').format.columnWidth=60;sh.getRange('F:F').format.columnWidth=85;rg.format.rowHeight=100;}
 if(t.sheet==='Appendix_Features'){sh.getRange('E:E').format.columnWidth=66;rg.format.rowHeight=60;}
 sh.freezePanes.freezeRows(3);
}
await wb.recalculate();
await(await SpreadsheetFile.exportXlsx(wb)).save(root+'/FINALDOCS/TABLES/TABLES_60Q.xlsx');
await fs.mkdir(root+'/tmp/query-revision/tables',{recursive:true});
await fs.writeFile(root+'/tmp/query-revision/tables/relevance.png',new Uint8Array(await(await wb.render({sheetName:'T5-1_HyDE_Relevance',range:'A3:H11',scale:1.5})).arrayBuffer()));
console.log('PASS: '+tables.length+' native sheets; white cells, maximum bold, question-centred results');
