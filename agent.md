# AI伴学系统 - Agent工作手册

> 📅 文档版本：v1.0 | 日期：2026-05-05
> 📂 基于：PRD v1.5 + 技术文档 v1.6

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

| 组件 | 选型 |
|------|------|
| 对话平台 | 飞书（机器人） |
| AI模型 | MiniMax code-plan |
| 数据库 | SQLite |
| 后端 | Python 3.10+ |
| PDF解析 | PyMuPDF + MiniMax |

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

## 三、知识点体系

### 3.1 学习阶段总览

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

### 3.2 第一阶段：计算机系统基本知识

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

## 四、AI提示词模板

### 4.1 费曼讲解提示词

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

### 4.2 苏格拉底追问提示词

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

### 4.3 PDF题目解析提示词

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

### 4.4 答案解析提示词

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

## 五、数据库设计

### 5.1 数据表结构

#### users（用户表）

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

#### questions（题目表）

```sql
CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,                    -- single/multiple/judge/fill/short
    content TEXT NOT NULL,
    options TEXT,                          -- JSON: {"A":"...","B":"...","C":"...","D":"..."}
    answer TEXT NOT NULL,
    analysis TEXT,
    knowledge_point TEXT,
    difficulty INTEGER DEFAULT 1,          -- 难度1-5
    source TEXT,
    source_file TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'pending'
);
```

#### knowledge_points（知识点表）

```sql
CREATE TABLE knowledge_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,             -- 1.1, 1.2.1
    name TEXT NOT NULL,
    chapter TEXT,
    stage TEXT,
    sort_order INTEGER,
    status TEXT DEFAULT 'locked',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### study_records（学习记录表）

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

#### wrong_questions（错题本表）

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

---

## 六、飞书机器人命令

| 命令 | 功能 | 示例 |
|------|------|------|
| `设置学习计划` | 配置每日学习目标和时间 | "设置学习计划每天9点学习" |
| `添加提醒` | 设置特定时间点提醒 | "下午3点提醒我复习错题" |
| `查看计划` | 显示当前学习计划 | "查看我的学习计划" |
| `查看进度` | 查询学习进度 | "查看我的进度" |
| `错题本` | 查看错题列表 | "查看我的错题本" |
| `跳过` | 跳过当前提醒 | "跳过今天的提醒" |
| `help` | 显示所有命令 | "help" |

---

## 七、每日学习流程

```
┌─────────────────────────────────────────────────────────┐
│                    每日学习流程                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1️⃣ 复习提醒                                           │
│     └→ AI推送："今天是学习第X天，复习内容是XXX"           │
│                                                         │
│  2️⃣ 费曼讲解                                           │
│     └→ AI用生活类比讲解新知识点                          │
│                                                         │
│  3️⃣ 苏格拉底追问                                       │
│     └→ AI连续追问，引导用户思考                          │
│        "能举个例子吗？""为什么？""还有其他可能吗？"        │
│                                                         │
│  4️⃣ 题目练习                                           │
│     └→ 3-5道练习题检验理解                               │
│                                                         │
│  5️⃣ 详细解析                                           │
│     └→ 答对→"你真棒！奖励+10分"                          │
│        答错→"别急，我们来分析为什么..."                  │
│                                                         │
│  6️⃣ 错题收录                                          │
│     └→ 答错的题目自动加入错题本                         │
│                                                         │
│  7️⃣ 学习报告                                           │
│     └→ 今日学习完成，获得积分，解锁明日内容               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 八、奖励机制

| 奖励类型 | 触发条件 | 奖励 |
|----------|----------|------|
| 连续学习 | 每天完成学习 | 连胜天数+1 |
| 答题得分 | 答对题目 | +10基础分 |
| 连击奖励 | 连续答对3题以上 | +2/题 |
| 快速答题 | 10秒内答对 | +5额外分 |
| 弄懂难点 | 首次答对错题 | +20分 |
| 阶段达标 | 完成一个章节 | +100分 |

---

## 九、PDF题库导入流程

```
┌─────────────────────────────────────────────────────────┐
│              PDF题库导入流程                             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1️⃣ 用户上传                                           │
│     └→ 用户在飞书发送PDF文件                            │
│                                                         │
│  2️⃣ AI解析                                            │
│     └→ 系统提取PDF中的题目、选项、答案                  │
│        支持：选择题、判断题、填空题、简答题             │
│                                                         │
│  3️⃣ 题目入库                                          │
│     └→ 解析后的题目存入题库                            │
│        自动打标签（章节、知识点、难度）                 │
│                                                         │
│  4️⃣ 人工校对                                           │
│     └→ 用户确认/修正AI解析结果                         │
│                                                         │
│  5️⃣ 出题调用                                           │
│     └→ 基于题库和知识点进行出题                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**PDF解析规则**：
- 题目识别：以序号开头（1.、2.、一、）
- 选项识别：以A/B/C/D或（1）（2）开头
- 答案识别：关键词："答案："、"正确答案是"、"[答案]"
- 解析识别：关键词："解析："、"分析："

---

## 十、项目结构

```
backend/
├── src/
│   ├── main.py                    # 入口
│   ├── config/
│   │   └── settings.py           # 配置
│   ├── modules/
│   │   ├── feishu/               # 飞书机器人模块
│   │   │   ├── bot.py            # 机器人主逻辑
│   │   │   ├── handlers/        # 消息处理器
│   │   │   │   ├── command.py   # 命令处理
│   │   │   │   ├── chat.py      # 对话处理
│   │   │   │   └── schedule.py  # 定时任务
│   │   │   └── cards/           # 卡片模板
│   │   ├── ai/                  # AI服务模块
│   │   │   ├── service.py       # AI服务
│   │   │   ├── feynman.py       # 费曼讲解
│   │   │   ├── socratic.py      # 苏格拉底追问
│   │   │   └── pdf_parser.py    # PDF解析
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
│   │       └── reminder.py      # 提醒服务
│   ├── database/
│   │   ├── db.py               # 数据库连接
│   │   └── migrations/         # 迁移脚本
│   └── prompts/
│       ├── feynman.txt         # 费曼提示词
│       ├── socratic.txt        # 苏格拉底提示词
│       └── explanation.txt      # 解析提示词
├── requirements.txt
└── run.py
```

---

## 十一、开发计划

### MVP（1-2周）

| 任务 | 工期 | 交付 |
|------|------|------|
| 项目初始化 | 1天 | Python项目搭建 |
| 数据库设计 | 1天 | SQLite表结构 |
| 飞书机器人 | 2天 | 机器人配置+消息处理 |
| AI服务接入 | 2天 | MiniMax API对接 |
| 费曼讲解功能 | 2天 | 核心对话流程 |
| 苏格拉底追问 | 2天 | 追问逻辑实现 |
| 题目练习功能 | 2天 | 答题+解析流程 |

### 功能完善（1周）

| 任务 | 工期 | 交付 |
|------|------|------|
| 学习提醒 | 2天 | 定时任务+飞书推送 |
| 进度追踪 | 1天 | 积分/连胜/等级 |
| 错题本 | 1天 | 错题收集+复习 |
| PDF导入 | 2天 | 题库导入功能 |

---

## 十二、验收标准

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

### 题目练习验收标准
- [ ] 每知识点3-5道题
- [ ] 答对/答错都有详细解析
- [ ] 答错的题目自动加入错题本

### PDF解析验收标准
- [ ] 支持PDF文本提取
- [ ] 支持单选/多选/判断/填空题型
- [ ] 自动识别题目、选项、答案、解析
- [ ] 人工校对后可入库

---

## 十三、注意事项

### AI回复原则
1. **不直接给答案** - 用追问引导
2. **生活化类比** - 用常见场景解释复杂概念
3. **分层递进** - 从简单到复杂
4. **鼓励为主** - 答对给予肯定，答错鼓励分析

### 开发原则
1. **轻量级** - SQLite本地数据库，降低部署复杂度
2. **预留升级** - 所有业务表含user_id，支持多用户
3. **模块化** - AI服务/飞书机器人/题库分离
4. **渐进开发** - MVP优先，功能逐步完善

---

_文档版本：v1.0 | 最后更新：2026-05-05_
