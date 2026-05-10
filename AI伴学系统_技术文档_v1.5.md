# AI伴学系统 - 产品技术文档

> 📅 文档版本：v1.6（新增用户管理模块 + 题库上传进度） | 日期：2026-05-10
> 👤 开发者：1902
> 🎯 基于：PRD v1.6

---

## 一、系统概述

### 1.1 项目背景

基于PRD文档，AI伴学系统旨在通过**费曼学习法 + 苏格拉底提问法**，为用户提供"懂教学法"的AI私教体验，彻底弄懂每一个知识点。

**核心技术变更（v1.5）**：
- AI模型：MiniMax code-plan
- 数据库：SQLite（轻量级文件型）
- 交互界面：H5页面（手机浏览器直接访问）
- 通知推送：飞书机器人（定时提醒、督促消息、成就通知）
- 题库系统：文档导入（PDF/Word/Excel/TXT/Markdown） + AI解析

### 1.2 技术目标

| 目标 | 说明 |
|------|------|
| H5交互 | H5页面作为学习交互界面，手机浏览器直接访问 |
| 飞书通知 | 飞书机器人作为通知推送渠道，消息内嵌H5跳转链接 |
| 轻量部署 | SQLite本地数据库，降低部署复杂度 |
| AI驱动 | MiniMax code-plan 提供智能交互 |
| 多格式题库 | 支持PDF/Word/Excel/TXT/Markdown导入，AI自动解析 |
| 多用户支持 | 预留user_id字段，后续可平滑升级多用户 |

### 1.3 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      多用户端                                │
├──────────────────────┬──────────────────────────────────────┤
│  H5页面（交互界面）  │  飞书机器人（通知渠道）              │
│  手机浏览器直接访问  │  定时提醒/督促/成就通知              │
│  学习地图/AI对话/    │  消息内嵌H5跳转链接                  │
│  题目练习/错题本     │  点击链接→跳转H5页面                 │
└──────────┬───────────┴──────────┬───────────────────────────┘
           │                      │
           └──────────┬───────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    AI伴学系统后端                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              交互层                                  │   │
│  │  H5前端托管  │  飞书开放平台                         │   │
│  │  RESTful API │  机器人 / 卡片消息 / 事件订阅         │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                 │
│                          ▼                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  学习引擎  │  │  题目服务   │  │  计划服务   │        │
│  │  费曼讲解  │  │  文档解析   │  │  定时提醒   │        │
│  │  苏格拉底  │  │  AI出题    │  │  飞书推送   │        │
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
│  │  费曼讲解 / 苏格拉底追问 / 文档解析 / 题目生成     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 二、技术选型

### 2.1 前端技术栈

| 组件 | 选型 | 理由 |
|------|------|------|
| **交互界面** | H5页面 | 手机浏览器直接访问，无需安装 |
| **H5框架** | Vue 3 / React | 移动端H5页面构建 |
| **UI组件库** | Vant / Ant Design Mobile | 移动端UI组件 |
| **通知推送** | 飞书机器人 | 定时提醒、督促消息、成就通知 |
| **消息卡片** | 飞书交互卡片 | 按钮、选择器，内嵌H5跳转链接 |

### 2.2 后端技术栈

| 组件 | 选型 | 理由 |
|------|------|------|
| **Runtime** | Python 3.10+ | AI/数据处理生态丰富 |
| **Web框架** | FastAPI / Flask | RESTful API + H5静态资源托管 |
| **数据库** | SQLite | 轻量级，文件型，无需安装 |
| **AI SDK** | MiniMax API | code-plan模型支持 |
| **定时任务** | APScheduler | 后端Cron定时触发 |
| **飞书SDK** | 飞书开放平台SDK | 消息推送、事件订阅 |
| **文档解析** | python-docx / pdfplumber / openpyxl | 多格式文档解析 |

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
    username VARCHAR(50) UNIQUE NOT NULL,        -- 用户名（登录用）
    password_hash VARCHAR(255) NOT NULL,         -- 密码哈希
    nickname VARCHAR(50),                        -- 昵称（显示用）
    avatar VARCHAR(255),                          -- 头像
    email VARCHAR(255),                          -- 邮箱
    role VARCHAR(20) DEFAULT 'user',            -- 角色：user/admin
    permissions TEXT,                         -- JSON：功能权限列表
    status VARCHAR(20) DEFAULT 'active',      -- 状态：active/banned
    level INTEGER DEFAULT 1,                  -- 学习等级
    score INTEGER DEFAULT 0,                  -- 总积分
    streak INTEGER DEFAULT 0,                 -- 连续学习天数
    streak_last_date DATE,                     -- 最后学习日期
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### user_permissions（用户权限表）

```sql
CREATE TABLE user_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,                  -- 用户ID
    module VARCHAR(50) NOT NULL,               -- 功能模块
    granted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    granted_by INTEGER,                        -- 授权人ID（管理员）
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, module)
);
```

#### upload_progress（上传进度表）

```sql
CREATE TABLE upload_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,                  -- 用户ID
    file_name VARCHAR(255),                     -- 文件名
    file_size INTEGER,                          -- 文件大小（字节）
    status VARCHAR(20) DEFAULT 'pending',     -- pending/processing/completed/failed
    progress INTEGER DEFAULT 0,                 -- 进度 0-100
    stage VARCHAR(50),                          -- 当前阶段
    total_questions INTEGER DEFAULT 0,            -- 总题目数
    processed_questions INTEGER DEFAULT 0,     -- 已处理题目数
    error_message TEXT,                         -- 错误信息
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
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
    feishu_chat_id TEXT,                       -- 飞书群聊/私聊ID（用于推送）
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
    message_template TEXT,                    -- 消息模板（含H5链接占位符）
    h5_url_template TEXT,                     -- H5跳转链接模板
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
│   │   ├── feishu/               # 飞书通知模块
│   │   │   ├── bot.py            # 机器人主逻辑
│   │   │   ├── handlers/        # 消息处理器
│   │   │   │   ├── command.py   # 命令处理
│   │   │   │   ├── chat.py      # 对话处理
│   │   │   │   └── schedule.py  # 定时任务
│   │   │   └── cards/           # 卡片模板（含H5链接）
│   │   │
│   │   ├── ai/                  # AI服务模块
│   │   │   ├── service.py       # AI服务
│   │   │   ├── feynman.py       # 费曼讲解
│   │   │   ├── socratic.py      # 苏格拉底追问
│   │   │   └── pdf_parser.py    # 文档解析
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
│   │       └── reminder.py      # 提醒服务（飞书推送）
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

frontend/                         # H5前端（手机浏览器交互界面）
├── src/
│   ├── views/
│   │   ├── Map.vue             # 学习地图页
│   │   ├── Learn.vue           # 知识点学习页（AI解答/帮测）
│   │   ├── Practice.vue        # 题目练习页
│   │   ├── WrongBook.vue       # 错题本页
│   │   ├── Report.vue          # 学习报告页
│   │   └── Admin.vue           # 题库管理页
│   ├── components/
│   │   ├── ChatBubble.vue      # AI对话气泡
│   │   ├── QuestionCard.vue    # 题目卡片
│   │   └── ProgressBar.vue     # 进度条
│   └── router/
│       └── index.js            # 路由配置
├── dist/                        # 构建产物（托管到CDN）
└── package.json
```

---

## 五、学习地图与核心功能模块

### 5.1 学习地图模块

#### 数据模型

```python
# models/knowledge.py

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Chapter:
    id: str
    title: str              # "第一章：计算机基础"
    order: int               # 排序
    sections: list = field(default_factory=list)  # 包含的知识节

@dataclass
class Section:
    id: str
    chapter_id: str
    title: str              # "1.1 存储系统"
    order: int
    knowledge_points: list = field(default_factory=list)

@dataclass
class KnowledgePoint:
    id: str
    section_id: str
    title: str              # "Cache（高速缓存存储器）"
    official_content: str   # 官方教材内容
    status: str             # locked / in_progress / completed
    mastery_level: int      # 掌握度 0-100
    order: int
    next_point_id: Optional[str] = None  # 下一知识点ID
```

#### API设计

| 接口 | 方法 | 说明 |
|------|------|------|
| `GET /api/study-map` | 获取学习地图 | 全量章节+知识点树 |
| `GET /api/study-map/chapter/<id>` | 获取章节详情 | 章节下知识点列表 |
| `GET /api/study-map/point/<id>` | 获取知识点详情 | 包含官方内容 |
| `POST /api/study-map/unlock` | 解锁知识点 | 前置知识点达标后 |
| `PUT /api/study-map/mastery` | 更新掌握度 | AI帮测后更新 |

#### 状态管理

```python
# store/study_map.py

study_map_state = {
    "chapters": [],                    # 章节树
    "current_chapter": None,           # 当前章节
    "current_point": None,             # 当前知识点
    "expanded_sections": [],           # 展开的章节ID列表
    "mastery_levels": {},              # { point_id: mastery_level }
    "unlocked_points": []              # 已解锁知识点ID列表
}
```

### 5.2 AI解答模块

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

```python
def build_feynman_prompt(knowledge: dict, user_question: str = None) -> str:
    """构建费曼讲解提示词"""
    base = f"""你是大王的学习助手，擅长用费曼学习法解答疑问。

【知识点】
标题：{knowledge['title']}
官方内容：{knowledge['official_content']}
"""
    if user_question:
        base += f"""
【用户提问】{user_question}

解答格式：
🤖 【AI解答】
[直接回应疑问]
[类比解释]
[回到核心概念]
[引导思考]
"""
    else:
        base += """
【任务】请先用费曼法讲解这个知识点

首次讲解格式：
📚 【费曼讲解】{title}

[类比引入] - 用生活场景开始
[核心解释] - 简洁明了
[生活例子] - 1-2个例子
[思考引导] - 抛出问题让用户思考
"""
    base += """
费曼学习法原则：
1. 用最简单的话讲清楚，让8岁小孩都能听懂
2. 用生活化类比解释抽象概念
3. 层层递进，从已知到未知
4. 最后引导用户自己总结
"""
    return base
```

### 5.3 AI帮测模块

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

```python
# modules/ai/socratic.py

MASTERY_SCORES = {
    "excellent": 25,    # 完全正确+理解到位
    "good": 15,         # 正确但理解一般
    "fair": 8,          # 部分正确
    "poor": 5,          # 方向对但细节错
    "wrong": 0          # 完全不对
}

UNLOCK_THRESHOLD = 90  # 解锁阈值 90%
MAX_QUESTIONS = 5      # 最大题目数
```

#### 苏格拉底提问策略

```python
# modules/ai/socratic.py

SOCRATIC_LEVELS = [
    "事实性问题（是什么）",
    "理解性问题（为什么）",
    "应用性问题（怎么样）",
    "分析性问题（与其他知识的关系）",
    "评价性问题（你的看法）"
]

def get_question_level(question_number: int) -> str:
    """根据题目序号选择不同层次的问题"""
    # Q1: Level 1 (事实) → Q2: Level 2 (理解) → ...
    index = min(question_number - 1, len(SOCRATIC_LEVELS) - 1)
    return SOCRATIC_LEVELS[index]
```

#### Prompt模板

```python
def build_socratic_prompt(
    knowledge: dict,
    user_answer: str = None,
    question_number: int = 1,
    total_mastery: int = 0
) -> str:
    """构建苏格拉底提问提示词"""
    base = f"""你是大王的学习助手，擅长用苏格拉底提问法测试学习效果。

【当前知识点】{knowledge['title']}
【核心要点】{knowledge.get('key_points', '')}
【官方内容】{knowledge['official_content']}
【当前累计掌握度】{total_mastery}%
"""
    if user_answer:
        base += f"""
【用户回答】{user_answer}
请评价回答质量并决定下一问题。
"""
    else:
        base += f"""
【任务】开始苏格拉底提问测试。问第1个问题（Level 1：事实性问题）。
"""
    base += """
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

输出格式：
🤔 【苏格拉底提问】
❓ 问题{question_number}/5：
[问题内容]

[等待用户回答后，输出评价和下一问题或最终判定]
"""
    return base
```

### 5.4 知识点解锁模块

#### 解锁规则

| 条件 | 结果 |
|------|------|
| 知识点掌握度 ≥ 90% | 自动解锁下一知识点 |
| 章节内所有知识点完成 | 自动解锁下一章节 |
| 前置知识点未达标 | 保持锁定状态 |

#### 解锁流程

```python
# modules/knowledge/unlock.py

async def unlock_next_point(current_point_id: str):
    """解锁下一知识点"""
    current = await get_knowledge_point(current_point_id)

    # 检查是否达到解锁条件
    if current.mastery_level >= UNLOCK_THRESHOLD:
        # 解锁下一知识点
        if current.next_point_id:
            await update_point_status(current.next_point_id, 'in_progress')
            await notify_user(f"🎉 已解锁新知识点：{current.next_title}")

        # 检查章节是否完成
        section_points = await get_section_points(current.section_id)
        all_completed = all(p.status == 'completed' for p in section_points)
        if all_completed:
            await unlock_next_section(current.section_id)
```

---

## 六、飞书通知与H5跳转设计

### 6.1 设计思路

采用**飞书通知 + H5交互**的混合架构：
- **飞书**：作为通知推送渠道，负责定时提醒、督促消息、成就通知
- **H5页面**：作为学习交互界面，负责费曼讲解、苏格拉底追问、题目练习等
- 用户在飞书中收到提醒消息 → 点击链接 → 跳转到H5页面开始学习

### 6.2 机器人能力

| 能力 | 说明 |
|------|------|
| **定时推送** | 每日学习提醒，消息内嵌H5跳转链接 |
| **卡片消息** | 交互式卡片，按钮直接跳转H5页面 |
| **事件订阅** | 接收用户消息、被@事件（用于跳转H5） |

### 6.3 飞书消息卡片模板

#### 学习提醒卡片（含H5链接）

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
      {"tag": "markdown", "content": "**今日任务**\n• 1.2 指令系统\n• 预计学习时长：15分钟\n• 已连续学习：2天"},
      {"tag": "action", "actions": [
        {"tag": "button", "text": {"tag": "plain_text", "content": "开始学习 ➤"}, "type": "primary", "url": "https://h5.aistudy.com/learn?point=1.2&tab=feynman"},
        {"tag": "button", "text": {"tag": "plain_text", "content": "稍后提醒我"}, "type": "default"}
      ]}
    ]
  }
}
```

#### 督促提醒卡片（含H5链接）

```json
{
  "msg_type": "interactive",
  "card": {
    "header": {
      "title": {"tag": "plain_text", "content": "🔥 督促提醒"},
      "template": "orange"
    },
    "elements": [
      {"tag": "markdown", "content": "嘿~ 上午10点了！"},
      {"tag": "markdown", "content": "**今日待办**\n• 1.2 指令系统（未开始）\n• 昨日错题复习（2道待巩固）"},
      {"tag": "action", "actions": [
        {"tag": "button", "text": {"tag": "plain_text", "content": "去学习新内容 ➤"}, "type": "primary", "url": "https://h5.aistudy.com/learn?point=1.2&tab=feynman"},
        {"tag": "button", "text": {"tag": "plain_text", "content": "先复习错题 ➤"}, "type": "default", "url": "https://h5.aistudy.com/wrong"}
      ]}
    ]
  }
}
```

#### 里程碑庆祝卡片（含H5链接）

```json
{
  "msg_type": "interactive",
  "card": {
    "header": {
      "title": {"tag": "plain_text", "content": "🎉 恭喜达成成就！"},
      "template": "green"
    },
    "elements": [
      {"tag": "markdown", "content": "🌟 学习达人 🌟\n连续7天完成学习计划！\n你已经掌握了5个知识点"},
      {"tag": "action", "actions": [
        {"tag": "button", "text": {"tag": "plain_text", "content": "查看学习报告 ➤"}, "type": "primary", "url": "https://h5.aistudy.com/report?date=2026-05-07"}
      ]}
    ]
  }
}
```

### 6.4 H5页面路由设计

飞书消息中的H5链接跳转到以下页面：

| 功能 | H5页面路径 | 说明 |
|------|-----------|------|
| 学习地图 | `/map` | 查看完整学习路径 |
| 知识点学习 | `/learn?point={id}&tab={mode}` | 费曼讲解 / 苏格拉底追问 |
| 题目练习 | `/practice?point={id}` | 即时练习，即时反馈 |
| 错题本 | `/wrong` | 查看所有错题 |
| 学习报告 | `/report?date={date}` | 今日学习总结 |
| 题库管理 | `/admin/question-bank` | 文档上传与管理 |

### 6.5 飞书配置步骤

| 步骤 | 操作 |
|------|------|
| 1 | 在[飞书开放平台](https://open.feishu.cn/)创建自建应用 |
| 2 | 开通机器人能力，开启「消息」和「定时消息」权限 |
| 3 | 配置事件订阅：im.message.receive_v1 |
| 4 | 开发后端服务，配置webhook事件接收 |
| 5 | 配置H5域名白名单（确保飞书内可正常跳转） |
| 6 | 测试消息发送，确认H5链接可正常跳转 |

---

## 七、AI服务设计

### 7.1 AI服务架构

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

### 7.2 提示词模板

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

### 7.3 MiniMax API调用

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

## 八、题库导入

### 8.1 处理流程

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

### 8.2 PDF解析规则

| 规则 | 说明 |
|------|------|
| 题目识别 | 以序号开头（1.、2.、一、）识别为题目 |
| 选项识别 | 以A/B/C/D或（1）（2）开头识别为选项 |
| 答案识别 | 关键词："答案："、"正确答案是"、"[答案]" |
| 解析识别 | 关键词："解析："、"分析：" |

### 8.3 支持题型

| 题型 | 支持状态 |
|------|----------|
| 单项选择题 | ✅ |
| 多项选择题 | ✅ |
| 判断题 | ✅ |
| 填空题 | ✅ |
| 简答题 | ⚠️ 部分支持 |

---

## 九、题库上传与管理技术实现

### 9.1 模块概述

题库上传与管理模块负责将线下文档导入系统，通过AI自动理解、分类、结构化存储，形成可用的题库资源。

```
┌─────────────────────────────────────────────────────────────────┐
│                题库上传与管理模块架构                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  文档解析   │  │  AI处理    │  │  数据存储   │             │
│  │  docx/pdf   │→ │  分类/提取  │→ │  SQLite    │             │
│  │  txt/md/excel│  │  MiniMax   │  │  本地文件   │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              管理员端（题库管理后台）                     │    │
│  │  知识点CRUD  │  题目CRUD  │  批量导入/导出              │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 9.2 文档解析服务

#### 支持格式

| 格式 | 解析库 | 说明 |
|------|--------|------|
| .docx | python-docx | Word 2007+ |
| .doc | 先转PDF再解析 | 需转换处理 |
| .pdf | pdfplumber / PyPDF2 | 文本提取 |
| .txt | 内置open() | 按行读取，格式分隔 |
| .md | 内置open() | Markdown结构化 |
| .xlsx/.xls | openpyxl | Excel表格解析 |

#### 解析服务实现

```python
# modules/question/document_parser.py

import os
from pathlib import Path

class DocumentParser:
    """文档解析服务"""

    def parse_document(self, file_path: str) -> dict:
        ext = Path(file_path).suffix.lower()

        if ext == '.docx':
            return self._parse_docx(file_path)
        elif ext == '.pdf':
            return self._parse_pdf(file_path)
        elif ext in ('.txt', '.md'):
            return self._parse_text(file_path)
        elif ext in ('.xlsx', '.xls'):
            return self._parse_excel(file_path)
        else:
            raise ValueError(f"不支持的格式: {ext}")

    def _parse_docx(self, file_path: str) -> dict:
        import docx
        doc = docx.Document(file_path)
        text = '\n'.join([p.text for p in doc.paragraphs])
        return {'content': text, 'type': 'docx'}

    def _parse_pdf(self, file_path: str) -> dict:
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            text = '\n'.join([p.extract_text() or '' for p in pdf.pages])
        return {'content': text, 'type': 'pdf'}

    def _parse_text(self, file_path: str) -> dict:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {'content': content, 'type': 'text'}

    def _parse_excel(self, file_path: str) -> dict:
        import openpyxl
        wb = openpyxl.load_workbook(file_path)
        ws = wb.active
        rows = [[cell.value for cell in row] for row in ws.iter_rows()]
        import json
        return {'content': json.dumps(rows, ensure_ascii=False), 'type': 'excel'}
```

### 9.3 AI分类与提取服务

#### 分类判断

```python
# modules/ai/classifier.py

import json

async def classify_document(content: str, ai_service) -> dict:
    """AI分类判断：知识点 or 习题"""
    prompt = f"""你是一个文档分类助手。请分析以下文档内容，判断是"精华知识点"还是"重点习题"。

文档内容：
---
{content[:2000]}
---

分类标准：
- 精华知识点：包含概念定义、原理说明、术语解释等
- 重点习题：包含问题、选项、答案等

请输出JSON格式（不包含markdown代码块）：
{{
  "type": "knowledge" | "question",
  "confidence": 0.0-1.0,
  "reason": "判断理由"
}}"""

    response = await ai_service.complete(prompt)
    return json.loads(response)
```

#### 知识点提取

```python
# modules/ai/knowledge_extractor.py

import json

async def extract_knowledge(content: str, ai_service, chapter: str = None) -> dict:
    """从文档中提取知识点"""
    chapter_info = f"章节：{chapter}" if chapter else ""

    prompt = f"""你是一个知识点提取助手。请从以下文档中提取知识点信息。

文档内容：
---
{content[:3000]}
---

{chapter_info}

请提取JSON（不包含markdown代码块）：
{{
  "title": "知识点标题",
  "chapter": "所属章节",
  "summary": "100字以内总结",
  "keyPoints": ["关键点1", "关键点2"],
  "difficulty": 1-5,
  "relatedKnowledge": ["相关知识点1"],
  "feynmanMaterial": "可用于费曼讲解的素材"
}}"""

    response = await ai_service.complete(prompt)
    cleaned = response.strip().strip('`').replace('json\n', '')
    return json.loads(cleaned)
```

#### 题目提取

```python
# modules/ai/question_extractor.py

import json

async def extract_questions(content: str, ai_service) -> list:
    """从文档中提取题目"""
    prompt = f"""你是一个题目提取助手。请从以下文档中提取题目信息。

文档内容：
---
{content[:3000]}
---

请提取所有题目，每题输出JSON（不包含markdown代码块）：
{{
  "type": "single" | "multiple" | "judge",
  "content": "题目内容",
  "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
  "answer": "B",
  "explanation": "答案解析",
  "difficulty": 1-5,
  "relatedKnowledge": "关联的知识点"
}}

如果文档包含多个题目，请以JSON数组形式输出。"""

    response = await ai_service.complete(prompt)
    cleaned = response.strip().strip('`').replace('json\n', '')
    parsed = json.loads(cleaned)
    return parsed if isinstance(parsed, list) else [parsed]
```

### 9.4 题库管理API

#### 知识点管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `GET /api/knowledge` | 获取知识点列表 | 支持分页、筛选 |
| `GET /api/knowledge/<id>` | 获取知识点详情 | 包含关联题目 |
| `POST /api/knowledge` | 新增知识点 | 手动创建 |
| `PUT /api/knowledge/<id>` | 更新知识点 | 完整更新 |
| `DELETE /api/knowledge/<id>` | 删除知识点 | 需确认关联题目 |
| `POST /api/knowledge/batch` | 批量导入 | Excel格式 |
| `GET /api/knowledge/export` | 批量导出 | Excel格式 |

#### 题目管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `GET /api/questions` | 获取题目列表 | 支持分页、筛选 |
| `GET /api/questions/<id>` | 获取题目详情 | 包含解析 |
| `POST /api/questions` | 新增题目 | 手动创建 |
| `PUT /api/questions/<id>` | 更新题目 | 完整更新 |
| `DELETE /api/questions/<id>` | 删除题目 | 需确认 |
| `POST /api/questions/batch` | 批量导入 | Excel格式 |
| `GET /api/questions/export` | 批量导出 | Excel格式 |

### 9.5 数据库扩展

#### 文档上传记录表

```sql
CREATE TABLE IF NOT EXISTS document_upload (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,              -- 原始文件名
    file_type TEXT,                      -- docx/doc/pdf/txt/md/xlsx/xls
    category TEXT NOT NULL,              -- knowledge/question
    status TEXT DEFAULT 'pending',       -- pending/processing/completed/failed
    ai_result TEXT,                      -- AI分类/提取结果（JSON）
    user_id INTEGER,
    error_message TEXT,
    processed_count INTEGER DEFAULT 0,   -- 处理数量
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 知识库扩展表

```sql
CREATE TABLE IF NOT EXISTS knowledge_detail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,                 -- 知识点标题
    chapter TEXT,                        -- 所属章节
    summary TEXT,                        -- 摘要
    content TEXT,                        -- 详细内容
    key_points TEXT,                     -- 关键点（JSON数组）
    feynman_material TEXT,               -- 费曼素材
    difficulty INTEGER DEFAULT 1,        -- 难度 1-5
    source_document_id INTEGER,          -- 来源文档
    status TEXT DEFAULT 'active',        -- active/archived
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_document_id) REFERENCES document_upload(id)
);
```

### 9.6 题库上传流程

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
│  │ 1. 保存文件到本地                                        │   │
│  │ 2. 创建 document_upload 记录（pending）                  │   │
│  │ 3. 异步处理：                                           │   │
│  │    a. 解析文档                                           │   │
│  │    b. AI分类判断                                         │   │
│  │    c. AI提取内容                                         │   │
│  │    d. 存储到数据库                                       │   │
│  │    e. 更新 document_upload 状态                          │   │
│  │ 4. 返回处理结果                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 十、部署架构

### 10.1 部署架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        部署环境                              │
│                                                          │
│   ┌─────────────────────────────────────────────────┐   │
│   │              Python 后端服务                      │   │
│   │                                                 │   │
│   │   ┌─────────────┐    ┌─────────────┐            │   │
│   │   │  飞书推送   │    │  AI服务     │            │   │
│   │   │  定时任务   │    │  MiniMax   │            │   │
│   │   └─────────────┘    └─────────────┘            │   │
│   │                                                 │   │
│   │   ┌─────────────────────────────────────┐      │   │
│   │   │  SQLite 数据库 (questions.db)         │      │   │
│   │   └─────────────────────────────────────┘      │   │
│   │                                                 │   │
│   └─────────────────────────────────────────────────┘   │
│                                                          │
│   ┌─────────────────────────────────────────────────┐   │
│   │              H5前端（CDN / 静态托管）             │   │
│   │  学习地图 / AI对话 / 题目练习 / 错题本 / 报告    │   │
│   └─────────────────────────────────────────────────┘   │
│                                                          │
│   域名：h5.aistudy.com（HTTPS，飞书跳转必需）            │
│                                                          │
└─────────────────────────────────────────────────────────────┘
```

### 10.2 部署配置

```yaml
# config.yaml
app:
  host: 0.0.0.0
  port: 8081

h5:
  base_url: https://h5.aistudy.com    # H5页面域名（需HTTPS）
  static_dir: ./frontend/dist         # H5前端构建产物目录

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

### 10.3 环境变量

```bash
# .env
H5_BASE_URL=https://h5.aistudy.com
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret
MINIMAX_API_KEY=your_api_key
DATABASE_PATH=./database/questions.db
```

---

## 十一、安全设计

### 11.1 接口安全

| 机制 | 说明 |
|------|------|
| 飞书签名验证 | 校验飞书消息请求来源 |
| H5链接Token | 飞书跳转H5时携带时效Token，防止未授权访问 |
| 命令白名单 | 只处理预定义命令 |
| 内容过滤 | AI输出合规检查 |
| 追问限制 | 单次对话最多20轮 |

### 11.2 数据安全

| 机制 | 说明 |
|------|------|
| 数据库文件 | 本地存储，定期备份 |
| 敏感信息 | API密钥通过环境变量配置 |
| HTTPS | H5页面必须配置SSL证书（飞书跳转要求） |
| 飞书白名单 | H5域名需加入飞书应用白名单 |

---

## 十二、监控运维

### 12.1 监控指标

| 指标 | 告警阈值 |
|------|----------|
| API响应时间 | > 2s |
| AI生成时间 | > 10s |
| 错误率 | > 1% |
| 并发会话数 | > 50 |

### 12.2 日志格式

```python
# utils/logger.py

import logging
import uuid
from datetime import datetime

def log_event(level: str, user_id: str, action: str, duration: int = None, status: int = 200):
    """统一日志格式"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "level": level,
        "traceId": str(uuid.uuid4()),
        "userId": user_id,
        "action": action,
        "duration": duration,
        "status": status
    }
    logging.info(json.dumps(log_entry, ensure_ascii=False))
```

### 12.3 数据库备份

```bash
#!/bin/bash
# scripts/backup_db.sh

BACKUP_DIR="./database/backup"
DB_PATH="./database/questions.db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
cp $DB_PATH "$BACKUP_DIR/questions_$TIMESTAMP.db"

# 保留最近7天的备份
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
```

---

## 十三、开发计划

### 阶段一：MVP（1-2周）

| 任务 | 工期 | 交付 |
|------|------|------|
| 项目初始化 | 1天 | Python项目搭建 |
| 数据库设计 | 1天 | SQLite表结构 |
| H5前端搭建 | 2天 | 移动端H5页面框架 |
| 飞书机器人 | 1天 | 机器人配置+消息推送（含H5链接） |
| AI服务接入 | 2天 | MiniMax API对接 |
| 费曼讲解功能 | 2天 | H5页面对话流程 |
| 苏格拉底追问 | 2天 | H5页面追问逻辑 |
| 题目练习功能 | 2天 | H5页面答题+解析 |

### 阶段二：功能完善（1周）

| 任务 | 工期 | 交付 |
|------|------|------|
| 学习提醒 | 2天 | 定时任务+飞书推送（含H5链接） |
| 进度追踪 | 1天 | 积分/连胜/等级 |
| 错题本 | 1天 | H5页面错题收集+复习 |
| 文档导入 | 2天 | 多格式题库导入功能 |
| H5部署 | 1天 | CDN部署+HTTPS配置+飞书白名单 |

### 阶段三：体验优化（持续）

- 题库扩充
- 历年真题接入
- 学习报告优化

---

## 十四、成本估算

### 14.1 基础成本

| 资源 | 选型 | 月费 |
|------|------|------|
| 后端托管 | Serverless / 本地 | ¥0-100 |
| H5前端托管 | CDN / 静态服务器 | ¥0-50 |
| 数据库 | SQLite本地 | ¥0 |
| AI调用 | MiniMax按量计费 | ¥100-300/月 |
| 域名+SSL | HTTPS证书（飞书跳转必需） | ¥0-50/年 |

### 14.2 AI调用估算

| 场景 | 调用量 | 估算费用 |
|------|--------|----------|
| 费曼讲解 | 45次/天 × 30 | ¥50 |
| 苏格拉底追问 | 100次/天 × 30 | ¥80 |
| PDF解析 | 1次/天 × 30 | ¥30 |
| AI出题 | 5次/天 × 30 | ¥40 |
| **总计** | - | **¥200/月** |

---

### 8.2 题库上传进度实现

#### 进度跟踪机制

```
┌─────────────────────────────────────────────────────────────────┐
│                    题库上传进度跟踪                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. 创建上传记录                                                │
│     └→ upload_progress 表插入初始记录，progress=0               │
│                                                                  │
│  2. 阶段性更新                                                  │
│     └→ 每个处理阶段更新 progress 和 stage 字段                   │
│        - file_uploaded (10%): 文件上传完成                      │
│        - parsing (30%): 正在解析文档内容                        │
│        - recognizing (50%): 识别题型和选项                       │
│        - importing (80%): 题目数据导入中                        │
│        - completed (100%): 上传完成                             │
│                                                                  │
│  3. 前端轮询/websocket                                          │
│     └→ 前端每2秒查询进度，或使用websocket实时推送                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### API设计

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/upload/progress | 创建上传任务 |
| GET | /api/upload/progress/{id} | 获取上传进度 |
| WebSocket | /ws/upload/{id} | 实时推送进度 |

---

_文档版本：v1.6（新增用户管理模块 + 题库上传进度） | 最后更新：2026-05-10_
_作者：1902 🦞_
