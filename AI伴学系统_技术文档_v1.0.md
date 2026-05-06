# AI伴学系统 - 产品技术文档

> 📅 文档版本：v1.6 | 日期：2026-05-05
> 👤 开发者：1902
> 🎯 基于：PRD v1.5

---

## 一、系统概述

### 1.1 项目背景

基于PRD文档，AI伴学系统旨在通过**费曼学习法 + 苏格拉底提问法**，为用户提供"懂教学法"的AI私教体验，彻底弄懂每一个知识点。

**核心技术变更（v1.5）**：
- AI模型：MiniMax code-plan
- 数据库：SQLite（轻量级文件型）
- 飞书机器人：学习提醒与督促
- 题库系统：PDF导入 + AI解析

### 1.2 技术目标

| 目标 | 说明 |
|------|------|
| 飞书为主 | 以飞书机器人为核心交互平台 |
| 轻量部署 | SQLite本地数据库，降低部署复杂度 |
| AI驱动 | MiniMax code-plan 提供智能交互 |
| PDF题库 | 支持PDF文件导入，自动解析题目 |
| 多用户支持 | 预留user_id字段，后续可平滑升级多用户 |

### 1.3 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      多用户端                                │
├────────────┬────────────┬────────────┬──────────────────────┤
│  用户A     │  用户B     │  用户C     │       ...           │
│  飞书机器人 │  飞书机器人 │  飞书机器人 │                      │
└──────┬─────┴─────┬─────┴─────┬─────┴──────────────────────┘
       │           │           │
       └───────────┴─────┬─────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    AI伴学系统后端                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              飞书开放平台                            │   │
│  │  机器人 / 定时消息 / 卡片消息 / 事件订阅            │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                 │
│                          ▼                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  学习引擎  │  │  题目服务   │  │  计划服务   │        │
│  │  费曼讲解  │  │  PDF解析    │  │  定时提醒   │        │
│  │  苏格拉底  │  │  AI出题    │  │  督促消息   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                          │                                 │
│                          ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              SQLite 数据库                          │   │
│  │  ┌─────────┐ ┌─────────────┐ ┌─────────────────┐  │   │
│  │  │ users   │ │ questions   │ │ study_records   │  │   │
│  │  │用户表   │ │ 题目表      │ │ 学习记录表      │  │   │
│  │  └─────────┘ └─────────────┘ └─────────────────┘  │   │
│  │  ※ 所有业务表含 user_id 字段，支持多用户隔离      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              MiniMax code-plan AI                  │   │
│  │  费曼讲解 / 苏格拉底追问 / PDF解析 / 题目生成       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 二、技术选型

### 2.1 前端技术栈

| 组件 | 选型 | 理由 |
|------|------|------|
| **对话平台** | 飞书 | 用户主力平台，机器人交互 |
| **机器人配置** | 飞书自建应用 | 定时消息、卡片消息、事件订阅 |
| **消息卡片** | 飞书交互卡片 | 按钮、选择器等交互能力 |

### 2.2 后端技术栈

| 组件 | 选型 | 理由 |
|------|------|------|
| **Runtime** | Python 3.10+ | AI/数据处理生态丰富 |
| **数据库** | SQLite | 轻量级，文件型，无需安装 |
| **AI SDK** | MiniMax API | code-plan模型支持 |
| **定时任务** | APScheduler / 飞书定时消息 | 学习提醒 |
| **PDF解析** | PyMuPDF + MiniMax | 文本提取 + AI解析 |

### 2.3 AI模型选型

| 模型 | 场景 | 特点 |
|------|------|------|
| **MiniMax code-plan** | 全部AI能力 | 费曼讲解/苏格拉底追问/PDF解析/出题 |

---

## 三、数据库设计

### 3.1 数据库文件结构

```
database/
├── questions.db          # 主数据库
├── backup/               # 备份
└── export/               # 导出
```

### 3.2 多用户支持设计

> 💡 设计原则：单用户 → 多用户 无需重构，只需迁移数据

**当前（单用户）**：SQLite文件型数据库，本地存储
**未来（多用户）**：可平滑迁移至 MySQL/PostgreSQL，只需修改连接配置

**多用户升级路径**：
1. 用户表添加 `openid/union_id` 字段对接飞书用户
2. 所有业务表添加 `user_id` 字段
3. 数据库连接池配置替代单文件连接
4. Redis缓存替代本地缓存（会话共享）

### 3.3 数据表结构

#### users（用户表）

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feishu_openid TEXT UNIQUE,                -- 飞书用户唯一标识
    feishu_union_id TEXT,                      -- 飞书Union ID（跨应用使用）
    nickname VARCHAR(50),                     -- 昵称
    avatar VARCHAR(255),                      -- 头像
    level INTEGER DEFAULT 1,                  -- 学习等级
    score INTEGER DEFAULT 0,                   -- 总积分
    streak INTEGER DEFAULT 0,                  -- 连续学习天数
    streak_last_date DATE,                     -- 最后学习日期
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### questions（题目表）

```sql
CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,                    -- single/multiple/judge/fill/short
    content TEXT NOT NULL,                 -- 题目内容
    options TEXT,                          -- JSON: {"A":"...","B":"...","C":"...","D":"..."}
    answer TEXT NOT NULL,                  -- 答案
    analysis TEXT,                          -- 解析
    knowledge_point TEXT,                   -- 知识点标签，多个用逗号分隔
    difficulty INTEGER DEFAULT 1,          -- 难度1-5
    source TEXT,                           -- 来源（如：2024年真题）
    source_file TEXT,                       -- 来源文件名
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'pending'         -- pending/approved/disabled
);
```

#### knowledge_points（知识点表）

```sql
CREATE TABLE knowledge_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,             -- 编码：1.1, 1.2.1
    name TEXT NOT NULL,                    -- 知识点名称
    chapter TEXT,                          -- 章节
    stage TEXT,                            -- 所属阶段
    sort_order INTEGER,                    -- 排序
    status TEXT DEFAULT 'locked',         -- locked/unlocked/completed
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### study_plans（学习计划表）

```sql
CREATE TABLE study_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,                  -- 用户ID
    name TEXT NOT NULL,                        -- 计划名称
    daily_goal TEXT,                          -- 每日目标
    preferred_time TEXT,                      -- 偏好时间（如：09:00, 20:00）
    reminder_enabled INTEGER DEFAULT 1,       -- 是否开启提醒
    reminder_times TEXT,                       -- JSON: ["09:00","20:00"]
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

#### reminder_rules（提醒规则表）

```sql
CREATE TABLE reminder_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,                           -- 用户ID（为空表示全局规则）
    type TEXT NOT NULL,                       -- schedule/督促/milestone
    trigger_time TEXT,                        -- 触发时间
    message_template TEXT,                    -- 消息模板
    enabled INTEGER DEFAULT 1,                 -- 是否启用
    condition TEXT,                            -- JSON: 触发条件
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

#### study_records（学习记录表）

```sql
CREATE TABLE study_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,                  -- 用户ID
    knowledge_point_id INTEGER,
    learned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    duration INTEGER,                          -- 学习时长（分钟）
    questions_done INTEGER DEFAULT 0,          -- 完成题数
    correct_count INTEGER DEFAULT 0,           -- 答对题数
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_points(id)
);
```

#### answer_records（答题记录表）

```sql
CREATE TABLE answer_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,                  -- 用户ID
    question_id INTEGER,
    user_answer TEXT,
    is_correct INTEGER,
    answered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_first_attempt INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (question_id) REFERENCES questions(id)
);
```

#### wrong_questions（错题本表）

```sql
CREATE TABLE wrong_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,                  -- 用户ID
    question_id INTEGER,
    wrong_count INTEGER DEFAULT 1,
    last_wrong_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    mastered INTEGER DEFAULT 0,                -- 是否已掌握
    mastered_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (question_id) REFERENCES questions(id)
);
```

#### user_sessions（用户会话表）

```sql
CREATE TABLE user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,                  -- 用户ID
    session_id TEXT NOT NULL,                  -- 会话UUID
    knowledge_point_id INTEGER,                -- 当前知识点
    mode TEXT DEFAULT 'feynman',              -- feynman/socratic/practice
    messages TEXT,                            -- JSON: 历史消息
    status TEXT DEFAULT 'active',             -- active/completed
    started_at DATETIME,
    completed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_points(id)
);
```

---

## 四、项目结构

```
backend/
├── src/
│   ├── main.py                    # 入口
│   │
│   ├── config/
│   │   └── settings.py           # 配置
│   │
│   ├── modules/
│   │   ├── feishu/               # 飞书机器人模块
│   │   │   ├── bot.py            # 机器人主逻辑
│   │   │   ├── handlers/        # 消息处理器
│   │   │   │   ├── command.py   # 命令处理
│   │   │   │   ├── chat.py      # 对话处理
│   │   │   │   └── schedule.py  # 定时任务
│   │   │   └── cards/           # 卡片模板
│   │   │
│   │   ├── ai/                  # AI服务模块
│   │   │   ├── service.py       # AI服务
│   │   │   ├── feynman.py       # 费曼讲解
│   │   │   ├── socratic.py      # 苏格拉底追问
│   │   │   └── pdf_parser.py    # PDF解析
│   │   │
│   │   ├── question/            # 题库模块
│   │   │   ├── service.py       # 题库服务
│   │   │   ├── repository.py    # 数据访问
│   │   │   └── generator.py     # AI出题
│   │   │
│   │   ├── knowledge/           # 知识库模块
│   │   │   ├── service.py
│   │   │   └── repository.py
│   │   │
│   │   └── study/               # 学习模块
│   │       ├── service.py       # 学习服务
│   │       ├── progress.py      # 进度管理
│   │       └── reminder.py      # 提醒服务
│   │
│   ├── database/
│   │   ├── db.py               # 数据库连接
│   │   └── migrations/         # 迁移脚本
│   │
│   └── prompts/
│       ├── feynman.txt         # 费曼提示词
│       ├── socratic.txt        # 苏格拉底提示词
│       └── explanation.txt      # 解析提示词
│
├── requirements.txt
└── run.py
```

---

## 五、飞书机器人设计

### 5.1 机器人能力

| 能力 | 说明 |
|------|------|
| **命令处理** | 接收用户命令（设置学习计划、查看进度等） |
| **定时消息** | 每日学习提醒 |
| **卡片消息** | 交互式消息卡片 |
| **事件订阅** | 接收用户消息、被@事件 |

### 5.2 命令设计

| 命令 | 功能 |
|------|------|
| `设置学习计划` | 配置每日学习目标和时间 |
| `添加提醒` | 设置特定时间点提醒 |
| `查看计划` | 显示当前学习计划 |
| `查看进度` | 查询学习进度 |
| `错题本` | 查看错题列表 |
| `跳过` | 跳过当前提醒 |
| `help` | 显示所有命令 |

### 5.3 消息卡片模板

#### 学习提醒卡片

```json
{
  "msg_type": "interactive",
  "card": {
    "header": {
      "title": {"tag": "plain_text", "content": "📚 AI伴学助手 - 学习提醒"},
      "template": "blue"
    },
    "elements": [
      {"tag": "markdown", "content": "⏰ 上午9:00 学习时间到！"},
      {"tag": "markdown", "content": "**今日任务**\n• 1.2 指令系统\n• 预计学习时长：15分钟"},
      {"tag": "action", "actions": [
        {"tag": "button", "text": {"tag": "plain_text", "content": "立即开始学习 ➤"}, "type": "primary"},
        {"tag": "button", "text": {"tag": "plain_text", "content": "稍后提醒我"}, "type": "default"}
      ]}
    ]
  }
}
```

### 5.4 飞书配置步骤

| 步骤 | 操作 |
|------|------|
| 1 | 在[飞书开放平台](https://open.feishu.cn/)创建自建应用 |
| 2 | 开通机器人能力，开启「消息」和「定时消息」权限 |
| 3 | 配置事件订阅：im.message.receive_v1 |
| 4 | 开发后端服务，配置webhook事件接收 |
| 5 | 测试并部署 |

---

## 六、AI服务设计

### 6.1 AI服务架构

```python
# ai/service.py
class AIService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "MiniMax code-plan"

    # 费曼讲解
    async def feynman_explain(self, knowledge: dict) -> str:
        prompt = self._build_feynman_prompt(knowledge)
        return await self._call_model(prompt)

    # 苏格拉底追问
    async def socratic_question(self, context: dict, user_answer: str) -> str:
        prompt = self._build_socratic_prompt(context, user_answer)
        return await self._call_model(prompt)

    # PDF解析
    async def parse_pdf(self, text: str) -> list:
        prompt = self._build_pdf_parse_prompt(text)
        return await self._call_model(prompt)

    # AI出题
    async def generate_questions(self, knowledge: dict, count: int = 5) -> list:
        prompt = self._build_question_gen_prompt(knowledge, count)
        return await self._call_model(prompt)
```

### 6.2 提示词模板

#### 费曼讲解提示词

```
你是AI学习助手，擅长用费曼学习法讲解知识点。
费曼学习法的核心是：用最简单的话把概念讲清楚，让8岁小孩都能听懂。

请用费曼学习法讲解以下知识点：

---
主题：{title}
内容：{content}
---

讲解要求：
1. 先用一个生活化的类比引入（用常见的场景解释）
2. 解释核心概念（不超3句话）
3. 举1-2个生活中的例子
4. 用"如果...会怎样"引导思考
```

#### 苏格拉底追问提示词

```
你是AI学习助手，擅长用苏格拉底提问法引导学生思考。
苏格拉底法的核心：不直接给答案，通过连续追问让学生自己发现答案。

当前情境：
- 知识点：{knowledge}
- AI的问题：{question}
- 学生的回答：{answer}

请根据学生的回答，给出追问或反馈：
1. 如果回答正确 → 给予肯定，追问更深层问题
2. 如果回答部分正确 → 指出模糊点，追问澄清
3. 如果回答错误 → 不直接否定，用问题引导
```

#### PDF题目解析提示词

```
请从以下文本中提取题目信息，返回JSON数组格式：

---
{text}
---

返回格式：
[
  {
    "type": "single/multi/judge/fill",
    "content": "题目内容",
    "options": {"A": "选项A", "B": "选项B", ...},
    "answer": "答案",
    "analysis": "解析（如果有）"
  }
]
```

### 6.3 MiniMax API调用

```python
# ai/client.py
import aiohttp

class MiniMaxClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.minimax.chat/v1"

    async def chat(self, prompt: str, stream: bool = True) -> str:
        payload = {
            "model": "MiniMax-Text-01",
            "messages": [{"role": "user", "content": prompt}],
            "stream": stream
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        # 调用API并返回结果
```

---

## 七、PDF题库导入

### 7.1 处理流程

```
用户上传PDF
    │
    ▼
PyMuPDF文本提取
    │
    ▼
MiniMax AI解析
    │ 识别题目、选项、答案、解析
    ▼
题目数据结构化
    │ 存入SQLite
    ▼
人工校对确认
    │
    ▼
题目入库完成
```

### 7.2 PDF解析规则

| 规则 | 说明 |
|------|------|
| 题目识别 | 以序号开头（1.、2.、一、）识别为题目 |
| 选项识别 | 以A/B/C/D或（1）（2）开头识别为选项 |
| 答案识别 | 关键词："答案："、"正确答案是"、"[答案]" |
| 解析识别 | 关键词："解析："、"分析：" |

### 7.3 支持题型

| 题型 | 支持状态 |
|------|----------|
| 单项选择题 | ✅ |
| 多项选择题 | ✅ |
| 判断题 | ✅ |
| 填空题 | ✅ |
| 简答题 | ⚠️ 部分支持 |

---

## 八、部署架构

### 8.1 部署架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        本地环境 / Serverless                 │
│                                                          │
│   ┌─────────────────────────────────────────────────┐   │
│   │              Python 后端服务                      │   │
│   │                                                 │   │
│   │   ┌─────────────┐    ┌─────────────┐            │   │
│   │   │  飞书机器人 │    │  AI服务     │            │   │
│   │   │  消息处理   │    │  MiniMax   │            │   │
│   │   └─────────────┘    └─────────────┘            │   │
│   │                                                 │   │
│   │   ┌─────────────────────────────────────┐      │   │
│   │   │  SQLite 数据库 (questions.db)         │      │   │
│   │   └─────────────────────────────────────┘      │   │
│   │                                                 │   │
│   └─────────────────────────────────────────────────┘   │
│                                                          │
└─────────────────────────────────────────────────────────────┘
```

### 8.2 部署配置

```yaml
# config.yaml
app:
  host: 0.0.0.0
  port: 8081

feishu:
  app_id: your_app_id
  app_secret: your_app_secret
  bot_name: AI伴学助手

database:
  path: ./database/questions.db

ai:
  api_key: your_minimax_api_key
  model: MiniMax-Text-01

reminder:
  default_times:
    - "09:00"
    - "20:00"
```

### 8.3 环境变量

```bash
# .env
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret
MINIMAX_API_KEY=your_api_key
DATABASE_PATH=./database/questions.db
```

---

## 九、安全设计

### 9.1 接口安全

| 机制 | 说明 |
|------|------|
| 飞书签名验证 | 校验请求来源 |
| 命令白名单 | 只处理预定义命令 |
| 内容过滤 | AI输出合规检查 |
| 追问限制 | 单次对话最多20轮 |

### 9.2 数据安全

| 机制 | 说明 |
|------|------|
| 数据库文件 | 本地存储，定期备份 |
| 敏感信息 | API密钥通过环境变量配置 |

---

## 十、开发计划

### 阶段一：MVP（1-2周）

| 任务 | 工期 | 交付 |
|------|------|------|
| 项目初始化 | 1天 | Python项目搭建 |
| 数据库设计 | 1天 | SQLite表结构 |
| 飞书机器人 | 2天 | 机器人配置+消息处理 |
| AI服务接入 | 2天 | MiniMax API对接 |
| 费曼讲解功能 | 2天 | 核心对话流程 |
| 苏格拉底追问 | 2天 | 追问逻辑实现 |
| 题目练习功能 | 2天 | 答题+解析流程 |

### 阶段二：功能完善（1周）

| 任务 | 工期 | 交付 |
|------|------|------|
| 学习提醒 | 2天 | 定时任务+飞书推送 |
| 进度追踪 | 1天 | 积分/连胜/等级 |
| 错题本 | 1天 | 错题收集+复习 |
| PDF导入 | 2天 | 题库导入功能 |

### 阶段三：体验优化（持续）

- 题库扩充
- 历年真题接入
- 学习报告优化

---

## 十一、成本估算

### 11.1 基础成本

| 资源 | 选型 | 月费 |
|------|------|------|
| 托管 | Serverless / 本地 | ¥0-100 |
| 数据库 | SQLite本地 | ¥0 |
| AI调用 | MiniMax按量计费 | ¥100-300/月 |

### 11.2 AI调用估算

| 场景 | 调用量 | 估算费用 |
|------|--------|----------|
| 费曼讲解 | 45次/天 × 30 | ¥50 |
| 苏格拉底追问 | 100次/天 × 30 | ¥80 |
| PDF解析 | 1次/天 × 30 | ¥30 |
| AI出题 | 5次/天 × 30 | ¥40 |
| **总计** | - | **¥200/月** |

---

_文档版本：v1.6 | 最后更新：2026-05-05_
_作者：1902 🦞_
