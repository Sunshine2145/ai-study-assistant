# AI伴学系统 - 后端

基于 FastAPI 构建的 REST API 后端服务，提供学习管理、题目练习、题库上传等功能。

## 技术栈

| 组件 | 选型 |
|------|------|
| Web框架 | FastAPI + Uvicorn |
| 数据库 | SQLite |
| AI模型 | DeepSeek / MiniMax |
| PDF解析 | PyMuPDF |

## 项目结构

```
backend/
├── src/
│   ├── main.py                 # FastAPI 入口
│   ├── config/
│   │   └── settings.py        # 配置管理（环境变量）
│   ├── database/
│   │   ├── db.py              # 数据库连接
│   │   └── migrations/
│   │       └── init_knowledge.py  # 初始化知识点
│   ├── modules/
│   │   ├── ai/                # AI服务模块
│   │   │   ├── feynman.py      # 费曼讲解
│   │   │   ├── socratic.py     # 苏格拉底追问
│   │   │   ├── pdf_parser.py   # PDF解析
│   │   │   └── question_generator.py  # AI出题
│   │   └── feishu/            # 飞书机器人
│   │       ├── bot.py
│   │       └── handlers/
│   │           ├── chat.py
│   │           ├── command.py
│   │           └── schedule.py
│   ├── routes/                # API路由
│   │   ├── learning.py        # 学习进度
│   │   ├── chat.py           # 对话/苏格拉底
│   │   ├── questions.py       # 题目
│   │   ├── answers.py         # 答题
│   │   ├── wrong_questions.py # 错题本
│   │   ├── question_bank.py  # 题库管理
│   │   ├── upload.py         # 题库上传
│   │   ├── report.py         # 学习报告
│   │   ├── reminders.py      # 提醒
│   │   ├── knowledge.py      # 知识点
│   │   └── user.py           # 用户
│   └── prompts/               # AI提示词模板
├── database/                   # SQLite 数据库文件
├── requirements.txt
├── run.py
├── .env.example
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`：
```env
DEEPSEEK_API_KEY=your-deepseek-api-key
MINIMAX_API_KEY=your-minimax-api-key
DATABASE_PATH=./database/questions.db
```

### 3. 初始化数据库

```bash
python -m src.database.migrations.init_knowledge
```

### 4. 启动服务

```bash
python -m src.main
# 或
python run.py
```

服务启动在 `http://localhost:8081`

## 主要API接口

### 学习相关

| 接口 | 方法 | 说明 |
|------|------|------|
| `GET /api/learning/status` | 获取学习状态 |
| `GET /api/learning/current` | 获取当前知识点 |
| `GET /api/learning/progress/{id}` | 获取学习进度 |
| `GET /api/learning/mastery/{id}` | 获取掌握度状态 |
| `POST /api/learning/select-unit/{id}` | 选择学习单元 |
| `POST /api/learning/unlock-next/{id}` | 解锁下一单元 |
| `POST /api/learning/reset` | 重置学习地图 |

### 对话

| 接口 | 方法 | 说明 |
|------|------|------|
| `POST /api/chat` | 发送消息（苏格拉底问答） |
| `GET /api/chat/history` | 获取聊天历史 |

### 题库管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `GET /api/question-bank/list` | 获取题库列表 |
| `GET /api/question-bank/questions` | 获取题目列表 |
| `GET /api/question-bank/stats` | 获取题库统计 |
| `DELETE /api/question-bank/{id}` | 删除题目 |
| `PUT /api/question-bank/{id}/status` | 更新题目状态 |
| `POST /api/question-bank/approve/{id}` | 批准题目 |

### 题库上传

| 接口 | 方法 | 说明 |
|------|------|------|
| `POST /api/upload/questions` | 上传题库文件 |
| `GET /api/upload/templates` | 获取上传模板 |

### 题目练习

| 接口 | 方法 | 说明 |
|------|------|------|
| `GET /api/questions/{knowledge_id}` | 获取练习题 |
| `POST /api/answers` | 提交答案 |
| `GET /api/wrong-questions` | 获取错题本 |
| `POST /api/wrong-questions/{id}/master` | 标记已掌握 |

## 数据库表结构

### learning_progress（学习进度）

```sql
CREATE TABLE learning_progress (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    knowledge_point_id INTEGER,
    feyman_completed INTEGER DEFAULT 0,
    practice_completed INTEGER DEFAULT 0,
    test_completed INTEGER DEFAULT 0,
    mastery_percentage INTEGER DEFAULT 0,
    socratic_rounds INTEGER DEFAULT 0,
    last_socratic_at DATETIME
);
```

### questions（题目）

```sql
CREATE TABLE questions (
    id INTEGER PRIMARY KEY,
    type TEXT,              -- single/multi/judge
    content TEXT,
    options TEXT,           -- JSON格式
    answer TEXT,
    analysis TEXT,
    knowledge_point TEXT,
    difficulty INTEGER,
    source TEXT,
    status TEXT             -- pending/approved
);
```

### knowledge_points（知识点）

```sql
CREATE TABLE knowledge_points (
    id INTEGER PRIMARY KEY,
    code TEXT,
    name TEXT,
    chapter TEXT,
    stage TEXT,
    sort_order INTEGER,
    status TEXT             -- locked/unlocked/completed
);
```

## 题目上传格式

### JSON格式

```json
[
  {
    "type": "single",
    "content": "Cache的主要作用是？",
    "options": {"A": "加快CPU访问内存速度", "B": "增加内存容量"},
    "answer": "A",
    "analysis": "Cache位于CPU和内存之间..."
  }
]
```

### TXT格式

```
题目内容
A. 选项A
B. 选项B
C. 选项C
D. 选项D
答案: A
```

### 支持的参数

| 参数 | 说明 |
|------|------|
| `knowledge_point` | 关联知识点ID |
| `use_ai_parse` | 启用AI解析（默认true） |
| `ai_provider` | AI提供商：deepseek/minimax |

上传示例：
```bash
curl -X POST "http://localhost:8081/api/upload/questions?use_ai_parse=true&ai_provider=deepseek" \
  -F "file=@questions.json"
```

## 健康检查

```bash
curl http://localhost:8081/health
# 返回 {"status": "ok"}
```
