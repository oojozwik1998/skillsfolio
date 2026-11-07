import process from 'node:process';
import { defineConfig, devices } from '@playwright/test';

const isCI = Boolean(process.env.CI);
// E2E_PORT lets the tests run next to a dev server that already uses 4321.
const port = process.env.E2E_PORT ?? '4321';
const baseURL = `http://localhost:${port}`;

export default defineConfig({
  testDir: 'tests/e2e',
  forbidOnly: isCI,
  retries: isCI ? 1 : 0,
  reporter: isCI ? [['github'], ['html', { open: 'never' }]] : 'list',
  use: {
    baseURL,
    ...devices['Desktop Chrome'],
  },
  webServer: {
    // --ignore-lock keeps the server in the foreground. Astro moves it to the background when an AI agent runs it.
    command: `pnpm preview --host localhost --port ${port} --ignore-lock`,
    url: baseURL,
    reuseExistingServer: !isCI,
  },
});
