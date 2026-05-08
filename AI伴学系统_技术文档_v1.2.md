# AI伴学系统 - 产品技术文档

> 📅 文档版本：v1.2 | 日期：2026-05-07
> 👤 开发者：1902
> 🎯 基于：PRD v1.0

---

## 一、系统概述

### 1.1 项目背景

基于PRD文档，AI伴学系统旨在通过**费曼学习法 + 苏格拉底提问法**，为用户提供"懂教学法"的AI私教体验，彻底弄懂每一个知识点。

### 1.2 技术目标

| 目标 | 说明 |
|------|------|
| 前后端分离 | 前端H5/小程序，后端API服务 |
| AI驱动 | 后端接入AI能力，智能交互 |
| 跨平台 | 飞书/微信/浏览器多端访问 |
| 实时对话 | AI即时响应，支持追问 |

### 1.3 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      用户端（多端）                        │
├─────────────┬─────────────┬─────────────┬─────────────────┤
│  飞书机器人  │  微信小程序  │   H5浏览器   │    桌面客户端    │
└──────┬──────┴──────┬──────┴──────┬──────┴────────┬───────┘
       │             │             │              │
       └─────────────┴──────┬──────┴──────────────┘
                            │ HTTP/WebSocket
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway (Nginx)                       │
│              限流 / 鉴权 / 路由 / 跨域                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
         ┌─────────────────┴─────────────────┐
         │                                   │
         ▼                                   ▼
┌──────────────────┐             ┌──────────────────┐
│    AI服务层        │             │    业务服务层     │
│                  │             │                  │
│  ┌─────────────┐ │             │  ┌─────────────┐ │
│  │  智谱GLM   │ │             │  │  学习引擎   │ │
│  │  GPT-4     │ │             │  │  题目服务   │ │
│  │  Claude    │ │             │  │  用户服务   │ │
│  └─────────────┘ │             │  └─────────────┘ │
│                  │             │                  │
└──────────────────┘             └────────┬─────────┘
                                           │
                          ┌────────────────┼────────────────┐
                          │                │                │
                          ▼                ▼                ▼
                  ┌──────────┐    ┌──────────┐    ┌──────────┐
                  │  MySQL   │    │  Redis   │    │ 文件存储  │
                  │  数据库   │    │   缓存   │    │  知识库   │
                  └──────────┘    └──────────┘    └──────────┘
```

---

## 二、技术选型

### 2.1 前端技术栈

| 组件 | 选型 | 理由 |
|------|------|------|
| **跨端框架** | Uni-app / Taro | 一套代码多端发布 |
| **UI框架** | Vant Weapp / WeUI | 轻量、适配好 |
| **状态管理** | Pinia | Vue3最佳状态管理 |
| **实时通信** | WebSocket | AI对话即时响应 |
| **本地存储** | localStorage | 离线缓存 |

### 2.2 后端技术栈

| 组件 | 选型 | 理由 |
|------|------|------|
| **Runtime** | Node.js 18+ | 生态好、异步I/O强 |
| **框架** | NestJS | 结构化、模块化 |
| **ORM** | TypeORM | TypeScript支持好 |
| **数据库** | MySQL 8.0 | 主数据存储 |
| **缓存** | Redis 7.x | 会话、队列缓存 |
| **AI SDK** | @zhipu-ai/sdk | 智谱AI中文优化 |
| **实时通信** | Socket.io | WebSocket封装 |

### 2.3 AI模型选型

| 模型 | 场景 | 特点 |
|------|------|------|
| **智谱GLM-4** | 费曼讲解 | 中文理解强 |
| **GPT-4** | 苏格拉底追问 | 追问深度好 |
| **Claude 3** | 知识解析 | 解释清晰 |

---

## 三、前端设计

### 3.1 页面结构

```
src/
├── pages/
│   ├── index/              # 首页（今日任务）
│   ├── chat/               # AI对话页（核心）
│   ├── knowledge/          # 知识库浏览
│   ├── practice/           # 题目练习
│   ├── wrong/              # 错题本
│   ├── progress/           # 学习进度
│   └── profile/            # 个人中心
├── components/
│   ├── ChatBubble/         # 对话气泡
│   ├── QuestionCard/       # 题目卡片
│   ├── FeynmanCard/         # 费曼讲解卡片
│   ├── ProgressRing/       # 进度圆环
│   └── SocraticQuestion/    # 苏格拉底追问
├── services/
│   ├── api.js             # API封装
│   ├── websocket.js        # WebSocket封装
│   └── ai.js              # AI对话服务
└── store/
    ├── user.js            # 用户状态
    ├── chat.js            # 对话状态
    └── progress.js         # 进度状态
```

### 3.2 核心页面交互

#### AI对话页（chat）

```
┌────────────────────────────────────────┐
│  AI伴学助手                    设置 ⚙️   │
├────────────────────────────────────────┤
│                                        │
│  ┌──────────────────────────────────┐ │
│  │ 📚 费曼讲解                      │ │
│  │                                  │ │
│  │ 今天我们学习Cache...             │ │
│  │                                  │ │
│  │ 想象你在厨房做饭：              │ │
│  │ - 你 = CPU                      │ │
│  │ - 冰箱 = 内存                  │ │
│  │ - 厨房台面 = Cache              │ │
│  └──────────────────────────────────┘ │
│                                        │
│           ┌──────────────────────────┐  │
│           │ 🔍 我来考考你：         │  │
│           │                          │  │
│           │ 为什么Cache比内存快？    │  │
│           └──────────────────────────┘  │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │ 🤔 用户回答                     │ │
│  │                                  │ │
│  │ 因为离CPU近...                   │ │
│  └──────────────────────────────────┘ │
│                                        │
├────────────────────────────────────────┤
│                                        │
│  ┌────────────────────────────────┐    │
│  │ 请输入你的回答...           发送 │    │
│  └────────────────────────────────┘    │
└────────────────────────────────────────┘
```

### 3.3 状态管理

```javascript
// store/chat.js
{
  state: {
    sessionId: 'uuid-xxx',        // 对话会话ID
    messages: [                      // 消息列表
      {
        id: 'msg-001',
        role: 'ai',                 // ai / user
        type: 'feynman',            // feynman / socratic / question / answer
        content: '今天我们学习Cache...',
        timestamp: 1714899200000,
        metadata: {
          knowledgeId: '1.1',
          difficulty: 2
        }
      }
    ],
    currentMode: 'feynman',         // feynman / socratic / practice
    isTyping: false,               // AI正在输入
    feedback: null                  // 用户对回答的反馈
  }
}
```

---

## 四、后端设计

### 4.1 项目结构

```
backend/
├── src/
│   ├── main.ts                     # 入口
│   ├── app.module.ts               # 根模块
│   │
│   ├── modules/
│   │   ├── chat/                   # AI对话模块
│   │   │   ├── chat.controller.ts
│   │   │   ├── chat.service.ts
│   │   │   ├── chat.gateway.ts    # WebSocket网关
│   │   │   ├── dto/
│   │   │   │   ├── send-message.dto.ts
│   │   │   │   └── ai-response.dto.ts
│   │   │   └── entities/
│   │   │       └── session.entity.ts
│   │   │
│   │   ├── knowledge/              # 知识库模块
│   │   │   ├── knowledge.controller.ts
│   │   │   ├── knowledge.service.ts
│   │   │   └── entities/
│   │   │       ├── knowledge.entity.ts
│   │   │       ├── question.entity.ts
│   │   │       └── wrong.entity.ts
│   │   │
│   │   ├── user/                  # 用户模块
│   │   │   ├── user.controller.ts
│   │   │   ├── user.service.ts
│   │   │   └── entities/
│   │   │       └── user.entity.ts
│   │   │
│   │   ├── progress/              # 进度模块
│   │   │   ├── progress.controller.ts
│   │   │   ├── progress.service.ts
│   │   │   └── entities/
│   │   │       ├── progress.entity.ts
│   │   │       └── daily-log.entity.ts
│   │   │
│   │   ├── ai/                   # AI服务模块
│   │   │   ├── ai.controller.ts
│   │   │   ├── ai.service.ts
│   │   │   ├── providers/
│   │   │   │   ├── zhipu.provider.ts
│   │   │   │   ├── openai.provider.ts
│   │   │   │   └── anthropic.provider.ts
│   │   │   └── prompts/
│   │   │       ├── feynman.prompt.ts
│   │   │       └── socratic.prompt.ts
│   │   │
│   │   └── gateway/               # 统一网关
│   │       └── gateway.module.ts
│   │
│   ├── common/
│   │   ├── guards/
│   │   │   └── auth.guard.ts
│   │   ├── interceptors/
│   │   │   └── logging.interceptor.ts
│   │   └── filters/
│   │       └── http-exception.filter.ts
│   │
│   └── config/
│       ├── database.config.ts
│       ├── redis.config.ts
│       └── ai.config.ts
│
├── test/
├── package.json
├── tsconfig.json
└── nest-cli.json
```

### 4.2 数据库设计

#### 用户表 (user)

```sql
CREATE TABLE `user` (
  `id` VARCHAR(36) PRIMARY KEY,
  `openid` VARCHAR(100) UNIQUE,        -- 微信openid
  `nickname` VARCHAR(50),              -- 昵称
  `avatar` VARCHAR(255),                -- 头像
  `level` INT DEFAULT 1,              -- 学习等级
  `score` INT DEFAULT 0,              -- 总积分
  `streak` INT DEFAULT 0,             -- 连续学习天数
  `streak_last_date` DATE,            -- 最后学习日期
  `created_at` DATETIME DEFAULT NOW(),
  `updated_at` DATETIME DEFAULT NOW()
);
```

#### 知识点表 (knowledge)

```sql
CREATE TABLE `knowledge` (
  `id` VARCHAR(36) PRIMARY KEY,
  `chapter` VARCHAR(20),              -- 章节编号 1.1
  `title` VARCHAR(100),               -- 标题
  `content` TEXT,                      -- 费曼讲解原文
  `level` INT DEFAULT 1,              -- 难度等级 1-5
  `status` ENUM('locked','available','completed') DEFAULT 'locked',
  `next_knowledge_id` VARCHAR(36),     -- 下一知识点
  `created_at` DATETIME DEFAULT NOW()
);
```

#### 题目表 (question)

```sql
CREATE TABLE `question` (
  `id` VARCHAR(36) PRIMARY KEY,
  `knowledge_id` VARCHAR(36),           -- 关联知识点
  `type` ENUM('single','multiple','judge'),
  `content` TEXT,                    -- 题目内容
  `options` JSON,                    -- 选项 [A,B,C,D]
  `answer` INT,                       -- 正确答案索引
  `explanation` TEXT,                 -- 解析
  `difficulty` INT DEFAULT 1,          -- 难度 1-5
  `wrong_count` INT DEFAULT 0,        -- 错误次数
  `created_at` DATETIME DEFAULT NOW()
);
```

#### 对话会话表 (session)

```sql
CREATE TABLE `session` (
  `id` VARCHAR(36) PRIMARY KEY,
  `user_id` VARCHAR(36),
  `knowledge_id` VARCHAR(36),           -- 当前知识点
  `mode` ENUM('feynman','socratic','practice'),
  `messages` JSON,                    -- 历史消息
  `status` ENUM('active','completed'),
  `started_at` DATETIME,
  `completed_at` DATETIME,
  `created_at` DATETIME DEFAULT NOW()
);
```

#### 学习进度表 (progress)

```sql
CREATE TABLE `progress` (
  `id` VARCHAR(36) PRIMARY KEY,
  `user_id` VARCHAR(36),
  `knowledge_id` VARCHAR(36),
  `status` ENUM('not_started','in_progress','completed'),
  `score` INT DEFAULT 0,              -- 本知识点得分
  `attempts` INT DEFAULT 0,           -- 尝试次数
  `correct_count` INT DEFAULT 0,       -- 答对次数
  `started_at` DATETIME,
  `completed_at` DATETIME,
  `created_at` DATETIME DEFAULT NOW()
);
```

#### 错题表 (wrong_question)

```sql
CREATE TABLE `wrong_question` (
  `id` VARCHAR(36) PRIMARY KEY,
  `user_id` VARCHAR(36),
  `question_id` VARCHAR(36),
  `user_answer` INT,                  -- 用户选择的答案
  `wrong_reason` TEXT,               -- 错误原因分析
  `mastered` BOOLEAN DEFAULT FALSE,   -- 是否已掌握
  `review_count` INT DEFAULT 0,       -- 复习次数
  `last_reviewed_at` DATETIME,
  `created_at` DATETIME DEFAULT NOW()
);
```

### 4.3 API设计

#### 对话相关

| 接口 | 方法 | 说明 |
|------|------|------|
| `POST /api/chat/send` | 发送消息 | AI对话 |
| `GET /api/chat/sessions` | 获取会话列表 | 用户所有会话 |
| `GET /api/chat/session/:id` | 获取会话详情 | 包含历史消息 |
| `POST /api/chat/session` | 创建新会话 | 开始新知识点学习 |
| `DELETE /api/chat/session/:id` | 删除会话 | 清除对话记录 |

#### 知识库相关

| 接口 | 方法 | 说明 |
|------|------|------|
| `GET /api/knowledge` | 获取知识列表 | 按章节分类 |
| `GET /api/knowledge/:id` | 获取知识点详情 | 包含题目 |
| `GET /api/knowledge/:id/questions` | 获取关联题目 | 练习用 |

#### 用户相关

| 接口 | 方法 | 说明 |
|------|------|------|
| `POST /api/user/login` | 微信登录 | 获取token |
| `GET /api/user/profile` | 获取用户信息 | 等级/积分/连胜 |
| `PUT /api/user/profile` | 更新用户信息 | 昵称/头像 |

#### 进度相关

| 接口 | 方法 | 说明 |
|------|------|------|
| `GET /api/progress` | 获取学习进度 | 全局进度 |
| `GET /api/progress/daily` | 获取日报 | 当日学习情况 |
| `POST /api/progress/complete` | 完成知识点 | 更新进度 |

### 4.4 WebSocket事件

#### 客户端 → 服务端

| 事件 | 说明 | 数据 |
|------|------|------|
| `chat:message` | 发送消息 | `{sessionId, content}` |
| `chat:feedback` | 回答反馈 | `{messageId, isCorrect}` |
| `chat:typing` | 开始输入 | `{sessionId}` |
| `chat:stop` | 停止生成 | `{sessionId}` |

#### 服务端 → 客户端

| 事件 | 说明 | 数据 |
|------|------|------|
| `chat:response` | AI回复 | `{sessionId, message, done}` |
| `chat:typing` | AI正在输入 | `{sessionId}` |
| `chat:error` | 错误 | `{code, message}` |
| `progress:update` | 进度更新 | `{knowledgeId, status}` |

---

## 五、AI服务设计

---

## 四、学习地图与核心功能模块

### 4.1 学习地图模块

#### 功能说明

学习地图是系统的核心入口，以树形结构展示完整学习路径（章节→知识节→知识点），支持点击跳转和状态展示。

#### 页面结构

```
┌─────────────────────────────────────────────────────────────────┐
│  📍 学习地图                                         [返回首页] │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📚 第一章：计算机基础                                           │
│  ├── 📖 1.1 存储系统                                             │
│  │   ├── 🔓 Cache（高速缓存存储器）  ✅ 已掌握                   │
│  │   ├── 🔓 内存管理                     ⏳ 进行中               │
│  │   └── 🔓 硬盘与IO                     🔒 待解锁              │
│  ├── 📖 1.2 指令系统                                             │
│  │   └── 🔒 ...                                                │
│  └── 📖 1.3 CPU结构                                             │
│       └── 🔒 ...                                                │
│                                                                  │
│  📚 第二章：操作系统                                             │
│  └── 🔒 ...                                                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 数据模型

```typescript
// 章节模型
interface Chapter {
  id: string;
  title: string;              // "第一章：计算机基础"
  order: number;               // 排序
  sections: Section[];        // 包含的知识节
}

// 知识节模型
interface Section {
  id: string;
  chapterId: string;
  title: string;              // "1.1 存储系统"
  order: number;
  knowledgePoints: KnowledgePoint[];
}

// 知识点模型
interface KnowledgePoint {
  id: string;
  sectionId: string;
  title: string;              // "Cache（高速缓存存储器）"
  officialContent: string;   // 官方教材内容
  status: 'locked' | 'in_progress' | 'completed';
  masteryLevel: number;      // 掌握度 0-100
  order: number;
  nextPointId: string | null; // 下一知识点ID
}
```

#### API设计

| 接口 | 方法 | 说明 |
|------|------|------|
| `GET /api/study-map` | 获取学习地图 | 全量章节+知识点树 |
| `GET /api/study-map/chapter/:id` | 获取章节详情 | 章节下知识点列表 |
| `GET /api/study-map/point/:id` | 获取知识点详情 | 包含官方内容 |
| `POST /api/study-map/unlock` | 解锁知识点 | 前置知识点达标后 |
| `PUT /api/study-map/mastery` | 更新掌握度 | AI帮测后更新 |

#### 状态管理

```typescript
// store/studyMap.js
{
  state: {
    chapters: [],                    // 章节树
    currentChapter: null,            // 当前章节
    currentPoint: null,              // 当前知识点
    expandedSections: [],            // 展开的章节ID列表
    masteryLevels: {},                // { pointId: masteryLevel }
    unlockedPoints: []                // 已解锁知识点ID列表
  }
}
```

### 4.2 AI解答模块

#### 功能说明

用户点击"AI解答"后，AI以费曼学习法讲解知识点，支持用户追问。

#### 交互流程

```
用户点击【AI解答】
    ↓
加载知识点官方内容
    ↓
AI费曼讲解（首次自动讲解）
    ↓
用户可追问 → AI继续解答
    ↓
用户点击【AI帮测】或退出
```

#### Prompt模板

```typescript
const feynmanPrompt = (knowledge: KnowledgePoint, userQuestion?: string) => `
你是大王的学习助手，擅长用费曼学习法解答疑问。

【知识点】
标题：${knowledge.title}
官方内容：${knowledge.officialContent}

${userQuestion ? `【用户提问】${userQuestion}` : '【任务】请先用费曼法讲解这个知识点'}

费曼学习法原则：
1. 用最简单的话讲清楚，让8岁小孩都能听懂
2. 用生活化类比解释抽象概念
3. 层层递进，从已知到未知
4. 最后引导用户自己总结

${userQuestion ? `
解答格式：
🤖 【AI解答】
[直接回应疑问]
[类比解释]
[回到核心概念]
[引导思考]
` : `
首次讲解格式：
📚 【费曼讲解】${knowledge.title}

[类比引入] - 用生活场景开始
[核心解释] - 简洁明了
[生活例子] - 1-2个例子
[思考引导] - 抛出问题让用户思考
`}
`;
```

### 4.3 AI帮测模块

#### 功能说明

用户点击"AI帮测"后，AI通过苏格拉底提问法测试学习效果，掌握度≥90%自动解锁下一知识点。

#### 交互流程

```
用户点击【AI帮测】
    ↓
初始化测试会话
    ↓
AI提问第1题（基础问题）
    ↓
用户回答
    ↓
AI评价回答质量（优秀/良好/一般/较差/错误）
    ↓
累计掌握度 += 该回答得分
    ↓
掌握度 ≥ 90%？
  ├── 是 → 🎉 恭喜解锁，触发解锁流程
  └── 否 → 继续提问下一题（最多5题）
           5题后仍<90% → 返回重新学习
```

#### 掌握度判定

```typescript
const MASTERY_SCORES = {
  excellent: 25,    // 完全正确+理解到位
  good: 15,         // 正确但理解一般
  fair: 8,          // 部分正确
  poor: 5,          // 方向对但细节错
  wrong: 0          // 完全不对
};

// 解锁阈值
const UNLOCK_THRESHOLD = 90; // 90%
const MAX_QUESTIONS = 5;
```

#### 苏格拉底提问策略

```typescript
const socraticStrategy = (knowledge: KnowledgePoint, questionNumber: number) => {
  const levels = [
    '事实性问题（是什么）',
    '理解性问题（为什么）',
    '应用性问题（怎么样）',
    '分析性问题（与其他知识的关系）',
    '评价性问题（你的看法）'
  ];
  
  // 根据题目序号选择不同层次的问题
  // Q1: Level 1 (事实) → Q2: Level 2 (理解) → Q3: Level 3 (应用)
  // Q4: Level 4 (分析) → Q5: Level 5 (评价)
};
```

#### Prompt模板

```typescript
const socraticPrompt = (knowledge: KnowledgePoint, userAnswer?: string, questionNumber?: number, totalMastery?: number) => `
你是大王的学习助手，擅长用苏格拉底提问法测试学习效果。

【当前知识点】${knowledge.title}
【核心要点】${knowledge.keyPoints}
【官方内容】${knowledge.officialContent}
【当前累计掌握度】${totalMastery || 0}%

${userAnswer ? `
【用户回答】${userAnswer}
请评价回答质量并决定下一问题。
` : `
【任务】开始苏格拉底提问测试。问第1个问题（Level 1：事实性问题）。
`}

苏格拉底提问规则：
1. 每次只问1个问题
2. 不直接给答案，通过追问引导
3. 正确时追问更深层
4. 错误时用引导性问题纠正
5. 5题后判断是否达到90%掌握度

回答质量评分：
- 优秀（完全正确+理解到位）：+25%
- 良好（正确但理解一般）：+15%
- 一般（部分正确）：+8%
- 较差（方向对但细节错）：+5%
- 错误（完全不对）：+0%

${userAnswer ? `
评价格式：
✅/⚠️ [评价]
${questionNumber < 5 && totalMastery < 90 ? `❓ 下一问题：` : ''}
[新问题或最终判定]
` : `
问题格式：
🤔 【苏格拉底提问】
❓ 问题1/5：
[问题内容]
`}
`;
```

### 4.4 知识点解锁模块

#### 解锁规则

| 条件 | 结果 |
|------|------|
| 知识点掌握度 ≥ 90% | 自动解锁下一知识点 |
| 章节内所有知识点完成 | 自动解锁下一章节 |
| 前置知识点未达标 | 保持锁定状态 |

#### 解锁流程

```typescript
// 解锁服务
async function unlockNextPoint(currentPointId: string) {
  const current = await getKnowledgePoint(currentPointId);
  
  // 检查是否达到解锁条件
  if (current.masteryLevel >= UNLOCK_THRESHOLD) {
    // 解锁下一知识点
    if (current.nextPointId) {
      await updatePointStatus(current.nextPointId, 'in_progress');
      await notifyUser(`🎉 已解锁新知识点：${current.nextPoint.title}`);
    }
    
    // 检查章节是否完成
    const sectionPoints = await getSectionPoints(current.sectionId);
    const allCompleted = sectionPoints.every(p => p.status === 'completed');
    if (allCompleted) {
      await unlockNextSection(current.sectionId);
    }
  }
}
```

### 5.1 AI服务架构

```typescript
// ai.service.ts
@Injectable()
export class AIService {
  constructor(
    private zhipuProvider: ZhipuProvider,
    private openaiProvider: OpenAIProvider,
  ) {}

  // 费曼讲解
  async feynmanExplain(knowledgeId: string): Promise<Stream> {
    const knowledge = await this.knowledgeService.findById(knowledgeId);
    const prompt = feynmanPrompt(knowledge);
    return this.zhipuProvider.stream(prompt);
  }

  // 苏格拉底追问
  async socraticQuestion(
    context: ChatContext,
    userAnswer: string
  ): Promise<Stream> {
    const prompt = socraticPrompt(context, userAnswer);
    return this.zhipuProvider.stream(prompt);
  }

  // 题目解析
  async explainAnswer(questionId: string, userAnswer: string): Promise<string> {
    const question = await this.questionService.findById(questionId);
    const prompt = explanationPrompt(question, userAnswer);
    return this.zhipuProvider.complete(prompt);
  }
}
```

### 5.2 提示词模板

#### 费曼讲解提示词

```typescript
const feynmanPrompt = (knowledge: Knowledge) => `
你是${STUDENT_NAME}的AI学习助手，擅长用费曼学习法讲解知识点。

费曼学习法的核心是：用最简单的话把概念讲清楚，让8岁小孩都能听懂。

请用费曼学习法讲解以下知识点：

---
主题：${knowledge.title}
内容：${knowledge.content}
---

讲解要求：
1. 先用一个生活化的类比引入（用常见的场景解释）
2. 解释核心概念（不超3句话）
3. 举1-2个生活中的例子
4. 用"如果...会怎样"引导思考

格式：
📚 【费曼讲解】${knowledge.title}

[类比引入]
[核心解释]
[生活例子]
[思考引导]
`;
```

#### 苏格拉底追问提示词

```typescript
const socraticPrompt = (context: ChatContext, userAnswer: string) => `
你是${STUDENT_NAME}的AI学习助手，擅长用苏格拉底提问法引导学生思考。

苏格拉底法的核心：不直接给答案，通过连续追问让学生自己发现答案。

当前情境：
- 知识点：${context.knowledge.title}
- AI的问题：${context.lastQuestion}
- 学生的回答：${userAnswer}

当前回答分析：
${analyzeAnswer(userAnswer)}

请根据学生的回答，给出追问或反馈：

规则：
1. 如果回答正确 → 给予肯定，追问更深层问题
2. 如果回答部分正确 → 指出模糊点，追问澄清
3. 如果回答错误 → 不直接否定，用问题引导

格式：
🤔 【追问】
[基于学生回答的追问或反馈]

[如果是追问，格式：]
❓ [追问问题]

[如果需要提示，格式：]
💡 [一个引导性提示]
`;
```

### 5.3 AI模型切换

```typescript
// ai.config.ts
export const AI_CONFIG = {
  default: 'zhipu',
  
  providers: {
    zhipu: {
      apiKey: process.env.ZHIPU_API_KEY,
      model: 'glm-4',
      baseURL: 'https://open.bigmodel.cn/api/paas/v4',
    },
    openai: {
      apiKey: process.env.OPENAI_API_KEY,
      model: 'gpt-4',
      baseURL: 'https://api.openai.com/v1',
    },
  },
  
  // 不同场景使用不同模型
  scenarios: {
    feynman: 'zhipu',      // 费曼讲解用智谱
    socratic: 'openai',     // 苏格拉底追问用GPT
    explanation: 'zhipu',   // 解析用智谱
  }
};
```

---

## 六、题库上传与管理技术实现

### 6.1 模块概述

题库上传与管理模块负责将线下文档导入系统，通过AI自动理解、分类、结构化存储，形成可用的题库资源。

```
┌─────────────────────────────────────────────────────────────────┐
│                题库上传与管理模块架构                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  文档解析   │  │  AI处理    │  │  数据存储   │             │
│  │  docx/pdf   │→ │  分类/提取  │→ │  MySQL     │             │
│  │  txt/md/excel│  │  GLM-4     │  │  Redis缓存 │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              管理员端（题库管理后台）                     │    │
│  │  知识点CRUD  │  题目CRUD  │  批量导入/导出              │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 文档解析服务

#### 支持格式

| 格式 | 解析库 | 说明 |
|------|--------|------|
| .docx | python-docx | Word 2007+ |
| .doc | comtypes + win32api | 需Windows环境，转PDF处理 |
| .pdf | pdfplumber / PyPDF2 | 文本提取 |
| .txt | 内置open() | 按行读取，格式分隔 |
| .md | 内置open() | Markdown结构化 |
| .xlsx/.xls | openpyxl | Excel表格解析 |

#### 解析服务实现

```typescript
// document-parser.service.ts
@Injectable()
export class DocumentParserService {
  
  async parseDocument(file: Express.Multer.File): Promise<ParsedDocument> {
    const ext = path.extname(file.originalname).toLowerCase();
    
    switch (ext) {
      case '.docx':
        return this.parseDocx(file.buffer);
      case '.pdf':
        return this.parsePdf(file.buffer);
      case '.txt':
      case '.md':
        return this.parseText(file.buffer.toString('utf-8'));
      case '.xlsx':
      case '.xls':
        return this.parseExcel(file.buffer);
      default:
        throw new BadRequestException(`Unsupported format: ${ext}`);
    }
  }
  
  private async parseDocx(buffer: Buffer): Promise<ParsedDocument> {
    const bufferStream = new Readable();
    bufferStream.push(buffer);
    bufferStream.push(null);
    
    const docxParser = require('docx-parser');
    const text = await docxParser.parseXml(buffer);
    return { content: text, type: 'docx' };
  }
  
  private async parsePdf(buffer: Buffer): Promise<ParsedDocument> {
    const pdfParse = require('pdf-parse');
    const data = await pdfParse(buffer);
    return { content: data.text, type: 'pdf' };
  }
  
  private async parseText(content: string): Promise<ParsedDocument> {
    return { content, type: 'text' };
  }
  
  private async parseExcel(buffer: Buffer): Promise<ParsedDocument> {
    const XLSX = require('xlsx');
    const workbook = XLSX.read(buffer, { type: 'buffer' });
    const sheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[sheetName];
    const json = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
    return { content: JSON.stringify(json), type: 'excel' };
  }
}
```

### 6.3 AI分类与提取服务

#### 分类判断

```typescript
// ai-classifier.service.ts
interface ClassificationResult {
  type: 'knowledge' | 'question';
  confidence: number;
  reason: string;
}

@Injectable()
export class AIClassifierService {
  constructor(private zhipuProvider: ZhipuProvider) {}
  
  async classifyDocument(content: string): Promise<ClassificationResult> {
    const prompt = documentClassificationPrompt(content);
    const response = await this.zhipuProvider.complete(prompt);
    return JSON.parse(response);
  }
}

const documentClassificationPrompt = (content: string) => `
你是一个文档分类助手。请分析以下文档内容，判断是"精华知识点"还是"重点习题"。

文档内容：
---
${content.substring(0, 2000)}
---

分类标准：
- 精华知识点：包含概念定义、原理说明、术语解释等
- 重点习题：包含问题、选项、答案等

请输出JSON格式（不包含markdown代码块）：
{
  "type": "knowledge" | "question",
  "confidence": 0.0-1.0,
  "reason": "判断理由"
}
`;
```

#### 知识点提取

```typescript
// knowledge-extractor.service.ts
interface KnowledgePoint {
  title: string;
  chapter: string;
  summary: string;
  keyPoints: string[];
  difficulty: 1 | 2 | 3 | 4 | 5;
  relatedKnowledge: string[];
  feynmanMaterial: string;
}

@Injectable()
export class KnowledgeExtractorService {
  async extractKnowledge(content: string, chapter?: string): Promise<KnowledgePoint> {
    const prompt = knowledgeExtractionPrompt(content, chapter);
    const response = await this.zhipuProvider.complete(prompt);
    
    // 清理返回的JSON（处理可能的markdown格式）
    const cleaned = response.replace(/```json
?/g, '').replace(/```
?/g, '').trim();
    return JSON.parse(cleaned);
  }
}

const knowledgeExtractionPrompt = (content: string, chapter?: string) => `
你是一个知识点提取助手。请从以下文档中提取知识点信息。

文档内容：
---
${content.substring(0, 3000)}
---

${chapter ? `章节：${chapter}` : ''}

请提取JSON（不包含markdown代码块）：
{
  "title": "知识点标题",
  "chapter": "所属章节",
  "summary": "100字以内总结",
  "keyPoints": ["关键点1", "关键点2"],
  "difficulty": 1-5,
  "relatedKnowledge": ["相关知识点1"],
  "feynmanMaterial": "可用于费曼讲解的素材"
}
`;
```

#### 题目提取

```typescript
// question-extractor.service.ts
interface Question {
  type: 'single' | 'multiple' | 'judge';
  content: string;
  options: string[];
  answer: string;
  explanation: string;
  difficulty: 1 | 2 | 3 | 4 | 5;
  relatedKnowledge: string;
}

@Injectable()
export class QuestionExtractorService {
  async extractQuestions(content: string): Promise<Question[]> {
    const prompt = questionExtractionPrompt(content);
    const response = await this.zhipuProvider.complete(prompt);
    
    // 清理返回的JSON
    const cleaned = response.replace(/```json
?/g, '').replace(/```
?/g, '').trim();
    
    // 处理可能的数组格式
    const parsed = JSON.parse(cleaned);
    return Array.isArray(parsed) ? parsed : [parsed];
  }
}

const questionExtractionPrompt = (content: string) => `
你是一个题目提取助手。请从以下文档中提取题目信息。

文档内容：
---
${content.substring(0, 3000)}
---

请提取所有题目，每题输出JSON（不包含markdown代码块）：
{
  "type": "single" | "multiple" | "judge",
  "content": "题目内容",
  "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
  "answer": "B",
  "explanation": "答案解析",
  "difficulty": 1-5,
  "relatedKnowledge": "关联的知识点"
}

如果文档包含多个题目，请以JSON数组形式输出。
`;
```

### 6.4 题库管理API

#### 知识点管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `GET /api/knowledge` | 获取知识点列表 | 支持分页、筛选 |
| `GET /api/knowledge/:id` | 获取知识点详情 | 包含关联题目 |
| `POST /api/knowledge` | 新增知识点 | 手动创建 |
| `PUT /api/knowledge/:id` | 更新知识点 | 完整更新 |
| `PATCH /api/knowledge/:id` | 部分更新 | 字段级更新 |
| `DELETE /api/knowledge/:id` | 删除知识点 | 需确认关联题目 |
| `POST /api/knowledge/batch` | 批量导入 | Excel格式 |
| `GET /api/knowledge/export` | 批量导出 | Excel格式 |

#### 题目管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `GET /api/questions` | 获取题目列表 | 支持分页、筛选 |
| `GET /api/questions/:id` | 获取题目详情 | 包含解析 |
| `POST /api/questions` | 新增题目 | 手动创建 |
| `PUT /api/questions/:id` | 更新题目 | 完整更新 |
| `DELETE /api/questions/:id` | 删除题目 | 需确认 |
| `POST /api/questions/batch` | 批量导入 | Excel格式 |
| `GET /api/questions/export` | 批量导出 | Excel格式 |

### 6.5 数据库设计

#### 文档上传记录表 (document_upload)

```sql
CREATE TABLE `document_upload` (
  `id` VARCHAR(36) PRIMARY KEY,
  `filename` VARCHAR(255) NOT NULL,         -- 原始文件名
  `file_type` ENUM('docx','doc','pdf','txt','md','xlsx','xls'),
  `category` ENUM('knowledge','question') NOT NULL,
  `status` ENUM('pending','processing','completed','failed') DEFAULT 'pending',
  `ai_result` JSON,                          -- AI分类/提取结果
  `user_id` VARCHAR(36),
  `error_message` TEXT,
  `processed_count` INT DEFAULT 0,          -- 处理数量（知识点/题目数）
  `created_at` DATETIME DEFAULT NOW(),
  `updated_at` DATETIME DEFAULT NOW()
);
```

#### 知识库表 (knowledge_point)

```sql
CREATE TABLE `knowledge_point` (
  `id` VARCHAR(36) PRIMARY KEY,
  `title` VARCHAR(100) NOT NULL,             -- 知识点标题
  `chapter` VARCHAR(50),                      -- 所属章节
  `summary` TEXT,                           -- 摘要
  `content` TEXT,                           -- 详细内容
  `key_points` JSON,                        -- 关键点数组
  `feynman_material` TEXT,                   -- 费曼素材
  `difficulty` TINYINT DEFAULT 1,           -- 难度 1-5
  `source_document_id` VARCHAR(36),          -- 来源文档
  `status` ENUM('active','archived') DEFAULT 'active',
  `created_at` DATETIME DEFAULT NOW(),
  `updated_at` DATETIME DEFAULT NOW()
);
```

#### 题目表 (扩展question表)

```sql
-- 在原有question表基础上增加字段
ALTER TABLE `question` ADD COLUMN `source_document_id` VARCHAR(36) COMMENT '来源文档';
ALTER TABLE `question` ADD COLUMN `ai_explanation` TEXT COMMENT 'AI解析补充';
ALTER TABLE `question` ADD COLUMN `source_url` VARCHAR(500) COMMENT '来源URL';
```

### 6.6 题库上传流程

```
┌─────────────────────────────────────────────────────────────────┐
│                    题库上传完整流程                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  用户操作：                                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 1. 选择文档（支持拖拽）                                  │   │
│  │ 2. 选择分类：精华知识点 / 重点习题                        │   │
│  │ 3. 点击上传                                             │   │
│  │ 4. 等待AI处理（实时显示进度）                           │   │
│  │ 5. 预览处理结果                                         │   │
│  │ 6. 确认入库                                             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  后端处理：                                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ POST /api/question-bank/upload                          │   │
│  │                                                         │   │
│  │ 1. 保存文件到本地/云存储                                 │   │
│  │ 2. 创建 document_upload 记录（pending）                  │   │
│  │ 3. 异步任务队列处理：                                   │   │
│  │    a. 解析文档                                           │   │
│  │    b. AI分类判断                                         │   │
│  │    c. AI提取内容                                         │   │
│  │    d. 存储到数据库                                       │   │
│  │    e. 更新 document_upload 状态                          │   │
│  │ 4. WebSocket推送进度                                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 6.7 前端组件设计

```
src/
├── pages/
│   ├── question-bank/
│   │   ├── upload.vue          # 上传页面
│   │   ├── knowledge-list.vue  # 知识点列表
│   │   ├── question-list.vue   # 题目列表
│   │   └── import.vue          # 批量导入
│   │
│   └── admin/
│       └── question-bank.vue   # 管理后台
│
├── components/
│   ├── upload/
│   │   ├── UploadArea.vue      # 拖拽上传区
│   │   ├── UploadProgress.vue  # 上传进度
│   │   └── PreviewResult.vue   # 预览结果
│   │
│   └── question-bank/
│       ├── KnowledgeTable.vue  # 知识点表格
│       ├── QuestionTable.vue  # 题目表格
│       └── BatchImportModal.vue # 批量导入弹窗
│
└── services/
    └── questionBank.js         # API封装
```

---

## 六、部署架构

### 6.1 部署架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        腾讯云 VPC                           │
│                                                          │
│   ┌─────────────────────────────────────────────────┐   │
│   │              CVM 云服务器 (2核4G)                  │   │
│   │                                                 │   │
│   │   ┌─────────────┐    ┌─────────────┐            │   │
│   │   │  Nginx     │    │  NestJS API  │            │   │
│   │   │  反向代理   │───▶│  后端服务   │            │   │
│   │   │  + SSL    │    └──────┬──────┘            │   │
│   │   └─────────────┘           │                   │   │
│   │                              │                   │   │
│   └──────────────────────────────┼───────────────────┘   │
│                                  │                       │
│                    ┌─────────────┴─────────────┐         │
│                    │                         │         │
│                    ▼                         ▼         │
│            ┌──────────┐           ┌──────────┐      │
│            │  MySQL   │           │  Redis   │      │
│            │ 高可用版  │           │ 集群版   │      │
│            └──────────┘           └──────────┘      │
│                                                      │
└──────────────────────────────────────────────────────┘

前端部署：
┌─────────────────┐
│  静态资源 CDN   │  (ViteBuild产物)
└─────────────────┘
```

### 6.2 部署配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: ./backend
    container_name: ai-study-api
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DB_HOST=${DB_HOST}
      - DB_PORT=3306
      - DB_NAME=${DB_NAME}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - REDIS_HOST=${REDIS_HOST}
      - REDIS_PORT=6379
      - ZHIPU_API_KEY=${ZHIPU_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    restart: unless-stopped
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    container_name: ai-study-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./frontend/dist:/usr/share/nginx/html
    depends_on:
      - api
    restart: unless-stopped
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

### 6.3 环境变量

```bash
# .env.production
NODE_ENV=production

# 数据库
DB_HOST=rm-xxx.mysql.tencentcdb.com
DB_PORT=3306
DB_NAME=ai_study
DB_USER=ai_study_user
DB_PASSWORD=your_password

# Redis
REDIS_HOST=redis-xxx.tencentcdb.com
REDIS_PORT=6379

# AI API Keys
ZHIPU_API_KEY=your_zhipu_key
OPENAI_API_KEY=your_openai_key

# JWT
JWT_SECRET=your_jwt_secret
JWT_EXPIRES_IN=7d

# 微信小程序
WECHAT_APPID=your_appid
WECHAT_SECRET=your_secret
```

---

## 七、安全设计

### 7.1 接口安全

| 机制 | 说明 |
|------|------|
| JWT认证 | 所有API需携带token |
| 接口限流 | 每IP每分钟100次 |
| SQL注入防护 | 参数化查询 |
| XSS防护 | 输入过滤+输出编码 |
| CORS | 限制域名访问 |

### 7.2 AI安全

| 机制 | 说明 |
|------|------|
| 内容过滤 | 敏感词检测 |
| 输出审核 | AI回复合规检查 |
| 追问限制 | 单次对话最多20轮 |
| 话题限定 | 只回答学习相关 |

---

## 八、监控运维

### 8.1 监控指标

| 指标 | 告警阈值 |
|------|----------|
| API响应时间 | > 2s |
| AI生成时间 | > 10s |
| 错误率 | > 1% |
| WebSocket连接数 | > 1000 |

### 8.2 日志

```typescript
// 统一日志格式
{
  timestamp: '2026-05-05T00:00:00Z',
  level: 'info',
  traceId: 'uuid',
  userId: 'user-xxx',
  action: 'chat.send',
  duration: 1234,
  status: 200
}
```

---

## 九、开发计划

### 阶段一：MVP（1-2周）

| 任务 | 工期 | 交付 |
|------|------|------|
| 项目初始化 | 1天 | 前后端框架搭建 |
| 数据库设计 | 1天 | 表结构+初始化SQL |
| AI服务接入 | 2天 | 智谱API对接 |
| 费曼讲解功能 | 2天 | 核心对话流程 |
| 苏格拉底追问 | 2天 | 追问逻辑实现 |
| 题目练习功能 | 2天 | 答题+解析流程 |

### 阶段二：功能完善（1周）

| 任务 | 工期 | 交付 |
|------|------|------|
| 进度追踪 | 2天 | 积分/连胜/等级 |
| 错题本 | 1天 | 错题收集+复习 |
| 知识库管理 | 1天 | 管理员后台 |
| 部署上线 | 1天 | 生产环境 |

### 阶段三：体验优化（持续）

- 多AI模型切换
- 用户体验优化
- 题库扩充
- 历年真题接入

---

## 十、成本估算

### 10.1 腾讯云月度成本

| 资源 | 规格 | 月费 |
|------|------|------|
| CVM | 2核4G | ¥150 |
| MySQL | 2核4G高可用 | ¥200 |
| Redis | 2G集群 | ¥100 |
| CDN | 50GB流量 | ¥30 |
| 域名+SSL | - | ¥10 |
| **总计** | - | **¥490/月** |

### 10.2 AI API成本

| 模型 | 调用量 | 月费估算 |
|------|--------|---------|
| 智谱GLM-4 | 1000次/天 | ¥200 |
| GPT-4 | 300次/天 | ¥300 |
| **总计** | - | **¥500/月** |

---

_文档版本：v1.2 | 最后更新：2026-05-07_
_作者：1902 🦞_
