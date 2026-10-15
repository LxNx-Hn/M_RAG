import fs from 'node:fs/promises';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';
import { fileURLToPath } from 'node:url';
const root=fileURLToPath(new URL('../../',import.meta.url));
const data=JSON.parse(await fs.readFile(`${root}/FINALDOCS/DATA/THESIS_TABLES_60Q.json`,'utf8'));
const wb=Workbook.create();
for (const t of data) {
  const sh=wb.worksheets.add(t.sheet), n=t.rows.length, c=t.rows[0].length;
  sh.showGridLines=false;
  sh.getCell(0,0).values=[[t.title]];
  sh.getCell(1,0).values=[['Source: FINALDOCS/DATA/FACTORIAL_STATISTICS_60Q.json; query evidence preserved']];
  const range=sh.getRangeByIndexes(2,0,n,c);
  range.values=t.rows;
  range.format.font={name:'Malgun Gothic',size:10};
  range.format.wrapText=true;
  range.format.verticalAlignment='center';
  range.format.columnWidth=23;
  range.format.rowHeight=34;
  range.format.borders={preset:'all',style:'thin',color:'#D9D9D9'};
  sh.getRangeByIndexes(2,0,1,c).format.fill='#E8E2F4';
  sh.getRangeByIndexes(2,0,1,c).format.font={bold:true,name:'Malgun Gothic',size:10};
  sh.getRangeByIndexes(0,0,1,c).format.rowHeight=30;
  for(let col=0;col<c;col++) {
    const header=t.rows[0][col];
    const r=sh.getRangeByIndexes(3,col,n-1,1);
    r.format.horizontalAlignment= /^(n|유효 n|평균|SD|F|p|보정 p|부분|dz|t\(|충실도|관련성|정밀도|재현율|한국어 비율)/.test(header)?'right':(['조건','H','C','S','효과','df'].includes(header)?'center':'left');
  }
  if(t.sheet==='Appendix_Queries') {
    sh.getRange('B:B').format.columnWidth=64;
    sh.getRange('F:F').format.columnWidth=94;
    range.format.rowHeight=95;
  }
  sh.freezePanes.freezeRows(3);
}
await wb.recalculate();
await (await SpreadsheetFile.exportXlsx(wb)).save(`${root}/FINALDOCS/TABLES/TABLES_60Q.xlsx`);
console.log('exported',data.length,'native worksheets');
