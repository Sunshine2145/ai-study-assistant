# AI伴学系统 — 单元测试结果清单

| 项目 | 值 |
|------|-----|
| 执行时间 | 2026-05-17 |
| 测试框架 | pytest 9.0.2 |
| Python 版本 | 3.11.2 |
| 测试数据库 | `backend/database/test_questions.db`（隔离 SQLite） |
| 用例总数 | **46** |
| 通过 | **46** |
| 失败 | **0** |
| 跳过 | **0** |
| 耗时 | ~3s |
| JUnit 报告 | `backend/tests/junit-report.xml` |

## 运行方式

```bash
cd backend
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest tests/ -v
```

---

## 测试结果总览

| 模块 | 文件 | 用例数 | 通过 | 失败 |
|------|------|--------|------|------|
| 健康检查 API | `test_api_health.py` | 2 | 2 | 0 |
| 认证 API | `test_auth_api.py` | 11 | 11 | 0 |
| 数据库 SQL 转换 | `test_database_sql.py` | 6 | 6 | 0 |
| 文档分类器 | `test_classifier.py` | 5 | 5 | 0 |
| 知识点服务/API | `test_knowledge_service.py` | 5 | 5 | 0 |
| 学习进度 API | `test_learning_api.py` | 5 | 5 | 0 |
| 题目服务/API | `test_questions_service.py` | 8 | 8 | 0 |
| 答题 API | `test_answers_api.py` | 4 | 4 | 0 |
| **合计** | | **46** | **46** | **0** |

---

## 详细用例清单

### 1. 健康检查 API (`test_api_health.py`)

| # | 用例 ID | 描述 | 结果 |
|---|---------|------|------|
| 1 | `test_root_returns_api_info` | GET `/` 返回 API 名称与版本 | ✅ PASS |
| 2 | `test_health_returns_ok` | GET `/health` 返回 `{"status":"ok"}` | ✅ PASS |

### 2. 认证模块 (`test_auth_api.py`)

| # | 用例 ID | 描述 | 结果 |
|---|---------|------|------|
| 3 | `test_hash_password_is_sha256_hex` | 密码哈希为 SHA256 十六进制 | ✅ PASS |
| 4 | `test_generate_verification_code_length` | 验证码为 6 位数字 | ✅ PASS |
| 5 | `test_register_success` | POST `/api/auth/register` 注册成功 | ✅ PASS |
| 6 | `test_register_duplicate_username` | 重复用户名返回 400 | ✅ PASS |
| 7 | `test_login_success` | POST `/api/auth/login` 登录成功 | ✅ PASS |
| 8 | `test_login_wrong_password` | 错误密码返回 401 | ✅ PASS |
| 9 | `test_login_nonexistent_user` | 不存在用户返回 401 | ✅ PASS |
| 10 | `test_get_me_returns_user_shape` | GET `/api/auth/me` 字段完整 | ✅ PASS |
| 11 | `test_get_current_user_full` | GET `/api/auth/current` 完整用户信息 | ✅ PASS |
| 12 | `test_send_and_login_with_code` | 发送验证码 + 验证码登录流程 | ✅ PASS |
| 13 | `test_login_code_invalid` | 错误验证码返回 400 | ✅ PASS |

### 3. 数据库 SQL 方言转换 (`test_database_sql.py`)

| # | 用例 ID | 描述 | 结果 |
|---|---------|------|------|
| 14 | `test_placeholder_conversion` | `?` → `%s` 占位符转换 | ✅ PASS |
| 15 | `test_date_now_conversion` | `DATE('now')` → `CURDATE()` | ✅ PASS |
| 16 | `test_datetime_days_conversion` | `datetime('now', '-7 days')` → `DATE_SUB` | ✅ PASS |
| 17 | `test_on_conflict_conversion` | `ON CONFLICT` → `ON DUPLICATE KEY UPDATE` | ✅ PASS |
| 18 | `test_autoincrement_conversion` | `AUTOINCREMENT` → `AUTO_INCREMENT` | ✅ PASS |
| 19 | `test_plain_sql_unchanged` | 普通 SQL 不被误改 | ✅ PASS |

### 4. AI 文档分类器 (`test_classifier.py`)

| # | 用例 ID | 描述 | 结果 |
|---|---------|------|------|
| 20 | `test_parse_valid_json` | 解析合法 JSON 分类结果 | ✅ PASS |
| 21 | `test_parse_json_embedded_in_text` | 从混合文本中提取 JSON | ✅ PASS |
| 22 | `test_parse_invalid_returns_fallback` | 非法 JSON 返回默认 `other` | ✅ PASS |
| 23 | `test_classify_success_mocked` | Mock API 成功返回分类（异步） | ✅ PASS |
| 24 | `test_classify_api_failure_returns_fallback` | API 异常时降级返回 | ✅ PASS |

### 5. 知识点模块 (`test_knowledge_service.py`)

| # | 用例 ID | 描述 | 结果 |
|---|---------|------|------|
| 25 | `test_create_get_update_delete` | 知识点 CRUD 全流程 | ✅ PASS |
| 26 | `test_create_duplicate_code_raises` | 重复 code 抛出 ValueError | ✅ PASS |
| 27 | `test_list_knowledge_points` | GET `/api/knowledge` 列表 | ✅ PASS |
| 28 | `test_get_knowledge_by_code` | GET `/api/knowledge/{code}` | ✅ PASS |
| 29 | `test_get_nonexistent_knowledge_returns_404` | 不存在 code 返回 404 | ✅ PASS |

### 6. 学习进度 API (`test_learning_api.py`)

| # | 用例 ID | 描述 | 结果 |
|---|---------|------|------|
| 30 | `test_learning_status_empty_db_defaults` | GET `/api/learning/status` 默认结构 | ✅ PASS |
| 31 | `test_learning_status_with_user_and_kp` | 有用户/知识点时状态统计 | ✅ PASS |
| 32 | `test_get_current_knowledge` | GET `/api/learning/current` | ✅ PASS |
| 33 | `test_select_unit` | POST `/api/learning/select-unit/{id}` | ✅ PASS |
| 34 | `test_mastery_endpoint` | GET `/api/learning/mastery/{id}` 掌握度字段 | ✅ PASS |

### 7. 题目模块 (`test_questions_service.py`)

| # | 用例 ID | 描述 | 结果 |
|---|---------|------|------|
| 35 | `test_create_and_get_by_id` | QuestionService 创建与查询 | ✅ PASS |
| 36 | `test_list_all_with_filter` | 按 source 过滤列表 | ✅ PASS |
| 37 | `test_update_and_delete` | 更新与删除题目 | ✅ PASS |
| 38 | `test_batch_import` | 批量导入 2 道题 | ✅ PASS |
| 39 | `test_get_stats` | 题库统计字段完整 | ✅ PASS |
| 40 | `test_create_question_via_api` | POST `/api/questions` 创建 | ✅ PASS |
| 41 | `test_list_questions_pagination` | 分页列表 API | ✅ PASS |
| 42 | `test_get_questions_by_knowledge_id_returns_data` | GET `/api/questions/{id}` | ✅ PASS |

### 8. 答题 API (`test_answers_api.py`)

| # | 用例 ID | 描述 | 结果 |
|---|---------|------|------|
| 43 | `test_submit_correct_answer` | 答对返回 `correct: true` | ✅ PASS |
| 44 | `test_submit_wrong_answer_records_wrong` | 答错返回 `correct: false` | ✅ PASS |
| 45 | `test_submit_nonexistent_question` | 不存在题目返回错误信息 | ✅ PASS |
| 46 | `test_answer_stats` | GET `/api/answers/stats` 统计 | ✅ PASS |

---

## 测试文件结构

```
backend/tests/
├── conftest.py              # 隔离测试库、TestClient、公共 fixture
├── test_api_health.py       # 根路由与健康检查
├── test_auth_api.py         # 注册/登录/验证码
├── test_database_sql.py     # SQLite→MySQL SQL 转换
├── test_classifier.py       # AI 分类器（Mock，无真实 API）
├── test_knowledge_service.py
├── test_learning_api.py
├── test_questions_service.py
├── test_answers_api.py
├── junit-report.xml         # CI 可消费的 JUnit 报告
└── TEST_RESULTS.md          # 本清单
```

## 未覆盖范围（后续可补充）

- 飞书 Webhook 回调 (`/feishu/*`)
- PDF/文件上传与 AI 解析 (`/api/upload/*`)
- 费曼/苏格拉底 AI 对话（需 Mock `AIService`）
- 管理员用户管理 (`/api/admin/*`)
- MySQL 双库模式集成测试

## 结论

**全部 46 项单元测试通过**，核心 API（认证、学习、题目、答题、知识点）与数据库工具函数行为符合预期。测试使用独立 SQLite 文件，不影响开发库 `questions.db`。
