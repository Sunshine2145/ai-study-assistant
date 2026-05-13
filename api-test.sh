#!/bin/bash
# AI伴学系统 - 全功能API测试脚本

API="http://localhost:5001"
FRONTEND="http://localhost:8081"
PASS=0
FAIL=0

check() {
  local name="$1"
  local method="$2"
  local url="$3"
  local data="$4"
  local expected_code="${5:-200}"

  if [ -n "$data" ]; then
    resp=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "$url" -H "Content-Type: application/json" -d "$data" 2>/dev/null)
  else
    resp=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "$url" 2>/dev/null)
  fi

  if [ "$resp" = "$expected_code" ]; then
    echo "  ✅ $name ($resp)"
    PASS=$((PASS + 1))
  else
    echo "  ❌ $name (expected $expected_code, got $resp)"
    FAIL=$((FAIL + 1))
  fi
}

echo "============================================"
echo "  AI伴学系统 全功能测试"
echo "============================================"

# ====== 1. 基础端点 ======
echo ""
echo "📋 1. 基础端点"
check "Health Check" GET "$API/health"
check "Root API" GET "$API/"
check "Frontend HTML" GET "$FRONTEND/index.html"
check "Frontend CSS" GET "$FRONTEND/css/style.css"
check "Frontend JS" GET "$FRONTEND/js/app.js"

# ====== 2. 认证模块 ======
echo ""
echo "📋 2. 认证模块"
check "用户注册" POST "$API/api/auth/register" "{\"username\":\"testuser$(date +%s)\",\"password\":\"test123\",\"nickname\":\"TestUser\",\"email\":\"test@test.com\"}"
check "用户登录" POST "$API/api/auth/login" '{"username":"user","password":"admin123"}'
check "登录失败" POST "$API/api/auth/login" '{"username":"user","password":"wrong"}' 401
check "获取当前用户(/me)" GET "$API/api/auth/me"
check "获取当前用户(/current)" GET "$API/api/auth/current"
check "发送验证码" POST "$API/api/auth/send-code" '{"username":"user"}'
check "重复注册" POST "$API/api/auth/register" '{"username":"user","password":"test123"}' 400

# ====== 3. 学习状态 ======
echo ""
echo "📋 3. 学习状态模块"
check "学习状态总览" GET "$API/api/learning/status"
check "当前知识点" GET "$API/api/learning/current"
check "选择学习单元" POST "$API/api/learning/select-unit/1"
check "获取掌握度" GET "$API/api/learning/mastery/1"
check "获取学习进度" GET "$API/api/learning/progress/1"
check "检查可练习" GET "$API/api/learning/can-practice/1"

# ====== 4. 知识点模块 ======
echo ""
echo "📋 4. 知识点模块"
check "知识点列表" GET "$API/api/knowledge"
check "知识点筛选(第一阶段)" GET "$API/api/knowledge?stage=%E7%AC%AC%E4%B8%80%E9%98%B6%E6%AE%B5"
check "知识点详情(按code)" GET "$API/api/knowledge/1.1"
check "知识点导出" GET "$API/api/knowledge/export"

# ====== 5. 题目模块 ======
echo ""
echo "📋 5. 题目模块"
check "题目列表" GET "$API/api/questions"
check "题目获取(knowledge_id=1)" GET "$API/api/questions/1"
check "题目导出" GET "$API/api/questions/export"

# ====== 6. 答题模块 ======
echo ""
echo "📋 6. 答题模块"
check "答题统计" GET "$API/api/answers/stats"

# ====== 7. 错题本 ======
echo ""
echo "📋 7. 错题本模块"
check "错题本(周)" GET "$API/api/wrong-questions?filter=week"
check "错题本(月)" GET "$API/api/wrong-questions?filter=month"
check "错题本(全部)" GET "$API/api/wrong-questions?filter=all"

# ====== 8. 学习报告 ======
echo ""
echo "📋 8. 学习报告模块"
check "学习报告" GET "$API/api/report"

# ====== 9. 题库管理 ======
echo ""
echo "📋 9. 题库管理模块"
check "题库列表" GET "$API/api/question-bank/list"
check "题库统计" GET "$API/api/question-bank/stats"
check "题目列表(分页)" GET "$API/api/question-bank/questions"

# ====== 10. 上传模块 ======
echo ""
echo "📋 10. 上传模块"
check "上传模板" GET "$API/api/upload/templates"

# ====== 11. AI问答 ======
echo ""
echo "📋 11. AI问答模块"
check "问答历史" GET "$API/api/ai-qa/history"

# ====== 12. 提醒模块 ======
echo ""
echo "📋 12. 提醒模块"
check "提醒列表" GET "$API/api/reminders"

# ====== 13. 用户管理(Admin) ======
echo ""
echo "📋 13. 用户管理模块"
check "用户列表" GET "$API/api/admin/users/list"
check "用户详情" GET "$API/api/admin/users/1"

# ====== 14. 学习进度完整流程 ======
echo ""
echo "📋 14. 学习流程完整测试"
# 选择知识点1开始学习
check "14.1 选择知识点" POST "$API/api/learning/select-unit/1"
# 标记费曼完成
check "14.2 标记费曼完成" POST "$API/api/learning/progress/1/complete?step=feynman"
# 检查解锁
check "14.3 解锁检查" POST "$API/api/learning/unlock-next/1"
# 重置
check "14.4 重置学习" POST "$API/api/learning/reset"

# ====== 15. 上传进度 ======
echo ""
echo "📋 15. 上传进度模块"
check "创建上传进度" POST "$API/api/upload/progress?file_name=test.pdf&file_size=1024"

# ====== 结果汇总 ======
echo ""
echo "============================================"
echo "📊 测试结果: $PASS 通过, $FAIL 失败 ($((PASS + FAIL)) 总数)"
echo "============================================"

if [ $FAIL -gt 0 ]; then
  exit 1
fi
exit 0
