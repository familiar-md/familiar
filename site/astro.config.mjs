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
      description: 'A project-memory and workflow layer that makes AI agents instantly familiar with your work, progress, and decisions.',
      social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/familiar-md/familiar' }],
      logo: { light: './src/assets/logo-light.svg', dark: './src/assets/logo-dark.svg', alt: 'familiar', replacesTitle: true },
      // The default favicon is the charcoal tile; dark browser tab bars get the cream tile.
      head: [{ tag: 'link', attrs: { rel: 'icon', type: 'image/svg+xml', href: '/familiar/favicon-light.svg', media: '(prefers-color-scheme: dark)' } }],
      customCss: ['./src/styles/familiar.css'],
      sidebar,
    }),
  ],
});
