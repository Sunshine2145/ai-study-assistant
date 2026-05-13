const { chromium } = require('playwright');
const http = require('http');

const BASE_URL = 'http://localhost:8081';
const API_BASE = 'http://localhost:5001';

function fetch(url, method = 'GET') {
  return new Promise((resolve, reject) => {
    const req = http.request(url, { method }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve({ status: res.statusCode, data }));
    });
    req.on('error', reject);
    req.end();
  });
}

(async () => {
  console.log('=== AI伴学系统 Playwright 测试 ===\n');

  // Check backend health
  try {
    const health = await fetch(`${API_BASE}/health`);
    console.log(`Backend: ${health.status === 200 ? '✅' : '❌'} health check (${health.status})`);
  } catch (e) {
    console.log(`❌ Backend not reachable: ${e.message}`);
    process.exit(1);
  }

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  let passed = 0;
  let failed = 0;

  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') errors.push(msg.text());
  });

  try {
    // Test 1: Page loads
    console.log('\n📄 测试1: 前端页面加载');
    await page.goto(`${BASE_URL}/index.html`, { waitUntil: 'networkidle', timeout: 10000 });
    console.log('  ✅ 页面加载成功');

    // Test 2: Home page
    console.log('\n📄 测试2: 学习首页');
    try {
      await page.waitForSelector('#pageTitle', { timeout: 5000 });
      const title = await page.textContent('#pageTitle');
      console.log(`  ${title ? '✅' : '⚠️'} 页面标题: ${title || '未找到'}`);
      passed++;
    } catch (e) {
      console.log(`  ❌ 首页加载失败: ${e.message}`);
      failed++;
    }

    // Test 3: Navigate to map
    console.log('\n📄 测试3: 学习地图');
    try {
      await page.click('.nav-item[data-page="map"]');
      await page.waitForTimeout(1000);
      await page.waitForSelector('#page-map', { state: 'visible', timeout: 3000 });
      const kpItems = await page.$$('.knowledge-point-item');
      console.log(`  ✅ 学习地图可见，知识点数: ${kpItems.length}`);
      passed++;
    } catch (e) {
      console.log(`  ❌ 学习地图失败: ${e.message}`);
      failed++;
    }

    // Test 4: Navigate to AI Q&A
    console.log('\n📄 测试4: AI问答');
    try {
      await page.click('.nav-item[data-page="ai-qa"]');
      await page.waitForTimeout(1000);
      await page.waitForSelector('#page-ai-qa', { state: 'visible', timeout: 3000 });
      console.log('  ✅ AI问答页面可见');
      passed++;
    } catch (e) {
      console.log(`  ❌ AI问答失败: ${e.message}`);
      failed++;
    }

    // Test 5: Navigate to practice
    console.log('\n📄 测试5: 题目练习');
    try {
      await page.click('.nav-item[data-page="practice"]');
      await page.waitForTimeout(1000);
      await page.waitForSelector('#page-practice', { state: 'visible', timeout: 3000 });
      console.log('  ✅ 题目练习页面可见');
      passed++;
    } catch (e) {
      console.log(`  ❌ 题目练习失败: ${e.message}`);
      failed++;
    }

    // Test 6: Navigate to wrong questions
    console.log('\n📄 测试6: 错题本');
    try {
      await page.click('.nav-item[data-page="wrong"]');
      await page.waitForTimeout(1000);
      await page.waitForSelector('#page-wrong', { state: 'visible', timeout: 3000 });
      console.log('  ✅ 错题本页面可见');
      passed++;
    } catch (e) {
      console.log(`  ❌ 错题本失败: ${e.message}`);
      failed++;
    }

    // Test 7: Navigate to report
    console.log('\n📄 测试7: 学习报告');
    try {
      await page.click('.nav-item[data-page="report"]');
      await page.waitForTimeout(1000);
      await page.waitForSelector('#page-report', { state: 'visible', timeout: 3000 });
      console.log('  ✅ 学习报告页面可见');
      passed++;
    } catch (e) {
      console.log(`  ❌ 学习报告失败: ${e.message}`);
      failed++;
    }

    // Test 8: Navigate to upload
    console.log('\n📄 测试8: 题库上传');
    try {
      await page.click('.nav-item[data-page="upload"]');
      await page.waitForTimeout(1000);
      await page.waitForSelector('#page-upload', { state: 'visible', timeout: 3000 });
      const uploadZone = await page.$('#uploadZone');
      console.log(`  ${uploadZone ? '✅' : '❌'} 上传区域${uploadZone ? '' : '未'}找到`);
      passed++;
    } catch (e) {
      console.log(`  ❌ 题库上传失败: ${e.message}`);
      failed++;
    }

    // Test 9: Navigate to question bank
    console.log('\n📄 测试9: 题库管理');
    try {
      await page.click('.nav-item[data-page="question-bank"]');
      await page.waitForTimeout(1000);
      await page.waitForSelector('#page-question-bank', { state: 'visible', timeout: 3000 });
      console.log('  ✅ 题库管理页面可见');
      passed++;
    } catch (e) {
      console.log(`  ❌ 题库管理失败: ${e.message}`);
      failed++;
    }

    // Test 10: Login flow
    console.log('\n📄 测试10: 登录流程');
    try {
      await page.goto(`${BASE_URL}/index.html`, { waitUntil: 'networkidle' });
      await page.waitForTimeout(1000);
      const loginPage = await page.$('#page-login');
      if (loginPage && await loginPage.isVisible()) {
        await page.fill('#loginUsername', 'user');
        await page.fill('#loginPassword', 'admin123');
        await page.click('.login-submit-btn');
        await page.waitForTimeout(2000);
        console.log('  ✅ 登录表单提交成功');
      } else {
        console.log('  ⚠️ 登录页面不可见（可能已登录）');
      }
      passed++;
    } catch (e) {
      console.log(`  ❌ 登录失败: ${e.message}`);
      failed++;
    }

    // Test 11: Knowledge point selection
    console.log('\n📄 测试11: 知识点选择');
    try {
      await page.click('.nav-item[data-page="map"]');
      await page.waitForTimeout(1000);
      const learnBtn = await page.$('.kp-btn-learn, .kp-btn-review, .btn-learn, [onclick*="selectKnowledgePoint"]');
      if (learnBtn) {
        await learnBtn.click();
        await page.waitForTimeout(1000);
        console.log('  ✅ 知识点选择成功');
      } else {
        console.log('  ⚠️ 未找到可学习的知识点按钮');
      }
      passed++;
    } catch (e) {
      console.log(`  ❌ 知识点选择失败: ${e.message}`);
      failed++;
    }

    // API endpoints test
    console.log('\n📄 测试12: 后端API端点');
    const endpoints = [
      ['Health', `${API_BASE}/health`],
      ['Auth /me', `${API_BASE}/api/auth/me`],
      ['Auth /current', `${API_BASE}/api/auth/current`],
      ['Learning Status', `${API_BASE}/api/learning/status`],
      ['Knowledge List', `${API_BASE}/api/knowledge`],
      ['Wrong Questions', `${API_BASE}/api/wrong-questions`],
      ['Report', `${API_BASE}/api/report`],
      ['Question Bank List', `${API_BASE}/api/question-bank/list`],
      ['Question Bank Stats', `${API_BASE}/api/question-bank/stats`],
      ['Questions Export', `${API_BASE}/api/questions/export`],
      ['Upload Templates', `${API_BASE}/api/upload/templates`],
      ['Learning Current', `${API_BASE}/api/learning/current`],
      ['Reminders', `${API_BASE}/api/reminders`],
      ['Admin Users', `${API_BASE}/api/admin/users/list`],
    ];

    for (const [name, url] of endpoints) {
      try {
        const res = await fetch(url);
        const status = res.status < 400 ? '✅' : '⚠️';
        console.log(`  ${status} ${name} (${res.status})`);
        if (res.status < 400) passed++;
        else failed++;
      } catch (e) {
        console.log(`  ❌ ${name}: ${e.message}`);
        failed++;
      }
    }

  } catch (e) {
    console.log(`\n❌ 测试异常: ${e.message}`);
    failed++;
  }

  // Summary
  console.log('\n========================================');
  console.log(`📊 测试结果: ${passed} 通过, ${failed} 失败 (共 ${passed + failed})`);
  console.log('========================================');

  if (errors.length > 0) {
    console.log(`\n⚠️ 浏览器控制台错误 (${errors.length}):`);
    errors.slice(0, 5).forEach(e => console.log(`  - ${e.substring(0, 150)}`));
  }

  await browser.close();

  process.exit(failed > 0 ? 1 : 0);
})();
