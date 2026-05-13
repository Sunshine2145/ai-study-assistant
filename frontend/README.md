# AI伴学系统 - 前端

基于原生 HTML/CSS/JavaScript 构建的单页应用前端，无需构建工具即可运行。

## 技术栈

| 组件 | 选型 |
|------|------|
| 结构 | HTML5 |
| 样式 | CSS3（原生，无框架） |
| 交互 | 原生 JavaScript（ES6+） |
| 图标 | Font Awesome 6.4 |
| 服务 | 可使用 npx serve 或任意静态服务器 |

## 项目结构

```
frontend/
├── index.html    # 主页面
├── css/
│   └── style.css  # 样式文件
├── js/
│   └── app.js     # 主逻辑
└── README.md
```

## 页面结构

### 1. 学习首页 (`page-home`)

- 今日学习卡片（日期、连续天数、今日任务）
- 学习进度概览（知识点完成数、连续天数、总积分、错题数）
- 快速操作按钮

### 2. 开始学习 (`page-learn`)

- AI对话区域（费曼讲解 + 苏格拉底追问）
- 阶段指示器：[费曼学习] → [苏格拉底] → [练习]
- 掌握度显示：XX%
- 消息输入框

### 3. 学习地图 (`page-map`)

- 阶段选择器（Tabs）
- 阶段信息（标题、进度条）
- 知识点列表（状态：已完成/进行中/未解锁）

### 4. 题目练习 (`page-practice`)

- 练习头部（进度条、当前题号）
- 题目卡片（题型、内容、选项）
- 解析卡片（答对/答错显示）
- 操作按钮（上一题、提交答案、继续下一题）

### 5. 错题本 (`page-wrong`)

- 筛选器（本周/本月/全部）
- 错题列表（题目、正确答案、用户答案）
- 一键复习按钮

### 6. 学习报告 (`page-report`)

- 今日学习报告卡片
- 学习内容、完成情况、获得积分

### 7. 题库上传 (`page-upload`)

- 拖拽上传区域
- 格式说明（JSON/TXT/MD/PDF）
- 关联知识点选择
- AI智能解析选项（DeepSeek/MiniMax）

### 8. 题库管理 (`page-question-bank`)

- 题库统计卡片
- 题库列表
- 题目列表（筛选、分页）
- 删除/批准操作

## 页面导航

导航通过 `navigateTo(page)` 函数实现：

```javascript
navigateTo('home');      // 学习首页
navigateTo('learn');      // 开始学习
navigateTo('map');       // 学习地图
navigateTo('practice');  // 题目练习
navigateTo('wrong');     // 错题本
navigateTo('report');    // 学习报告
navigateTo('upload');    // 题库上传
navigateTo('question-bank'); // 题库管理
```

## API对接

前端通过 `api` 对象对接后端 REST API：

```javascript
// API_BASE = 'http://localhost:8081/api'

// 学习
api.getLearningStatus();
api.getCurrentKnowledge();
api.getLearningProgress(id);
api.getMastery(id);
api.selectLearningUnit(id);
api.unlockNext(id);
api.resetLearning();

// 对话
api.sendMessage(text);

// 题目
api.getQuestions(knowledgeId);
api.submitAnswer(questionId, answer);

// 题库
api.getQuestionBanks();
api.getQuestionBankQuestions(source, page);
api.deleteQuestion(id);
api.approveQuestion(id);

// 上传
api.uploadQuestions(formData, useAiParse, aiProvider);

// 错题
api.getWrongQuestions(filter);
```

## 状态管理

```javascript
const state = {
    user: null,
    currentKnowledge: null,      // 当前知识点
    questions: [],               // 练习题列表
    currentQuestionIndex: 0,      // 当前题目索引
    wrongQuestions: [],          // 错题列表
    stageData: []                // 知识点数据
};
```

## 主要功能函数

| 函数 | 说明 |
|------|------|
| `navigateTo(page)` | 页面导航 |
| `loadPageData(page)` | 加载页面数据 |
| `loadHomeData()` | 加载首页数据 |
| `loadLearnData()` | 加载学习页数据（含费曼讲解） |
| `loadMapData()` | 加载学习地图数据 |
| `loadPracticeData()` | 加载练习题数据 |
| `sendMessage()` | 发送消息进行苏格拉底问答 |
| `showToast(message, type)` | 显示提示消息 |
| `resetLearningMap()` | 重置学习进度 |

## 启动方式

### 方式1：使用 serve

```bash
cd frontend
npx serve -l 3000
# 访问 http://localhost:3000
```

### 方式2：直接打开

```bash
# 在浏览器中直接打开 index.html
# 或使用 Python 简易服务器
python -m http.server 3000
```

### 方式3：VS Code Live Server

在 VS Code 中安装 Live Server 插件，右键 `index.html` → "Open with Live Server"

## 关键页面流程

### 学习流程

```
1. 用户进入学习地图 (page-map)
2. 选择知识点开始学习
3. 进入费曼学习阶段 (page-learn)
4. 通过苏格拉底追问达到90%掌握度
5. 解锁题目练习 (page-practice)
6. 完成后自动解锁下一知识点
```

### 题库上传流程

```
1. 进入题库上传页面 (page-upload)
2. 选择文件或拖拽上传
3. 选择AI提供商（DeepSeek/MiniMax）
4. 点击上传，AI自动解析
5. 查看上传结果
6. 进入题库管理查看和管理题目
```

## 样式变量

```css
:root {
    --primary: #2563EB;        /* 主色 */
    --primary-dark: #1D4ED8;
    --success: #10B981;         /* 成功色 */
    --warning: #F59E0B;        /* 警告色 */
    --error: #EF4444;          /* 错误色 */
    --bg-primary: #EFF6FF;     /* 主背景色 */
    --text-primary: #1E293B;   /* 主文字色 */
    --text-secondary: #64748B; /* 次文字色 */
    --border-color: #E2E8F0;   /* 边框色 */
    --radius-sm: 6px;
    --radius-md: 8px;
    --radius-lg: 12px;
}
```

## 响应式断点

```css
/* 平板 */
@media (max-width: 1024px) { ... }

/* 移动端 */
@media (max-width: 768px) { ... }
```
