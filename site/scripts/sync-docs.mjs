// Generates the site's pages from the repo's own Markdown, so the site and the GitHub docs never
// disagree: README.md (Getting started, Using familiar), INSTALL.md (Install and update) and
// MANUAL.md (Manual). Each `## ` section becomes one page; its `###` headings move up one level.
// Links between the documents are rewritten to the pages they land on; links to other repo files
// go to GitHub. Run by `npm run build` and `npm run dev`; never edit the generated pages.
import { readFileSync, writeFileSync, mkdirSync, rmSync, cpSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const SITE = join(dirname(fileURLToPath(import.meta.url)), '..');
const ROOT = join(SITE, '..');
const DOCS = join(SITE, 'src', 'content', 'docs');
const BASE = '/familiar';
const REPO = 'https://github.com/familiar-md/familiar/blob/main/';

// Which README sections go where, in reading order. A README section not listed is left off the site
// (Versioning and License live in the footer and on GitHub).
const README_GROUPS = {
  start: ['Download', 'Works with', 'Your first session'],
  use: ['The everyday loop', 'The skills', 'Where things live', 'One folder per project',
        'What familiar will not do', 'Working with synced folders', 'Troubleshooting', 'Going further'],
};

function slugify(text) {
  // The same rule GitHub and Starlight use for heading ids (github-slugger).
  return text.toLowerCase().trim().replace(/[^\p{L}\p{N}\- _]/gu, '').replace(/ /g, '-');
}

function plainTitle(heading) {
  return heading.replace(/`/g, '').replace(/\*\*/g, '').trim();
}

// Split a document into its preamble and its `## ` sections, ignoring headings inside code fences.
function split(text) {
  const lines = text.replace(/\r\n/g, '\n').split('\n');
  const sections = [];
  let preamble = [];
  let current = null;
  let fence = false;
  for (const line of lines) {
    if (/^(```|~~~)/.test(line)) fence = !fence;
    const m = !fence && /^## (.+)$/.exec(line);
    if (m) {
      current = { title: m[1].trim(), lines: [] };
      sections.push(current);
    } else if (current) {
      current.lines.push(line);
    } else {
      preamble.push(line);
    }
  }
  return { preamble: preamble.join('\n'), sections };
}

function demote(body) {
  let fence = false;
  return body.split('\n').map((line) => {
    if (/^(```|~~~)/.test(line)) fence = !fence;
    return !fence && /^#{3,6} /.test(line) ? line.slice(1) : line;
  }).join('\n');
}

// pages: [{doc, group, slug, title, body}]; anchors: doc -> {headingSlug: url}
const pages = [];
const anchors = { 'README.md': {}, 'INSTALL.md': {}, 'MANUAL.md': {} };

function addPage(doc, group, title, body) {
  const slug = slugify(plainTitle(title)).replace(/^-+|-+$/g, '') || 'overview';
  const url = `${BASE}/${group}/${slug}/`;
  pages.push({ doc, group, slug, title: plainTitle(title), body: body.trim() + '\n', url });
  anchors[doc][slugify(plainTitle(title))] = url;
  for (const m of body.matchAll(/^#{3,6} (.+)$/gm)) anchors[doc][slugify(plainTitle(m[1]))] = url + '#' + slugify(plainTitle(m[1]));
  return url;
}

const read = (name) => readFileSync(join(ROOT, name), 'utf8');

// README
const readme = split(read('README.md'));
for (const [group, titles] of Object.entries(README_GROUPS)) {
  for (const title of titles) {
    const section = readme.sections.find((s) => s.title === title);
    if (!section) throw new Error(`README.md has no "## ${title}" section; update README_GROUPS in sync-docs.mjs`);
    addPage('README.md', group, title, demote(section.lines.join('\n')));
  }
}
anchors['README.md'][''] = `${BASE}/start/download/`;

// INSTALL: the opening paragraph leads the first page.
const install = split(read('INSTALL.md'));
install.sections.forEach((s, i) => {
  const lead = i === 0 ? install.preamble.replace(/^# .+$/m, '').trim() + '\n\n' : '';
  addPage('INSTALL.md', 'install', s.title, lead + demote(s.lines.join('\n')));
});
anchors['INSTALL.md'][''] = pages.find((p) => p.doc === 'INSTALL.md').url;

// MANUAL: the preamble becomes the manual's first page.
const manual = split(read('MANUAL.md'));
addPage('MANUAL.md', 'manual', 'About this manual', manual.preamble.replace(/^# .+$/m, ''));
for (const s of manual.sections) addPage('MANUAL.md', 'manual', s.title, demote(s.lines.join('\n')));
anchors['MANUAL.md'][''] = `${BASE}/manual/about-this-manual/`;

function mapTarget(doc, target) {
  if (/^(https?:|mailto:|\/)/.test(target)) return target;
  const [path, hash = ''] = target.split('#');
  const file = path === '' ? doc : path.replace(/^\.\//, '');
  if (anchors[file]) return anchors[file][hash] ?? anchors[file][''];
  if (file === 'CHEATSHEET.md') return `${BASE}/cheatsheet/`;
  if (file.startsWith('docs/assets/')) return `${BASE}/assets/${file.slice('docs/assets/'.length)}`;
  return `${REPO}${file}${hash ? '#' + hash : ''}`;
}

function rewrite(doc, body) {
  return body
    .replace(/\]\(([^)\s]+)\)/g, (_, target) => `](${mapTarget(doc, target)})`)
    .replace(/\b(src|href)="([^"]+)"/g, (_, attr, target) => `${attr}="${mapTarget(doc, target)}"`);
}

// Write the pages.
for (const group of ['start', 'use', 'install', 'manual']) rmSync(join(DOCS, group), { recursive: true, force: true });
for (const p of pages) {
  const dir = join(DOCS, p.group);
  mkdirSync(dir, { recursive: true });
  const front = `---\ntitle: ${JSON.stringify(p.title)}\neditUrl: false\n---\n\n`;
  const note = `<!-- Generated from ${p.doc} by site/scripts/sync-docs.mjs. Edit ${p.doc}, not this file. -->\n\n`;
  writeFileSync(join(dir, `${p.slug}.md`), front + note + rewrite(p.doc, p.body));
}

// Static files the pages link to.
rmSync(join(SITE, 'public', 'assets'), { recursive: true, force: true });
cpSync(join(ROOT, 'docs', 'assets'), join(SITE, 'public', 'assets'), { recursive: true });
rmSync(join(SITE, 'public', 'cheatsheet'), { recursive: true, force: true });
if (existsSync(join(ROOT, 'docs', 'cheatsheet.html'))) {
  mkdirSync(join(SITE, 'public', 'cheatsheet'), { recursive: true });
  cpSync(join(ROOT, 'docs', 'cheatsheet.html'), join(SITE, 'public', 'cheatsheet', 'index.html'));
}

// The sidebar, in document order.
const group = (label, key, collapsed = false) => ({
  label, collapsed,
  items: pages.filter((p) => p.group === key).map((p) => ({ label: p.title, slug: `${p.group}/${p.slug}` })),
});
const sidebar = [
  group('Getting started', 'start'),
  group('Using familiar', 'use'),
  { label: 'Cheat sheet', link: '/cheatsheet/' },
  group('Install and update', 'install', true),
  group('Manual', 'manual', true),
  {
    label: 'Add-ons',
    items: [
      { label: 'familiar-hub', link: 'https://github.com/familiar-md/familiar-hub' },
      { label: 'familiar-hooks', link: 'https://github.com/familiar-md/familiar-hooks' },
      { label: 'familiar-template', link: 'https://github.com/familiar-md/familiar-template' },
    ],
  },
];
writeFileSync(join(SITE, 'src', 'sidebar.generated.json'), JSON.stringify(sidebar, null, 2) + '\n');
console.log(`sync-docs: ${pages.length} pages from README.md, INSTALL.md and MANUAL.md`);
