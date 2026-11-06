import process from 'node:process';
import { defineConfig, devices } from '@playwright/test';

const isCI = Boolean(process.env.CI);

export default defineConfig({
  testDir: 'tests/e2e',
  forbidOnly: isCI,
  retries: isCI ? 1 : 0,
  reporter: isCI ? [['github'], ['html', { open: 'never' }]] : 'list',
  use: {
    baseURL: 'http://localhost:4321',
    ...devices['Desktop Chrome'],
  },
  webServer: {
    // --ignore-lock keeps the server in the foreground. Astro moves it to the background when an AI agent runs it.
    command: 'pnpm preview --host localhost --port 4321 --ignore-lock',
    url: 'http://localhost:4321',
    reuseExistingServer: !isCI,
  },
});
