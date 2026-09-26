// @ts-check
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './roles',
  timeout: 120000,
  expect: { timeout: 15000 },
  fullyParallel: false,
  workers: 1,
  reporter: [
    ['html', { outputFolder: '../playwright-report' }],
    ['list'],
  ],
  use: {
    baseURL: 'http://localhost:8069',
    screenshot: 'on',
    trace: 'on-first-retry',
    video: 'off',
    actionTimeout: 10000,
    navigationTimeout: 30000,
  },
});
