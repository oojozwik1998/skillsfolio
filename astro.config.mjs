// @ts-check
import process from 'node:process';
import keystatic from '@keystatic/astro';
import react from '@astrojs/react';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'astro/config';

// The panel has server routes, so it runs in local development only. The public build stays static.
const isDev = process.argv.includes('dev');

export default defineConfig({
  integrations: isDev ? [react(), keystatic()] : [],
  vite: {
    plugins: [tailwindcss()],
  },
});
