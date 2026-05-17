# AI伴学系统 — 前端 JavaScript 单元测试结果清单

| 项目 | 值 |
|------|-----|
| 执行时间 | 2026-05-17 |
| 测试框架 | Vitest 3.2.4 + jsdom |
| 测试环境 | Node.js |
| 用例总数 | **36** |
| 通过 | **36** |
| 失败 | **0** |
| 耗时 | ~5s |
| JUnit 报告 | `frontend/tests/junit-report.xml`（运行带 `--reporter=junit` 时生成） |

## 运行方式

```bash
# 项目根目录
npm install
npm run test:frontend

# 监听模式
npm run test:frontend:watch

# 或在 frontend 目录
cd frontend
npx vitest run
```

## 代码结构变更

| 文件 | 说明 |
|------|------|
| `frontend/js/lib/utils.js` | 可测试纯函数（格式化、权限、URL、进度等） |
| `frontend/js/app.js` | 改为 ES Module，从 `utils.js` 引入并挂接 `window.*` 供 onclick 使用 |
| `frontend/index.html` | `<script type="module" src="js/app.js">` |
| `frontend/tests/utils.test.js` | 工具函数单元测试 |
| `frontend/tests/navigation.test.js` | 导航 DOM 行为测试（jsdom） |
| `frontend/vitest.config.js` | Vitest 配置 |

---

## 测试结果总览

| 模块 | 文件 | 用例数 | 通过 | 失败 |
|------|------|--------|------|------|
| 工具函数库 | `utils.test.js` | 33 | 33 | 0 |
| 导航 DOM | `navigation.test.js` | 3 | 3 | 0 |
| **合计** | | **36** | **36** | **0** |

---

## 详细用例清单

### 1. 工具函数 (`utils.test.js`)

| # | 用例 | 描述 | 结果 |
|---|------|------|------|
| 1 | formatText - bold | `**text**` 转为 knowledge-tag | ✅ |
| 2 | formatText - newline | `\n` 转为 `<br>` | ✅ |
| 3 | getPageTitle - known | 已知页面标题 | ✅ |
| 4 | getPageTitle - unknown | 未知页面默认标题 | ✅ |
| 5-6 | getQuestionTypeLabel | 题型标签与回退 | ✅ |
| 7-9 | calcPracticeProgress | 进度百分比计算 | ✅ |
| 10-12 | buildUploadQuestionsUrl | 上传 URL 与 AI 参数 | ✅ |
| 13-14 | checkAnswerMatch | 答案比较（忽略大小写） | ✅ |
| 15-17 | parseStoredUser | localStorage 用户解析 | ✅ |
| 18 | shouldShowAdminNav | 管理员导航可见性 | ✅ |
| 19-22 | hasPagePermission | 页面权限判断 | ✅ |
| 23-25 | getNavItemDisplayState | 导航禁用/隐藏状态 | ✅ |
| 26-28 | togglePermission | 权限列表增删 | ✅ |
| 29-30 | renderPhaseIndicatorHtml | 学习阶段指示器 HTML | ✅ |
| 31-33 | constants | PRD 模块与权限常量 | ✅ |

### 2. 导航 DOM (`navigation.test.js`)

| # | 用例 | 描述 | 结果 |
|---|------|------|------|
| 34 | updates page title | 切换页面时更新标题 | ✅ |
| 35 | shows target page | 显示目标页、隐藏其他页 | ✅ |
| 36 | activates nav item | 高亮对应导航项 | ✅ |

---

## 与后端测试的关系

| 层级 | 命令 | 用例数 |
|------|------|--------|
| 后端 API | `cd backend && python -m pytest tests/` | 46 |
| 前端 JS | `npm run test:frontend` | 36 |
| E2E（可选） | `npx playwright test` | 需启动前后端服务 |

## 未覆盖范围

- `api.request` 完整 fetch 流程（可 Mock fetch 扩展）
- 文件上传拖拽、`handleFileUpload` 全流程
- 聊天/费曼/苏格拉底 UI 交互
- 与真实后端的集成（由 Playwright E2E 覆盖更合适）

## 结论

**全部 36 项前端单元测试通过**。核心纯函数与导航 DOM 逻辑已纳入自动化测试，与后端 46 项用例共同构成项目测试体系。
