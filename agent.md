# AI伴学系统 - Agent工作手册

> 📅 文档版本：v1.5 | 日期：2026-05-07
> 📂 基于：PRD v1.5 + 技术文档 v1.5

---

## 一、项目概述

### 1.1 项目背景

**AI伴学系统**是一款基于**费曼学习法 + 苏格拉底提问法**的智能备考助手，帮助用户通过2026年11月系统架构师考试。

**核心理念**：不直接给答案，通过追问引导用户自己思考，彻底弄懂每一个知识点。

### 1.2 核心目标

| 目标 | 衡量指标 |
|------|----------|
| 考试通过 | 系统架构师 ≥ 45分 |
| 知识点掌握 | 每个核心概念能用自己的话讲清楚 |
| 学习坚持 | 连续学习 ≥ 30天 |

### 1.3 技术栈

| 组件 | 选型 | 说明 |
|------|------|------|
| **交互界面** | H5页面 | 手机浏览器直接访问，无需安装 |
| **通知推送** | 飞书机器人 | 定时提醒、督促消息、成就通知 |
| **AI模型** | MiniMax code-plan | 费曼讲解/苏格拉底追问/文档解析/出题 |
| **数据库** | SQLite | 轻量级文件型数据库 |
| **后端** | Python 3.10+ | FastAPI/Flask |
| **文档解析** | python-docx/pdfplumber/openpyxl | 多格式文档解析 |

### 1.4 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      用户端                                 │
├──────────────────────┬──────────────────────────────────────┤
│  H5页面（交互界面）  │  飞书机器人（通知渠道）              │
│  学习地图/AI对话/    │  定时提醒/督促/成就通知              │
│  题目练习/错题本     │  消息内嵌H5跳转链接                  │
└──────────┬───────────┴──────────┬───────────────────────────┘
           │                      │
           └──────────┬───────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    AI伴学系统后端                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  学习引擎  │  │  题目服务   │  │  计划服务   │        │
│  │  费曼讲解  │  │  文档解析   │  │  飞书推送   │        │
│  │  苏格拉底  │  │  AI出题    │  │  定时任务   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                      │                                     │
│              ┌───────┴───────┐                             │
│              │  SQLite 数据库 │                             │
│              └───────────────┘                             │
│                      │                                     │
│              ┌───────┴───────┐                             │
│              │ MiniMax AI    │                             │
│              └───────────────┘                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、学习方法论

### 2.1 费曼学习法

**核心原则**：用最简单的话把概念讲清楚，让8岁小孩都能听懂。

**操作步骤**：
1. 选择一个概念
2. 假设要教给8岁小孩
3. 用生活化的类比讲解
4. 发现讲不清楚的地方 → 回头复习
5. 简化类比，用更简单的语言重讲

**示例（Cache讲解）**：

```
Cache = CPU和内存之间的"厨房台面"

想象你在厨房做饭：
- 你 = CPU（需要数据的人）
- 冰箱 = 内存（存储数据的地方）
- 厨房台面 = Cache（临时存放常用食材）

做菜时你会先看台面有没有食材，没有才去开冰箱拿，
而不是每次都跑超市买。

Cache就是这样：把CPU常用的数据放在"台面"上，
CPU不用每次都去"冰箱"（内存）慢慢找数据了。
```

### 2.2 苏格拉底提问法

**核心原则**：不直接给答案，通过连续追问引导用户自己发现答案。

**提问层次**：
- Level 1: "这个问题是什么意思？"
- Level 2: "为什么会出现这种现象？"
- Level 3: "能举个生活中的例子吗？"
- Level 4: "如果...会怎样？"
- Level 5: "还有其他可能性吗？"

**示例（追问Cache为什么快）**：

```
Q: 为什么Cache比内存快？
A: 因为离CPU近

Q: "近"意味着什么？（距离、位置）
A: 物理距离近，传输延迟短

Q: 还有什么原因让Cache更快？
A: 技术实现不同...

（逐步引导，不直接给答案）
```

---

## 三、学习地图与核心功能

### 3.1 学习地图

学习地图是整个伴学系统的入口，以树形结构展示完整学习路径。

```
📍 学习地图

📚 第一章：计算机基础
├── 📖 1.1 存储系统
│   ├── 🔓 Cache（高速缓存存储器）  ✅ 已掌握
│   ├── 🔓 内存管理                     ⏳ 进行中
│   └── 🔓 硬盘与IO                     🔒 待解锁
├── 📖 1.2 指令系统
│   ├── 🔒 指令格式                     🔒 待解锁
│   └── 🔒 寻址方式                     🔒 待解锁
└── 📖 1.3 CPU结构
    └── 🔒 ...
```

**知识点状态机**：

```
待解锁(LOCKED) → 进行中(IN_PROGRESS) → 已掌握(COMPLETED)
      ↑                                        │
      └────────── 放弃学习 ←──────────────────┘
```

### 3.2 AI解答（费曼学习法）

**功能入口**：学习页点击【AI解答】按钮

**交互流程**：
1. AI先用官方教材内容讲解知识点
2. 用户可追问："这个不理解"、"能举个例吗"
3. AI通过费曼法，用生活类比帮助理解

### 3.3 AI帮测（苏格拉底提问法）

**功能入口**：学习页点击【AI帮测】按钮

**掌握度判定算法**：

| 回答质量 | 加分 |
|----------|------|
| 优秀（完全正确+理解到位） | +25% |
| 良好（正确但理解一般） | +15% |
| 一般（部分正确） | +8% |
| 较差（方向对但细节错） | +5% |
| 错误（完全不对） | +0% |

- 初始掌握度：0%，问题数量：5题
- 解锁条件：掌握度 ≥ 90%
- 失败处理：5题后仍 < 90%，返回知识点重新学习

### 3.4 知识点解锁机制

- 同一章节内的知识点按顺序解锁
- 前置知识点掌握度达到90%，才能解锁下一个
- 章节内所有知识点完成后，自动解锁下一章节
- 用户可随时回顾已掌握的知识点（重新测试）

---

## 四、知识点体系

### 4.1 学习阶段总览

| 阶段 | 科目 | 建议时间 |
|------|------|----------|
| 第一阶段 | 计算机系统基本知识 | 第1-10天 |
| 第二阶段 | 信息系统基础 | 第11-15天 |
| 第三阶段 | 信息安全技术 | 第16-18天 |
| 第四阶段 | 软件工程 | 第19-25天 |
| 第五阶段 | 数据库设计 | 第26-30天 |
| 第六阶段 | 系统架构设计 | 第31-38天 |
| 第七阶段 | 架构评估与可靠性 | 第39-42天 |
| 第八阶段 | 软件架构演化维护 | 第43-45天 |
| 冲刺阶段 | 历年真题+模拟题 | 第46天+ |

### 4.2 第一阶段：计算机系统基本知识

**1.1 计算机系统概述**
- 计算机系统的定义、组成和分类

**1.2 计算机硬件**
- 1.2.1 冯·诺依曼计算机结构
- 1.2.2 处理器（CPU、GPU、DSP、FPGA、国产芯片）
- 1.2.3 指令集（CISC和RISC）
- 1.2.4 存储器（片上缓存、片外缓存、主存、外存）
- 1.2.5 总线（内总线、系统总线、外部总线）
- 1.2.6 接口（显示、音频、网络、SATA）

**1.3 计算机软件**
- 1.3.1 操作系统（组成、类型、特点原理）
- 1.3.2 批处理/分时/网络/分布式操作系统
- 1.3.3 嵌入式操作系统与实时操作系统
- 1.3.4 数据库系统（关系型、分布式）
- 1.3.5 文件系统（类型、原理、存取方式）
- 1.3.6 网络协议（LAN、WAN、无线网、移动通信网）
- 1.3.7 中间件（MQ Series、Tuxedo）
- 1.3.8 软件构件（CORBA、J2EE、DNA2000）

**1.4 嵌入式系统及软件**
- 1.4.1 嵌入式系统组成及特点
- 1.4.2 实时系统分类（强实时/弱实时/安全攸关）
- 1.4.3 嵌入式软件开发方法
- 1.4.4 安全攸关软件安全性设计（DO-178）

**1.5 计算机网络**
- 1.5.1 网络基本概念（四阶段、基本功能、指标）
- 1.5.2 通信技术（信道、信号、复用、5G）
- 1.5.3 网络技术（LAN、WLAN、WAN、MAN、移动网）
- 1.5.4 组网技术（OSI/RM、TCP/IP协议集）
- 1.5.5 网络工程（规划、设计、实施）

**1.6 计算机语言**
- 1.6.1 机器语言与汇编语言
- 1.6.2 高级语言（C、C++、Java、Python）
- 1.6.3 建模语言（UML组成、关系、五种视图）
- 1.6.4 形式化语言（Z语言）

**1.7 多媒体**
- 多媒体概述、视音频技术、数据压缩、VR/AR

**1.8 系统工程**
- 霍尔三维结构、切克兰德方法、并行工程
- MBSE基于模型的系统工程

**1.9 系统性能**
- 性能指标、Amdahl解决方案、负载均衡、性能评估

---

## 五、AI提示词模板

### 5.1 费曼讲解提示词

```
你是大王的学习助手，擅长用费曼学习法解答疑问。

当前知识点：{knowledge_title}
官方教材内容：{official_content}

用户提问：{user_question}

解答原则：
1. 先承认用户的疑问是合理的
2. 用生活化类比解释（避免术语堆砌）
3. 层层递进，从已知到未知
4. 最后引导用户自己总结

格式：
🤖 【AI解答】

[直接回应用户的疑问，用费曼法]
[生活化类比]
[回到知识点本身的核心]
[引导用户思考："你现在能用自己的话说吗？"]
```

### 5.2 苏格拉底追问提示词

```
你是大王的学习助手，擅长用苏格拉底提问法测试学习效果。

当前知识点：{knowledge_title}
核心要点：{key_points}
官方教材内容：{official_content}

测试规则：
1. 每次只问1个问题
2. 根据用户回答，判断理解程度（优秀/良好/一般/较差/错误）
3. 正确时不直接夸赞，继续追问更深层
4. 错误时不直接否定，用引导性问题纠正
5. 累计5题后判断是否达到90%掌握度

苏格拉底提问层次：
- Level 1: 事实性问题（是什么）
- Level 2: 理解性问题（为什么）
- Level 3: 应用性问题（怎么样）
- Level 4: 分析性问题（与其他知识的关系）
- Level 5: 评价性问题（你的看法）

输出格式：
🤔 【苏格拉底提问】

❓ 问题{序号}/5：
{问题内容}

[等待用户回答后，输出评价和下一问题或最终判定]
```

### 5.3 文档分类提示词

```
你是一个文档分类助手。请分析以下文档内容，判断是"精华知识点"还是"重点习题"。

文档内容：
---
{content}
---

分类标准：
- 精华知识点：包含概念定义、原理说明、术语解释等
- 重点习题：包含问题、选项、答案等

请输出JSON格式：
{
  "type": "knowledge" | "question",
  "confidence": 0.0-1.0,
  "reason": "判断理由"
}
```

### 5.4 知识点提取提示词

```
你是一个知识点提取助手。请从以下文档中提取知识点信息。

文档内容：
---
{content}
---

章节（可选）：{chapter || '未指定'}

请提取JSON：
{
  "title": "知识点标题",
  "chapter": "所属章节",
  "summary": "100字以内总结",
  "keyPoints": ["关键点1", "关键点2", ...],
  "difficulty": 1-5,
  "relatedKnowledge": ["相关知识点1", ...],
  "feynmanMaterial": "可用于费曼讲解的素材"
}
```

### 5.5 题目提取提示词

```
你是一个题目提取助手。请从以下文档中提取题目信息。

文档内容：
---
{content}
---

请提取所有题目，每题输出JSON：
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
```

### 5.6 答案解析提示词

```
题目：{question}
用户答案：{user_answer}
正确答案：{correct_answer}

请给出详细解析：
1. 分析用户答案对错
2. 解释正确答案是何得出
3. 关联相关知识点
4. 如答错，给出理解提示

要求：清晰、详细、帮助用户真正理解
```

---

## 六、数据库设计

### 6.1 users（用户表）

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feishu_openid TEXT UNIQUE,
    feishu_union_id TEXT,
    nickname VARCHAR(50),
    avatar VARCHAR(255),
    level INTEGER DEFAULT 1,
    score INTEGER DEFAULT 0,
    streak INTEGER DEFAULT 0,
    streak_last_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 6.2 questions（题目表）

```sql
CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    options TEXT,
    answer TEXT NOT NULL,
    analysis TEXT,
    knowledge_point TEXT,
    difficulty INTEGER DEFAULT 1,
    source TEXT,
    source_file TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'pending'
);
```

### 6.3 knowledge_points（知识点表）

```sql
CREATE TABLE knowledge_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    chapter TEXT,
    stage TEXT,
    sort_order INTEGER,
    status TEXT DEFAULT 'locked',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 6.4 study_plans（学习计划表）

```sql
CREATE TABLE study_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    feishu_chat_id TEXT,
    name TEXT NOT NULL,
    daily_goal TEXT,
    preferred_time TEXT,
    reminder_enabled INTEGER DEFAULT 1,
    reminder_times TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 6.5 reminder_rules（提醒规则表）

```sql
CREATE TABLE reminder_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    type TEXT NOT NULL,
    trigger_time TEXT,
    message_template TEXT,
    h5_url_template TEXT,
    enabled INTEGER DEFAULT 1,
    condition TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 6.6 study_records（学习记录表）

```sql
CREATE TABLE study_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    knowledge_point_id INTEGER,
    learned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    duration INTEGER,
    questions_done INTEGER DEFAULT 0,
    correct_count INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_points(id)
);
```

### 6.7 answer_records（答题记录表）

```sql
CREATE TABLE answer_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question_id INTEGER,
    user_answer TEXT,
    is_correct INTEGER,
    answered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_first_attempt INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (question_id) REFERENCES questions(id)
);
```

### 6.8 wrong_questions（错题本表）

```sql
CREATE TABLE wrong_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question_id INTEGER,
    wrong_count INTEGER DEFAULT 1,
    last_wrong_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    mastered INTEGER DEFAULT 0,
    mastered_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (question_id) REFERENCES questions(id)
);
```

### 6.9 document_upload（文档上传记录表）

```sql
CREATE TABLE document_upload (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    file_type TEXT,
    category TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    ai_result TEXT,
    user_id INTEGER,
    error_message TEXT,
    processed_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 6.10 knowledge_detail（知识库扩展表）

```sql
CREATE TABLE knowledge_detail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    chapter TEXT,
    summary TEXT,
    content TEXT,
    key_points TEXT,
    feynman_material TEXT,
    difficulty INTEGER DEFAULT 1,
    source_document_id INTEGER,
    status TEXT DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_document_id) REFERENCES document_upload(id)
);
```

---

## 七、飞书通知与H5跳转设计

### 7.1 设计思路

采用**飞书通知 + H5交互**的混合架构：
- **飞书**：通知推送渠道（定时提醒、督促消息、成就通知）
- **H5页面**：学习交互界面（费曼讲解、苏格拉底追问、题目练习等）
- 用户在飞书中收到提醒 → 点击链接 → 跳转到H5页面开始学习

### 7.2 飞书消息卡片（含H5链接）

**学习提醒卡片**：

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

**督促提醒卡片**：

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

### 7.3 飞书自动行为

| 触发条件 | 飞书消息行为 | 跳转链接 |
|----------|------------|---------|
| 到达学习时间 | 学习提醒卡片 | → 学习页 |
| 上午未学习 | 督促消息 | → 学习页 |
| 错题被收录 | 鼓励消息 | → 错题本 |
| 连续学习3天 | 恭喜消息 | → 学习报告 |
| 连续学习7天 | 庆祝卡片 | → 成就页 |
| 完成章节 | 里程碑庆祝 | → 学习报告 |

### 7.4 H5页面路由

| 功能 | H5页面路径 | 说明 |
|------|-----------|------|
| 学习地图 | `/map` | 查看完整学习路径 |
| 知识点学习 | `/learn?point={id}&tab={mode}` | 费曼讲解 / 苏格拉底追问 |
| 题目练习 | `/practice?point={id}` | 即时练习 |
| 错题本 | `/wrong` | 查看所有错题 |
| 学习报告 | `/report?date={date}` | 今日学习总结 |
| 题库管理 | `/admin/question-bank` | 文档上传与管理 |

---

## 八、题库上传与管理

### 8.1 支持的文档格式

| 格式 | 说明 | 处理方式 |
|------|------|----------|
| .docx | Word 2007+ | python-docx 解析 |
| .doc | Word 97-2003 | 先转pdf再解析 |
| .pdf | PDF文档 | pdfplumber/PyPDF2 解析 |
| .txt | 纯文本 | 直接读取，按格式分隔 |
| .md | Markdown | 直接读取，结构化解析 |
| .xlsx/.xls | Excel表格 | openpyxl 解析 |

### 8.2 文档分类

| 类型 | 用途 | 处理方式 |
|------|------|----------|
| **精华知识点** | 纳入学习地图 | AI提取核心概念，生成费曼讲解素材 |
| **重点习题** | 日常练习/测验 | AI识别题型、答案、解析 |

### 8.3 AI处理流程

```
文档上传 → 文档解析 → AI分类判断 → AI内容提取 → 结构化存储 → 与学习地图联动
```

### 8.4 文档解析规则

- 题目识别：以序号开头（1.、2.、一、）
- 选项识别：以A/B/C/D或（1）（2）开头
- 答案识别：关键词："答案："、"正确答案是"、"[答案]"
- 解析识别：关键词："解析："、"分析："

---

## 九、每日学习流程

```
┌─────────────────────────────────────────────────────────┐
│                    每日学习流程                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1️⃣ 飞书提醒                                           │
│     └→ 飞书推送提醒，点击链接跳转H5学习页面              │
│                                                         │
│  2️⃣ 学习地图                                           │
│     └→ 打开H5学习地图，选择今日学习的知识点              │
│                                                         │
│  3️⃣ AI解答（费曼学习法）                                │
│     └→ AI用生活类比讲解新知识点                          │
│        用户可追问，AI继续解答                            │
│                                                         │
│  4️⃣ AI帮测（苏格拉底提问法）                            │
│     └→ AI连续追问，引导用户思考                          │
│        掌握度≥90% → 自动解锁下一知识点                   │
│                                                         │
│  5️⃣ 题目练习                                           │
│     └→ 3-5道练习题检验理解                               │
│        答对→积分奖励 / 答错→收录错题本                   │
│                                                         │
│  6️⃣ 学习报告                                           │
│     └→ 今日学习完成，获得积分，解锁明日内容               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 十、奖励机制

| 奖励类型 | 触发条件 | 奖励 |
|----------|----------|------|
| 连续学习 | 每天完成学习 | 连胜天数+1 |
| 答题得分 | 答对题目 | +10基础分 |
| 连击奖励 | 连续答对3题以上 | +2/题 |
| 快速答题 | 10秒内答对 | +5额外分 |
| 弄懂难点 | 首次答对错题 | +20分 |
| 阶段达标 | 完成一个章节 | +100分 |

---

## 十一、项目结构

```
backend/
├── src/
│   ├── main.py                    # 入口
│   ├── config/
│   │   └── settings.py           # 配置
│   ├── modules/
│   │   ├── feishu/               # 飞书通知模块
│   │   │   ├── bot.py            # 机器人主逻辑
│   │   │   ├── handlers/        # 消息处理器
│   │   │   │   ├── command.py   # 命令处理
│   │   │   │   ├── chat.py      # 对话处理
│   │   │   │   └── schedule.py  # 定时任务
│   │   │   └── cards/           # 卡片模板（含H5链接）
│   │   ├── ai/                  # AI服务模块
│   │   │   ├── service.py       # AI服务
│   │   │   ├── feynman.py       # 费曼讲解
│   │   │   ├── socratic.py      # 苏格拉底追问
│   │   │   └── pdf_parser.py    # 文档解析
│   │   ├── question/            # 题库模块
│   │   │   ├── service.py       # 题库服务
│   │   │   ├── repository.py    # 数据访问
│   │   │   └── generator.py     # AI出题
│   │   ├── knowledge/           # 知识库模块
│   │   │   ├── service.py
│   │   │   └── repository.py
│   │   └── study/               # 学习模块
│   │       ├── service.py       # 学习服务
│   │       ├── progress.py      # 进度管理
│   │       └── reminder.py      # 提醒服务（飞书推送）
│   ├── database/
│   │   ├── db.py               # 数据库连接
│   │   └── migrations/         # 迁移脚本
│   └── prompts/
│       ├── feynman.txt         # 费曼提示词
│       ├── socratic.txt        # 苏格拉底提示词
│       └── explanation.txt      # 解析提示词
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

## 十二、开发计划

### MVP（1-2周）

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

### 功能完善（1周）

| 任务 | 工期 | 交付 |
|------|------|------|
| 学习提醒 | 2天 | 定时任务+飞书推送（含H5链接） |
| 进度追踪 | 1天 | 积分/连胜/等级 |
| 错题本 | 1天 | H5页面错题收集+复习 |
| 文档导入 | 2天 | 多格式题库导入功能 |
| H5部署 | 1天 | CDN部署+HTTPS配置+飞书白名单 |

---

## 十三、验收标准

### 费曼讲解验收标准
- [ ] 用生活化类比引入（让8岁小孩能懂）
- [ ] 核心概念解释不超过3句话
- [ ] 提供1-2个生活例子
- [ ] 有"如果...会怎样"的思考引导

### 苏格拉底追问验收标准
- [ ] 不直接给答案
- [ ] 根据用户回答调整追问方向
- [ ] 至少追问3轮
- [ ] 引导用户自己发现答案
- [ ] 掌握度判定算法正确（优秀+25%/良好+15%/一般+8%/较差+5%/错误+0%）

### 题目练习验收标准
- [ ] 每知识点3-5道题
- [ ] 答对/答错都有详细解析
- [ ] 答错的题目自动加入错题本

### 文档导入验收标准
- [ ] 支持PDF/Word/Excel/TXT/Markdown格式
- [ ] AI自动分类（知识点 vs 习题）
- [ ] 自动提取知识点或题目信息
- [ ] 人工校对后可入库
- [ ] 精华知识点与学习地图联动

### H5页面验收标准
- [ ] 手机浏览器可正常访问
- [ ] 学习地图展示完整知识章节树
- [ ] AI对话流程顺畅（费曼讲解+苏格拉底追问）
- [ ] 飞书消息链接可正常跳转H5页面
- [ ] HTTPS配置正确（飞书跳转必需）

### 飞书通知验收标准
- [ ] 定时提醒正常推送
- [ ] 消息卡片内嵌H5跳转链接
- [ ] 点击链接可正常跳转对应H5页面
- [ ] 督促消息频率合理（最小间隔2小时）

---

## 十四、注意事项

### AI回复原则
1. **不直接给答案** - 用追问引导
2. **生活化类比** - 用常见场景解释复杂概念
3. **分层递进** - 从简单到复杂
4. **鼓励为主** - 答对给予肯定，答错鼓励分析

### 开发原则
1. **轻量级** - SQLite本地数据库，降低部署复杂度
2. **预留升级** - 所有业务表含user_id，支持多用户
3. **模块化** - AI服务/飞书通知/H5前端/题库分离
4. **渐进开发** - MVP优先，功能逐步完善

### 部署注意事项
1. **HTTPS必须** - 飞书跳转H5页面要求HTTPS
2. **域名白名单** - H5域名需加入飞书应用白名单
3. **链接时效** - 飞书消息中的H5链接需携带时效Token
4. **消息频率** - 督促消息不宜过于频繁，最小间隔2小时

---

_文档版本：v1.5 | 最后更新：2026-05-07_
