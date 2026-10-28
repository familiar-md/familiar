// The familiar docs site. Pages under start/, use/, install/ and manual/ are generated from the
// repo's README.md, INSTALL.md and MANUAL.md by scripts/sync-docs.mjs, so edit those files, not the
// generated pages. Served at https://familiar-md.github.io/familiar/ once the repo is public.
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import { readFileSync } from 'node:fs';

const sidebar = JSON.parse(readFileSync(new URL('./src/sidebar.generated.json', import.meta.url), 'utf8'));

export default defineConfig({
  site: 'https://familiar-md.github.io',
  base: '/familiar',
  integrations: [
    starlight({
      title: 'familiar',
      description: 'A project-memory and workflow layer for LLM agents, where nothing has to be explained twice.',
      social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/familiar-md/familiar' }],
      customCss: ['./src/styles/familiar.css'],
      head: [{ tag: 'link', attrs: { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&display=swap' } }],
      sidebar,
    }),
  ],
});
