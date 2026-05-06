# AI伴学系统 - 智能备考助手

基于**费曼学习法 + 苏格拉底提问法**的智能备考助手，帮助通过2026年11月系统架构师考试。

## 核心功能

| 功能 | 说明 |
|------|------|
| 费曼讲解 | AI用生活化类比讲解知识点 |
| 苏格拉底追问 | AI连续追问引导深入思考，90%掌握度门槛 |
| 题目练习 | 学完即练，检验理解 |
| 答案解析 | 详细解析，不只告诉对错 |
| 题库导入 | 支持PDF/TXT/JSON/MD格式，AI智能解析 |
| 题库管理 | 查看题库列表、题目、筛选、审核 |
| 学习进度追踪 | 掌握度百分比、连续天数、积分 |

## 学习流程

```
┌─────────────────────────────────────────────────────────────┐
│  学习地图 → 选择单元 → 费曼学习 → 苏格拉底提问 → 90%门槛 → 练习 → 解锁下一单元  │
└─────────────────────────────────────────────────────────────┘

1️⃣ 学习地图
   └─> 显示完整知识体系结构和章节关联

2️⃣ 选择学习单元
   └─> 从地图选择特定章节，自动跳转学习环节

3️⃣ 费曼学习法教学
   └─> 生活化类比讲解
   └─> 用户用自己的语言复述核心知识点

4️⃣ 苏格拉底提问法验证
   └─> 持续追问引导深入思考
   └─> 每轮更新掌握度百分比
   └─> 需达到90%掌握度 + 完成3轮对话

5️⃣ 题目练习
   └─> 90%门槛解锁
   └─> 答题正确/错误均有详细解析

6️⃣ 解锁下一单元
   └─> 自动解锁下一知识点
```

## 项目结构

```
ai-study-assistant/
├── backend/                     # FastAPI 后端
│   ├── src/
│   │   ├── main.py            # 入口
│   │   ├── config/            # 配置
│   │   ├── database/          # SQLite 数据库
│   │   │   └── db.py
│   │   ├── modules/
│   │   │   ├── ai/            # AI 服务
│   │   │   │   ├── feynman.py      # 费曼讲解
│   │   │   │   ├── socratic.py     # 苏格拉底追问
│   │   │   │   └── pdf_parser.py   # PDF 解析
│   │   │   └── feishu/        # 飞书机器人
│   │   └── routes/            # API 路由
│   │       ├── learning.py    # 学习进度
│   │       ├── chat.py        # 对话
│   │       ├── questions.py   # 题目
│   │       ├── question_bank.py  # 题库管理
│   │       └── upload.py      # 题库上传
│   └── requirements.txt
├── frontend/                    # 前端
│   ├── index.html             # 主页面
│   ├── css/style.css          # 样式
│   └── js/app.js              # 主逻辑
└── AI伴学系统_PRD_v1.0.md      # 产品需求文档
```

## 快速开始

### 环境要求

- Python 3.9+
- Node.js 16+
- SQLite

### 1. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp backend/.env.example backend/.env
# 编辑 .env 填入配置：
#   DEEPSEEK_API_KEY=你的DeepSeek API密钥
#   MINIMAX_API_KEY=你的MiniMax API密钥
```

### 3. 启动后端服务

```bash
cd backend
python -m src.main
# 服务运行在 http://localhost:8081
```

### 4. 启动前端服务

```bash
cd frontend
npx serve -l 3000
# 访问 http://localhost:3000
```

## 技术栈

| 组件 | 选型 |
|------|------|
| 后端框架 | FastAPI + Uvicorn |
| 数据库 | SQLite |
| AI模型 | DeepSeek / MiniMax |
| PDF解析 | PyMuPDF |
| 前端 | 原生 HTML/CSS/JS |

## 主要API接口

### 学习相关

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/learning/status` | GET | 获取学习状态 |
| `/api/learning/current` | GET | 获取当前知识点 |
| `/api/learning/progress/{id}` | GET | 获取学习进度 |
| `/api/learning/mastery/{id}` | GET | 获取掌握度状态 |
| `/api/learning/select-unit/{id}` | POST | 选择学习单元 |
| `/api/learning/unlock-next/{id}` | POST | 解锁下一单元 |
| `/api/learning/reset` | POST | 重置学习地图 |
| `/api/chat` | POST | 发送消息（苏格拉底问答） |

### 题库相关

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/question-bank/list` | GET | 获取题库列表 |
| `/api/question-bank/questions` | GET | 获取题目列表 |
| `/api/question-bank/stats` | GET | 获取题库统计 |
| `/api/upload/questions` | POST | 上传题库文件 |
| `/api/questions/{id}` | GET | 获取题目 |

### 题目练习

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/questions/{knowledge_id}` | GET | 获取练习题 |
| `/api/answers` | POST | 提交答案 |
| `/api/wrong-questions` | GET | 获取错题本 |

## 数据库表结构

### learning_progress（学习进度表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 用户ID |
| knowledge_point_id | INTEGER | 知识点ID |
| feyman_completed | INTEGER | 费曼学习是否完成 |
| practice_completed | INTEGER | 练习是否完成 |
| mastery_percentage | INTEGER | 掌握度百分比(0-100) |
| socratic_rounds | INTEGER | 苏格拉底问答轮数 |
| last_socratic_at | DATETIME | 最后苏格拉底互动时间 |

### questions（题目表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| type | TEXT | 题型：single/multi/judge |
| content | TEXT | 题目内容 |
| options | TEXT | 选项（JSON格式） |
| answer | TEXT | 答案 |
| analysis | TEXT | 解析 |
| knowledge_point | TEXT | 知识点标签 |
| source | TEXT | 来源 |
| status | TEXT | 状态：pending/approved |

## 题目上传格式

### JSON格式

```json
[
  {
    "type": "single",
    "content": "Cache的主要作用是？",
    "options": {"A": "加快CPU访问内存速度", "B": "增加内存容量", "C": "降低功耗", "D": "提高可靠性"},
    "answer": "A",
    "analysis": "Cache位于CPU和内存之间，用于暂存CPU常用的数据，加快访问速度。"
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
---
判断题示例
答案: 对
```

## 学习地图初始知识点

| 阶段 | 知识点数量 | 说明 |
|------|------------|------|
| 第一阶段 | ~25个 | 计算机系统基本知识 |
| 第二阶段 | ~15个 | 信息系统基础 |
| 第三阶段 | ~10个 | 信息安全技术 |
| 第四阶段 | ~15个 | 软件工程 |
| 第五阶段 | ~10个 | 数据库设计 |
| 第六阶段 | ~15个 | 系统架构设计 |
| 第七阶段 | ~10个 | 架构评估与可靠性 |
| 第八阶段 | ~8个 | 软件架构演化维护 |

## 环境变量说明

```env
# AI API 配置
DEEPSEEK_API_KEY=your-deepseek-api-key
MINIMAX_API_KEY=your-minimax-api-key

# 飞书机器人配置（可选）
FEISHU_APP_ID=your-app-id
FEISHU_APP_SECRET=your-app-secret

# 数据库配置
DATABASE_PATH=./database/questions.db
```

## 开发说明

### 目录结构

- `backend/` - FastAPI 后端服务
- `frontend/` - 前端（原生 HTML/CSS/JS）
- `database/` - SQLite 数据库文件
- `AI伴学系统_PRD_v1.0.md` - 产品需求文档

### 主要依赖

```
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.0.0
python-multipart>=0.0.6
python-dotenv>=1.0.0
loguru>=0.7.0
aiohttp>=3.9.0
pymupdf>=1.23.0
```

### 启动检查

```bash
# 后端健康检查
curl http://localhost:8081/health

# 前端访问
curl http://localhost:3000
```

## 许可证

MIT License
