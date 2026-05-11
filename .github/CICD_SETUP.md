# GitHub Actions CI/CD 配置指南

> AI伴学系统 — GitHub Actions 工作流配置说明

---

## 工作流概览

| 文件 | 触发条件 | 用途 |
|------|----------|------|
| `ci.yml` | push / PR | 自动构建、测试、安全扫描 |
| `cd.yml` | push main / tag / 手动 | 自动部署到 Staging / Production |
| `pr-check.yml` | PR 创建/更新 | PR 快速检查 |
| `health-check.yml` | 每天 09:00 / 手动 | 生产环境巡检告警 |

---

## 必须配置的 GitHub Secrets

进入仓库 → Settings → Secrets and variables → Actions

### 🔑 应用密钥（必须）

| Secret 名称 | 说明 | 示例 |
|-------------|------|------|
| `MINIMAX_API_KEY` | MiniMax AI API Key | `eyJ...` |
| `DEEPSEEK_API_KEY` | DeepSeek API Key（可选） | `sk-...` |
| `FEISHU_APP_ID` | 飞书应用 ID | `cli_xxx` |
| `FEISHU_APP_SECRET` | 飞书应用密钥 | `xxx` |
| `FEISHU_VERIFICATION_TOKEN` | 飞书事件验证 Token | `xxx` |

### 🚀 部署密钥（部署时需要）

| Secret 名称 | 说明 |
|-------------|------|
| `SSH_PRIVATE_KEY` | 服务器 SSH 私钥（`~/.ssh/id_rsa`） |
| `STAGING_HOST` | Staging 服务器 IP/域名 |
| `STAGING_USER` | Staging SSH 用户名 |
| `PROD_HOST` | 生产服务器 IP/域名 |
| `PROD_USER` | 生产 SSH 用户名 |
| `DOCKER_USERNAME` | Docker Hub 用户名（可选） |
| `DOCKER_PASSWORD` | Docker Hub 密码（可选） |

---

## 必须配置的 GitHub Variables

进入仓库 → Settings → Secrets and variables → Actions → Variables

| Variable 名称 | 说明 | 示例 |
|--------------|------|------|
| `STAGING_URL` | Staging 环境 URL | `http://1.2.3.4:5001` |
| `STAGING_DEPLOY_PATH` | Staging 部署路径 | `/opt/ai-study-assistant` |
| `PRODUCTION_URL` | 生产环境 URL | `https://ai-study.example.com` |
| `PROD_DEPLOY_PATH` | 生产部署路径 | `/opt/ai-study-assistant` |
| `FEISHU_WEBHOOK` | 飞书机器人 Webhook URL（通知用） | `https://open.feishu.cn/...` |
| `DOCKER_ENABLED` | 是否启用 Docker 构建（可选） | `true` |

---

## 快速开始

### 1. 仅使用 CI（无需服务器）

只需配置应用密钥（MINIMAX_API_KEY 等），CI 流水线即可正常运行：
- 代码 push → 自动运行测试 + 安全扫描
- PR 提交 → 自动进行 PR 检查

### 2. 启用自动部署

**第一步：** 在服务器上创建 SSH 密钥对
```bash
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions
cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys
# 将私钥内容粘贴到 GitHub Secret: SSH_PRIVATE_KEY
cat ~/.ssh/github_actions
```

**第二步：** 配置服务器目录结构
```bash
sudo mkdir -p /opt/ai-study-assistant/{releases,shared}
sudo mkdir -p /opt/ai-study-assistant/shared/database
# 创建生产环境 .env
sudo nano /opt/ai-study-assistant/shared/.env
```

**第三步：** 配置 systemd 服务（可选）
```ini
# /etc/systemd/system/ai-study-assistant.service
[Unit]
Description=AI Study Assistant Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/ai-study-assistant/current/backend
ExecStart=/opt/ai-study-assistant/current/backend/venv/bin/python run.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 3. 发布正式版本

```bash
# 打 tag 即触发生产部署
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

---

## 部署流程图

```
代码推送到 main
      │
      ├── [CI 检查]
      │   ├── 后端测试（Python 3.10 + 3.11）
      │   ├── 前端文件检查
      │   └── 安全扫描
      │
      └── [CD 部署 → Staging]
          ├── 同步代码到服务器
          ├── 安装/更新依赖
          ├── 重启服务
          └── 健康检查

推送 tag（如 v1.0.0）
      │
      └── [CD 部署 → Production]
          ├── 创建发布包
          ├── 蓝绿部署（原子切换）
          ├── 健康检查
          ├── 创建 GitHub Release
          └── 飞书通知
```

---

## 常见问题

### Q: CI 一直因为 AI Key 无效而失败？
A: CI 环境使用 dummy key，模块导入检查不会真正调用 AI API。如果启动时报错，检查 settings.py 是否在启动时立即调用 API。

### Q: 如何只跑 CI 不部署？
A: push 到 `feature/*` 或 `develop` 分支只触发 CI，不触发 CD。

### Q: 紧急 hotfix 如何跳过测试直接部署？
A: 手动触发 CD workflow（workflow_dispatch），勾选 `skip_tests: true` 并选择目标环境。

### Q: 如何查看部署历史？
A: 进入 GitHub → Actions → CD - 自动部署，查看每次运行记录。
