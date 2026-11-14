import { cpSync, mkdirSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const source = path.join(root, 'observed/dist');
const publication = JSON.parse(readFileSync(path.join(source, 'data/publication/index.json'), 'utf8'));
if (publication.product !== 'observed-platform-history' || publication.communes.length !== 54) {
  throw new Error('Run python3 pipeline/publish_observed.py before building.');
}
mkdirSync(path.join(root, 'web/public/observed'), { recursive: true });
cpSync(source, path.join(root, 'web/public/observed'), { recursive: true });
console.log('FireChronos: published observed history, provenance and original explorer.');
