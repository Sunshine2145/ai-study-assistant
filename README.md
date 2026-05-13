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
| 上传进度 | 实时显示文件上传和解析进度 |
| 学习进度追踪 | 掌握度百分比、连续天数、积分 |
| 用户管理 | 注册登录、角色权限管理（管理员/用户） |
| AI问答 | 智能问答助手，解答学习疑问 |

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
│   │       ├── upload.py      # 题库上传
│   │       ├── ai_qa.py      # AI问答
│   │       ├── auth.py       # 用户认证
│   │       ├── admin_user.py  # 用户管理
│   │       └── upload_progress.py # 上传进度
│   └── requirements.txt
├── frontend/                    # 前端
│   ├── index.html             # 主页面
│   ├── css/style.css          # 样式
│   └── js/app.js              # 主逻辑
├── AI伴学系统_PRD_v1.0.md      # 产品需求文档
└── README.md                  # 项目文档
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
# 服务运行在 http://localhost:5001
```

### 4. 启动前端服务

```bash
cd frontend
npx serve -l 5000
# 访问 http://localhost:5000
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

### 用户认证

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/auth/register` | POST | 用户注册 |
| `/api/auth/login` | POST | 用户登录 |
| `/api/auth/current` | GET | 获取当前用户信息 |
| `/api/auth/me` | GET | 获取当前用户（简化版） |

### 用户管理（管理员）

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/admin/users/list` | GET | 获取用户列表 |
| `/api/admin/users/{user_id}` | GET | 获取指定用户 |
| `/api/admin/users/{user_id}` | PUT | 更新用户信息 |
| `/api/admin/users/{user_id}/permissions` | PUT | 更新用户权限 |
| `/api/admin/users/{user_id}/ban` | POST | 禁用用户 |
| `/api/admin/users/{user_id}/unban` | POST | 启用用户 |

### 上传进度

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/upload/progress` | POST | 创建上传任务 |
| `/api/upload/progress/{id}` | GET | 获取上传进度 |
| `/api/upload/progress/{id}` | PUT | 更新上传进度 |

### AI问答

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/ai-qa/chat` | POST | 发送AI问答消息 |
| `/api/ai-qa/history` | GET | 获取对话历史 |
| `/api/ai-qa/clear` | POST | 清除对话历史 |

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

### users（用户表 - 扩展）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| username | VARCHAR(50) | 用户名（唯一） |
| password_hash | VARCHAR(255) | 密码哈希 |
| nickname | VARCHAR(50) | 昵称 |
| email | VARCHAR(255) | 邮箱 |
| role | VARCHAR(20) | 角色：admin/user |
| permissions | TEXT | 权限JSON数组 |
| status | VARCHAR(20) | 状态：active/banned |
| score | INTEGER | 积分 |
| streak | INTEGER | 连续学习天数 |

### user_permissions（用户权限表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 用户ID |
| module | VARCHAR(50) | 功能模块名 |

### upload_progress（上传进度表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 用户ID |
| file_name | VARCHAR(255) | 文件名 |
| file_size | INTEGER | 文件大小 |
| status | VARCHAR(20) | 状态：processing/completed/failed |
| progress | INTEGER | 进度百分比 |
| stage | VARCHAR(50) | 当前阶段 |
| total_questions | INTEGER | 总题目数 |
| processed_questions | INTEGER | 已处理题目数 |
| error_message | TEXT | 错误信息 |

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
curl http://localhost:5001/health

# 前端访问
curl http://localhost:5000
```

## 常见问题

### Q: 如何修改端口？
A: 后端端口在 `backend/src/main.py` 中修改 `uvicorn.run(port=5001)`；前端使用 `npx serve -l <端口号>`

### Q: 默认管理员账号？
A: 首次启动后，使用用户名 `tanxiaolei`，密码 `admin123` 登录，角色为管理员

### Q: 如何添加新用户？
A: 在登录页面点击"注册新账号"进行注册，管理员可在用户管理页面分配权限

## 许可证

MIT License
