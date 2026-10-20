import fs from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import sharp from 'sharp';
const root=fileURLToPath(new URL('../../',import.meta.url));
await sharp(root+'/tmp/query-revision/poster/poster.svg',{density:75}).png().toFile(root+'/tmp/query-revision/poster/vector.png');
console.log('PASS: canonical poster vector preview');
