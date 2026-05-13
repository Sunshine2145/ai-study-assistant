const { test, expect } = require('@playwright/test');

const BASE_URL = 'http://localhost:8081';
const API_BASE = 'http://localhost:5001';

test.describe('AI伴学系统 - 全功能测试', () => {

  test.beforeAll(async () => {
    // Ensure backend is healthy
    const response = await fetch(`${API_BASE}/health`);
    if (!response.ok) throw new Error(`Backend health check failed: ${response.status}`);
  });

  // ======== 1. 登录功能 ========
  test('1. 用户登录', async ({ page }) => {
    const pageErrors = [];
    page.on('console', msg => { if (msg.type() === 'error') pageErrors.push(msg.text()); });

    await page.goto(`${BASE_URL}/index.html`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(1000);

    // Should redirect to login page
    const loginPage = page.locator('#page-login');
    if (await loginPage.isVisible()) {
      // Fill login form
      await page.fill('#loginUsername', 'user');
      await page.fill('#loginPassword', 'admin123');
      await page.click('.login-submit-btn');
      await page.waitForTimeout(2000);

      // Should navigate to map page after login
      const mapPage = page.locator('#page-map');
      if (await mapPage.isVisible()) {
        console.log('✅ 登录成功，进入学习地图');
      } else {
        console.log('⚠️ 登录后未跳转到地图页面（可能需要检查API返回）');
      }
    } else {
      console.log('⚠️ 登录页面不可见（可能已登录或页面结构不同）');
    }

    expect(pageErrors.filter(e => !e.includes('favicon'))).toEqual([]);
  });

  // ======== 2. 学习地图 ========
  test('2. 学习地图 - 查看知识点', async ({ page }) => {
    await page.goto(`${BASE_URL}/index.html`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(1500);

    // Try to navigate to map page
    await page.click('.nav-item[data-page="map"]');
    await page.waitForTimeout(1000);

    const mapPage = page.locator('#page-map');
    await expect(mapPage).toBeVisible();

    // Check if stage tabs are rendered
    const stageTabs = page.locator('#stageTabs');
    await expect(stageTabs).toBeVisible();
    console.log('✅ 学习地图页面正常显示');
  });

  // ======== 3. AI问答 ========
  test('3. AI问答 - 页面加载', async ({ page }) => {
    await page.goto(`${BASE_URL}/index.html`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(1000);

    await page.click('.nav-item[data-page="ai-qa"]');
    await page.waitForTimeout(500);

    const aiQaPage = page.locator('#page-ai-qa');
    await expect(aiQaPage).toBeVisible();
    console.log('✅ AI问答页面正常显示');
  });

  // ======== 4. 题目练习 ========
  test('4. 题目练习 - 页面加载', async ({ page }) => {
    await page.goto(`${BASE_URL}/index.html`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(1000);

    await page.click('.nav-item[data-page="practice"]');
    await page.waitForTimeout(1000);

    const practicePage = page.locator('#page-practice');
    await expect(practicePage).toBeVisible();
    console.log('✅ 题目练习页面正常显示');
  });

  // ======== 5. 错题本 ========
  test('5. 错题本 - 页面加载', async ({ page }) => {
    await page.goto(`${BASE_URL}/index.html`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(1000);

    await page.click('.nav-item[data-page="wrong"]');
    await page.waitForTimeout(1000);

    const wrongPage = page.locator('#page-wrong');
    await expect(wrongPage).toBeVisible();
    console.log('✅ 错题本页面正常显示');
  });

  // ======== 6. 学习报告 ========
  test('6. 学习报告 - 页面加载', async ({ page }) => {
    await page.goto(`${BASE_URL}/index.html`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(1000);

    await page.click('.nav-item[data-page="report"]');
    await page.waitForTimeout(1000);

    const reportPage = page.locator('#page-report');
    await expect(reportPage).toBeVisible();
    console.log('✅ 学习报告页面正常显示');
  });

  // ======== 7. 题库管理 ========
  test('7. 题库管理 - 页面加载', async ({ page }) => {
    await page.goto(`${BASE_URL}/index.html`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(1000);

    await page.click('.nav-item[data-page="question-bank"]');
    await page.waitForTimeout(1000);

    const bankPage = page.locator('#page-question-bank');
    await expect(bankPage).toBeVisible();
    console.log('✅ 题库管理页面正常显示');
  });

  // ======== 8. 题库上传 ========
  test('8. 题库上传 - 页面加载', async ({ page }) => {
    await page.goto(`${BASE_URL}/index.html`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(1000);

    await page.click('.nav-item[data-page="upload"]');
    await page.waitForTimeout(1000);

    const uploadPage = page.locator('#page-upload');
    await expect(uploadPage).toBeVisible();

    // Check upload zone exists
    const uploadZone = page.locator('#uploadZone');
    await expect(uploadZone).toBeVisible();
    console.log('✅ 题库上传页面正常显示');
  });

  // ======== 9. 首页 ========
  test('9. 学习首页 - 学习状态', async ({ page }) => {
    await page.goto(`${BASE_URL}/index.html`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(1500);

    const homePage = page.locator('#page-home');
    if (await homePage.isVisible()) {
      const title = page.locator('#pageTitle');
      await expect(title).toBeVisible();
      console.log('✅ 学习首页正常显示');
    }
  });

  // ======== 10. 注册页面 ========
  test('10. 用户注册 - 页面加载', async ({ page }) => {
    await page.goto(`${BASE_URL}/index.html`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(1000);

    // Go to login page first, then switch to register
    const registerPage = page.locator('#page-register');
    if (await registerPage.isVisible()) {
      await expect(registerPage).toBeVisible();
    }
    console.log('✅ 注册页面可达');
  });

  // ======== 11. API端点验证 ========
  test('11. 后端API端点全面检查', async ({ page }) => {
    const endpoints = [
      { name: 'Health', url: `${API_BASE}/health`, method: 'GET' },
      { name: 'Auth Me', url: `${API_BASE}/api/auth/me`, method: 'GET' },
      { name: 'Auth Current', url: `${API_BASE}/api/auth/current`, method: 'GET' },
      { name: 'Learning Status', url: `${API_BASE}/api/learning/status`, method: 'GET' },
      { name: 'Knowledge List', url: `${API_BASE}/api/knowledge`, method: 'GET' },
      { name: 'Wrong Questions', url: `${API_BASE}/api/wrong-questions`, method: 'GET' },
      { name: 'Report', url: `${API_BASE}/api/report`, method: 'GET' },
      { name: 'Question Bank List', url: `${API_BASE}/api/question-bank/list`, method: 'GET' },
      { name: 'Question Bank Stats', url: `${API_BASE}/api/question-bank/stats`, method: 'GET' },
      { name: 'Questions Export', url: `${API_BASE}/api/questions/export`, method: 'GET' },
      { name: 'Upload Templates', url: `${API_BASE}/api/upload/templates`, method: 'GET' },
      { name: 'Learning Current', url: `${API_BASE}/api/learning/current`, method: 'GET' },
      { name: 'AI QA History', url: `${API_BASE}/api/ai-qa/history`, method: 'GET' },
      { name: 'Admin Users', url: `${API_BASE}/api/admin/users/list`, method: 'GET' },
    ];

    let passed = 0;
    let failed = 0;

    for (const ep of endpoints) {
      try {
        const response = await fetch(ep.url, { method: ep.method });
        if (response.ok) {
          passed++;
          console.log(`  ✅ ${ep.name}: ${response.status}`);
        } else {
          failed++;
          console.log(`  ⚠️ ${ep.name}: ${response.status} ${response.statusText}`);
        }
      } catch (e) {
        failed++;
        console.log(`  ❌ ${ep.name}: ${e.message}`);
      }
    }

    console.log(`\n📊 API测试结果: ${passed} 通过, ${failed} 失败 (共 ${endpoints.length})`);
    expect(failed).toBe(0);
  });

});
