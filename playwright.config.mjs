import {defineConfig,devices} from '@playwright/test';
export default defineConfig({
  testDir:'./tests/e2e',
  fullyParallel:false,
  timeout:180_000,
  expect:{timeout:120_000},
  retries:1,
  reporter:'list',
  use:{...devices['Desktop Chrome'],baseURL:'http://127.0.0.1:8787',trace:'retain-on-failure'},
  webServer:{command:'python3 -m http.server 8787 --bind 127.0.0.1 --directory dist',
    url:'http://127.0.0.1:8787',reuseExistingServer:!process.env.CI,timeout:30_000}
});
