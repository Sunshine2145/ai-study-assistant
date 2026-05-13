const { test, expect } = require('@playwright/test');

const BASE_URL = 'http://127.0.0.1:5500';
const HEALTH_URL = 'http://127.0.0.1:5001/health';

test.beforeAll(async () => {
  // Ensure backend health endpoint is available before browser checks.
  const response = await fetch(HEALTH_URL);
  if (!response.ok) throw new Error(`Backend health check failed: ${response.status}`);
});

test('frontend loads and main pages do not return 404 for API calls', async ({ page }) => {
  const pageErrors = [];
  const networkFailures = [];
  const badApiResponses = [];

  page.on('console', msg => {
    if (msg.type() === 'error') pageErrors.push(msg.text());
  });

  page.on('requestfailed', request => {
    networkFailures.push(`${request.url()} - ${request.failure()?.errorText}`);
  });

  page.on('response', response => {
    const url = response.url();
    if (url.startsWith('http://127.0.0.1:5001')) {
      if (!response.ok()) {
        badApiResponses.push(`${response.status()} ${response.statusText()} ${url}`);
      }
    }
  });

  await page.goto(`${BASE_URL}/index.html`, { waitUntil: 'networkidle' });
  await expect(page.locator('#pageTitle')).toHaveText(/学习首页/);

  const navPages = ['learn', 'practice', 'wrong', 'report', 'upload', 'question-bank', 'ai-qa', 'map'];
  for (const pageId of navPages) {
    await page.click(`.nav-item[data-page="${pageId}"]`);
    await expect(page.locator(`#page-${pageId}`)).toBeVisible();
    await page.waitForTimeout(500);
  }

  expect(pageErrors).toEqual([]);
  expect(networkFailures).toEqual([]);
  expect(badApiResponses).toEqual([]);
});
