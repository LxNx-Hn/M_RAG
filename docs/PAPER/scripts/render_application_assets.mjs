// Render source diagrams and capture the real saved-result audit HTML.
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';

const deps=process.env.ARTIFACT_RUNTIME_ROOT || path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies');
const require=createRequire(path.join(deps,'node/node_modules/package.json'));
const sharp=require('sharp');
const {chromium}=require('playwright');
const root=process.cwd();
const figures=path.join(root,'docs/PAPER/output/application_study/figures');
for(const name of await fs.readdir(figures)){
  if(name.endsWith('.svg'))await sharp(path.join(figures,name),{density:192}).png().toFile(path.join(figures,name.replace(/\.svg$/,'.png')));
}
const browser=await chromium.launch({channel:'msedge',headless:true});
try{
  const page=await browser.newPage({viewport:{width:1160,height:900},deviceScaleFactor:1.5});
  await page.goto(pathToFileURL(path.join(root,'tmp/application_review/evidence.html')).href);
  await page.evaluate(()=>document.fonts.ready);
  await page.screenshot({path:path.join(figures,'execution_evidence.png'),fullPage:true});
}finally{await browser.close();}
console.log('Rendered SVGs and captured the saved-result audit screen.');
