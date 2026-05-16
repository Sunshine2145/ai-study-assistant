/**
 * AI伴学系统 - 主JavaScript文件
 * 实现界面交互功能 + API集成
 */

// ========================================
// 配置
// ========================================
const API_BASE = 'http://localhost:5001/api';

// ========================================
// 状态管理
// ========================================
const state = {
    user: null,
    currentKnowledge: null,
    questions: [],
    currentQuestionIndex: 0,
    wrongQuestions: [],
    stageData: [],
    learningPhase: 'feynman'
};

// ========================================
// API服务
// ========================================
const api = {
    async request(endpoint, options = {}) {
        try {
            const response = await fetch(`${API_BASE}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            return null;
        }
    },

    async getUser() { return await this.request('/auth/current'); },
    async getLearningStatus() { return await this.request('/learning/status'); },
    async getKnowledgePoints(stage = null) {
        const url = stage ? `/knowledge?stage=${stage}` : '/knowledge';
        return await this.request(url);
    },
    async getCurrentKnowledge() { return await this.request('/learning/current'); },
    async sendMessage(content) {
        const knowledgeId = state.currentKnowledge?.id;
        return await this.request('/chat', {
            method: 'POST',
            body: JSON.stringify({ content, knowledge_id: knowledgeId })
        });
    },
    async getQuestions(knowledgeId) { return await this.request(`/questions/${knowledgeId}`); },
    async submitAnswer(questionId, answer) {
        return await this.request('/answers', {
            method: 'POST',
            body: JSON.stringify({ question_id: questionId, answer })
        });
    },
    async getWrongQuestions(filter = 'week') {
        return await this.request(`/wrong-questions?filter=${filter}`);
    },
    async getReport(date = null) {
        const url = date ? `/report?date=${date}` : '/report';
        return await this.request(url);
    },
    async getReminders() { return await this.request('/reminders'); },
    async uploadQuestions(formData, useAiParse = true, aiProvider = 'deepseek') {
        try {
            const params = useAiParse
                ? `?use_ai_parse=true&ai_provider=${aiProvider}`
                : `?use_ai_parse=false`;
            const url = `${API_BASE}/upload/questions${params}`;
            const response = await fetch(url, {
                method: 'POST',
                body: formData
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Upload Error:', error);
            return { success: false, message: error.message };
        }
    },
    async getUploadTemplate() {
        return await this.request('/upload/templates');
    },
    async getQuestionBanks() { return await this.request('/question-bank/list'); },
    async getQuestionBankQuestions(source, page = 1, pageSize = 20) {
        const params = new URLSearchParams({ source, page: page.toString(), page_size: pageSize.toString() });
        return await this.request(`/question-bank/questions?${params}`);
    },
    async getQuestionBankStats() { return await this.request('/question-bank/stats'); },
    async deleteQuestion(questionId) {
        return await this.request(`/question-bank/${questionId}`, { method: 'DELETE' });
    },
    async updateQuestionStatus(questionId, status) {
        return await this.request(`/question-bank/${questionId}/status`, {
            method: 'PUT',
            body: JSON.stringify({ status })
        });
    },
    async approveQuestion(questionId) {
        return await this.request(`/question-bank/approve/${questionId}`, { method: 'POST' });
    },
    async deleteBank(source) {
        // Use query parameter to avoid URL encoding issues
        return await this.request(`/question-bank/bank?source=${encodeURIComponent(source)}`, { method: 'DELETE' });
    },
    async getLearningProgress(knowledgeId) { return await this.request(`/learning/progress/${knowledgeId}`); },
    async completeLearningStep(knowledgeId, step) {
        return await this.request(`/learning/progress/${knowledgeId}/complete?step=${step}`, { method: 'POST' });
    },
    async canPractice(knowledgeId) { return await this.request(`/learning/can-practice/${knowledgeId}`); },
    async selectLearningUnit(knowledgeId) {
        return await this.request(`/learning/select-unit/${knowledgeId}`, { method: 'POST' });
    },
    async getMastery(knowledgeId) { return await this.request(`/learning/mastery/${knowledgeId}`); },
    async unlockNext(knowledgeId) {
        return await this.request(`/learning/unlock-next/${knowledgeId}`, { method: 'POST' });
    },
    async resetLearning() { return await this.request('/learning/reset', { method: 'POST' }); },
    async getFeynmanContent(knowledgeId) {
        return await this.request(`/learning/feynman/${knowledgeId}`);
    },
    // 用户管理
    async login(username, password) {
        return await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
    },
    async register(username, password, nickname) {
        return await this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ username, password, nickname })
        });
    },
    async loginWithCode(username, code) {
        return await this.request('/auth/login-code', {
            method: 'POST',
            body: JSON.stringify({ username, code })
        });
    },
    async sendSmsCode(username) {
        return await this.request('/auth/send-code', {
            method: 'POST',
            body: JSON.stringify({ username })
        });
    },
    async logout() {
        return await this.request('/auth/logout', { method: 'POST' });
    },
    async getUserList() {
        return await this.request('/admin/users/list');
    },
    async getUserById(userId) {
        return await this.request(`/admin/users/${userId}`);
    },
    async updateUser(userId, data) {
        return await this.request(`/admin/users/${userId}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    async updateUserPermissions(userId, permissions) {
        return await this.request(`/admin/users/${userId}/permissions`, {
            method: 'PUT',
            body: JSON.stringify({ user_id: userId, permissions })
        });
    },
    async banUser(userId) {
        return await this.request(`/admin/users/${userId}/ban`, { method: 'POST' });
    },
    async unbanUser(userId) {
        return await this.request(`/admin/users/${userId}/unban`, { method: 'POST' });
    },
    async createUser(data) {
        return await this.request('/admin/users', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    async resetPassword(userId, password) {
        return await this.request(`/admin/users/${userId}/reset-password`, {
            method: 'POST',
            body: JSON.stringify({ password })
        });
    },
    // 上传进度
    async getUploadProgress(uploadId) {
        return await this.request(`/upload/progress/${uploadId}`);
    }
};

// ========================================
// 页面导航
// ========================================
function navigateTo(page) {
    const pages = document.querySelectorAll('.page');
    pages.forEach(p => { p.style.display = 'none'; p.classList.remove('active'); });

    const targetPage = document.getElementById(`page-${page}`);
    if (targetPage) { targetPage.style.display = 'block'; targetPage.classList.add('active'); }

    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => item.classList.remove('active'));

    const activeNav = document.querySelector(`.nav-item[data-page="${page}"]`);
    if (activeNav) activeNav.classList.add('active');

    const pageTitles = { 'home': '学习首页', 'learn': '开始学习', 'map': '学习地图', 'practice': '题目练习', 'wrong': '错题本', 'report': '学习报告', 'upload': '题库上传', 'question-bank': '题库管理', 'ai-qa': 'AI问答', 'user-management': '用户管理', 'login': '登录', 'register': '注册' };
    const pageTitle = document.getElementById('pageTitle');
    if (pageTitle && pageTitles[page]) pageTitle.textContent = pageTitles[page];

    const sidebar = document.getElementById('sidebar');
    // Hide sidebar for login/register pages
    if (page === 'login' || page === 'register') {
        sidebar.style.display = 'none';
    } else {
        sidebar.style.display = 'flex';
        if (window.innerWidth <= 1024) sidebar.classList.remove('open');
    }

    loadPageData(page);
}

// ========================================
// 页面数据加载
// ========================================
async function loadPageData(page) {
    switch (page) {
        case 'home': await loadHomeData(); break;
        case 'learn': await loadLearnData(); break;
        case 'map': await loadMapData(); break;
        case 'practice': await loadPracticeData(); break;
        case 'wrong': await loadWrongData(); break;
        case 'report': await loadReportData(); break;
        case 'upload': await loadUploadData(); break;
        case 'question-bank': await loadQuestionBankData(); break;
        case 'user-management': await loadUserManagementData(); break;
    }
}

async function loadHomeData() {
    const status = await api.getLearningStatus();
    if (!status) { updateHomeWithDemoData(); return; }

    document.getElementById('userName').textContent = status.user_name || '学员';
    document.getElementById('streakDays').textContent = status.streak || 0;
    document.getElementById('totalPoints').textContent = status.total_points || 0;

    const now = new Date();
    document.getElementById('currentDate').textContent = `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日`;
    document.getElementById('learnDays').textContent = status.learn_days || 0;
    document.getElementById('streakBadge').textContent = `连续${status.streak || 0}天`;

    const hour = now.getHours();
    let greeting = hour < 12 ? '早上好' : hour < 18 ? '下午好' : '晚上好';
    document.getElementById('greetingText').textContent = `${greeting}！👋`;

    if (status.current_knowledge) {
        document.getElementById('todayTitle').textContent = status.current_knowledge;
        document.getElementById('todayDuration').textContent = status.estimated_time || '预计学习时长：15分钟';
        document.getElementById('greetingDesc').textContent = status.next_learning_tip || '继续学习下一个知识点';
    }

    document.getElementById('statKnowledge').textContent = `${status.completed_count || 0}/${status.total_count || 0}`;
    document.getElementById('statStreak').textContent = status.streak || 0;
    document.getElementById('statPoints').textContent = status.total_points || 0;
    document.getElementById('statWrong').textContent = status.wrong_count || 0;

    const progress = status.total_count > 0 ? (status.completed_count / status.total_count * 100).toFixed(1) : 0;
    document.getElementById('totalProgress').style.width = `${progress}%`;
    document.getElementById('totalPercent').textContent = `${progress}%`;

    const reminders = await api.getReminders();
    const badge = document.getElementById('reminderBadge');
    if (reminders && reminders.length > 0) { badge.textContent = reminders.length; badge.style.display = 'block'; }
    else { badge.style.display = 'none'; }
}

function updateHomeWithDemoData() {
    const now = new Date();
    document.getElementById('currentDate').textContent = `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日`;
    document.getElementById('userName').textContent = '谭晓磊';
    document.getElementById('streakDays').textContent = '2';
    document.getElementById('totalPoints').textContent = '25';
    document.getElementById('learnDays').textContent = '2';
    document.getElementById('streakBadge').textContent = '连续2天';
    const hour = now.getHours();
    let greeting = hour < 12 ? '早上好' : hour < 18 ? '下午好' : '晚上好';
    document.getElementById('greetingText').textContent = `${greeting}！👋`;
    document.getElementById('greetingDesc').textContent = '继续学习下一个知识点';
    document.getElementById('todayTitle').textContent = '1.2.4 存储器';
    document.getElementById('todayDuration').textContent = '预计学习时长：15分钟';
    document.getElementById('statKnowledge').textContent = '1/45';
    document.getElementById('statStreak').textContent = '2';
    document.getElementById('statPoints').textContent = '25';
    document.getElementById('statWrong').textContent = '5';
    document.getElementById('totalProgress').style.width = '2.2%';
    document.getElementById('totalPercent').textContent = '2.2%';
    document.getElementById('reminderBadge').textContent = '3';
}

async function loadLearnData() {
    const current = await api.getCurrentKnowledge();
    const chatMessages = document.getElementById('chatMessages');
    if (!current) {
        chatMessages.innerHTML = `<div class="message ai-message"><div class="message-avatar"><i class="fas fa-robot"></i></div><div class="message-content"><div class="message-sender">AI伴学助手</div><div class="message-text"><p>欢迎来到AI伴学系统！</p><p>请从学习地图选择一个知识点开始学习。</p></div><div class="message-time">${getCurrentTime()}</div></div></div>`;
        document.getElementById('socraticText').textContent = '请从学习地图选择知识点';
        return;
    }
    state.currentKnowledge = current;

    await loadLearnDataWithFeynman(current.id);
}

async function loadMapData() {
    const result = await api.getKnowledgePoints();
    const stageTabs = document.getElementById('stageTabs');
    const knowledgePointsEl = document.getElementById('knowledgePoints');
    const stageInfoEl = document.getElementById('stageInfo');
    if (!result || !result.data || result.data.length === 0) {
        stageTabs.innerHTML = '';
        knowledgePointsEl.innerHTML = '<div style="text-align:center;padding:48px;color:#64748b;"><i class="fas fa-map" style="font-size:48px;margin-bottom:16px;display:block;"></i><p>暂无知识点数据</p><p style="font-size:13px;margin-top:8px;">请稍后刷新页面重试</p></div>';
        if (stageInfoEl) stageInfoEl.style.display = 'none';
        return;
    }
    if (stageInfoEl) stageInfoEl.style.display = '';
    state.stageData = result.data;
    const cnNum = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10};
    const stages = [...new Set(result.data.map(k => k.stage))].sort((a, b) => {
        const mA = a.match(/[一二三四五六七八九十]/);
        const mB = b.match(/[一二三四五六七八九十]/);
        return (cnNum[mA?.[0]] || 0) - (cnNum[mB?.[0]] || 0);
    });
    stageTabs.innerHTML = stages.map((stage, index) => `<button class="stage-tab ${index === 0 ? 'active' : ''}" data-stage="${stage}">${stage}</button>`).join('');
    initStageTabs();
    if (stages.length > 0) renderKnowledgePoints(stages[0]);
}

function renderStageTabsDemo() {
    const stages = ['第一阶段', '第二阶段', '第三阶段', '第四阶段', '第五阶段', '第六阶段'];
    document.getElementById('stageTabs').innerHTML = stages.map((stage, index) => `<button class="stage-tab ${index === 0 ? 'active' : ''}" data-stage="${index + 1}">${stage}</button>`).join('');
}

function renderKnowledgePointsDemo(stage) {
    const stageInfo = {
        '1': { title: '第一阶段：计算机系统基本知识', desc: '第1-10天 | 建议25个知识点', progress: 20, completed: 5, total: 25 },
        '2': { title: '第二阶段：信息系统基础', desc: '第11-15天 | 建议15个知识点', progress: 0, completed: 0, total: 15 },
        '3': { title: '第三阶段：信息安全技术', desc: '第16-18天 | 建议10个知识点', progress: 0, completed: 0, total: 10 },
        '4': { title: '第四阶段：软件工程', desc: '第19-25天 | 建议15个知识点', progress: 0, completed: 0, total: 15 },
        '5': { title: '第五阶段：数据库设计', desc: '第26-30天 | 建议10个知识点', progress: 0, completed: 0, total: 10 },
        '6': { title: '第六阶段：系统架构设计', desc: '第31-38天 | 建议15个知识点', progress: 0, completed: 0, total: 15 }
    };
    const info = stageInfo[stage] || stageInfo['1'];
    const stageInfoEl = document.getElementById('stageInfo');
    stageInfoEl.querySelector('h2').textContent = info.title;
    stageInfoEl.querySelector('p').textContent = info.desc;
    stageInfoEl.querySelector('.progress-fill').style.width = `${info.progress}%`;
    stageInfoEl.querySelector('.progress-text').textContent = `已完成 ${info.completed}/${info.total} 知识点 (${info.progress}%)`;

    const points = [
        { code: '1.1', name: '计算机系统概述', status: 'completed' },
        { code: '1.2.1', name: '冯·诺依曼计算机结构', status: 'completed' },
        { code: '1.2.4', name: '存储器', status: 'current' },
        { code: '1.2.2', name: '处理器（CPU、GPU）', status: 'locked' },
        { code: '1.2.3', name: '指令集', status: 'locked' }
    ];
    document.getElementById('knowledgePoints').innerHTML = points.map(p => `<div class="point-card ${p.status}"><div class="point-status">${p.status === 'completed' ? '<i class="fas fa-check-circle"></i>' : p.status === 'current' ? '<i class="fas fa-play-circle"></i>' : '<i class="fas fa-lock"></i>'}</div><div class="point-info"><h4>${p.code} ${p.name}</h4><p>${p.status === 'completed' ? '已掌握' : p.status === 'current' ? '进行中' : '需先完成前置知识'}</p></div><div class="point-action">${p.status === 'completed' ? '<button class="btn btn-sm btn-outline" onclick="startLearn(\'' + p.code + '\')">复习</button>' : p.status === 'current' ? '<button class="btn btn-sm btn-primary" onclick="startLearn(\'' + p.code + '\')">继续</button>' : '<button class="btn btn-sm btn-disabled" disabled>未解锁</button>'}</div></div>`).join('');
}

function renderKnowledgePoints(stage) {
    const points = state.stageData.filter(k => k.stage === stage);
    const stageInfoEl = document.getElementById('stageInfo');
    const completed = points.filter(p => p.status === 'completed').length;
    const progress = points.length > 0 ? Math.round(completed / points.length * 100) : 0;
    stageInfoEl.querySelector('h2').textContent = `${stage}：${points[0]?.chapter || ''}`;
    stageInfoEl.querySelector('p').textContent = `共${points.length}个知识点`;
    stageInfoEl.querySelector('.progress-fill').style.width = `${progress}%`;
    stageInfoEl.querySelector('.progress-text').textContent = `已完成 ${completed}/${points.length} 知识点 (${progress}%)`;

    const statusIcons = {
        'completed': '<i class="fas fa-check-circle" style="color:#10B981;"></i>',
        'unlocked': '<i class="fas fa-play-circle" style="color:#2563EB;"></i>',
        'locked': '<i class="fas fa-lock" style="color:#94a3b8;"></i>'
    };

    document.getElementById('knowledgePoints').innerHTML = points.map(p => `
        <div class="point-card ${p.status}">
            <div class="point-status">${statusIcons[p.status] || statusIcons['locked']}</div>
            <div class="point-info">
                <h4>${p.code} ${p.name}</h4>
                <p>${p.status === 'completed' ? '✅ 已掌握' : p.status === 'unlocked' ? '📚 待学习' : '🔒 需先完成前置知识'}</p>
            </div>
            <div class="point-action">
                ${p.status === 'completed' ? `<button class="btn btn-sm btn-outline" onclick="selectKnowledgePoint(${p.id}, '${p.name}')"><i class="fas fa-redo"></i> 复习</button>` : ''}
                ${p.status === 'unlocked' ? `<button class="btn btn-sm btn-primary" onclick="selectKnowledgePoint(${p.id}, '${p.name}')"><i class="fas fa-play"></i> 学习</button>` : ''}
                ${p.status === 'locked' ? `<button class="btn btn-sm btn-disabled" disabled><i class="fas fa-lock"></i> 未解锁</button>` : ''}
            </div>
        </div>
    `).join('');
}

async function loadPracticeData() {
    const current = await api.getCurrentKnowledge();
    if (!current) { showPracticeEmpty('请先从学习地图选择知识点'); return; }

    // Check mastery - must reach 90% before practice
    const mastery = await api.getMastery(current.id);
    if (!mastery?.threshold_met) {
        const msg = mastery?.message || '需要先达到90%掌握度才能开始练习';
        showPracticeEmpty(msg);
        return;
    }

    const result = await api.getQuestions(current.id);
    if (!result || !result.data || result.data.length === 0) { showPracticeEmpty(); return; }
    state.questions = result.data;
    state.currentQuestionIndex = 0;
    renderQuestion(0);
}

function showPracticeEmpty(message) {
    const defaultMsg = message || '学习知识点后可获得练习题';
    document.getElementById('practiceTitle').textContent = '题目练习';
    document.getElementById('questionType').textContent = '暂无题目';
    document.getElementById('questionContent').textContent = defaultMsg;
    document.getElementById('optionsList').innerHTML = `<p style="text-align: center; color: var(--text-secondary);">${defaultMsg}</p>`;
    document.getElementById('analysisCard').style.display = 'none';
}

function renderQuestion(index) {
    const question = state.questions[index];
    if (!question) return;
    document.getElementById('practiceTitle').textContent = `题目练习 - ${state.currentKnowledge?.name || ''}`;
    document.getElementById('practiceProgress').textContent = `第${index + 1}题/共${state.questions.length}题`;
    document.getElementById('practiceFill').style.width = `${((index + 1) / state.questions.length * 100)}%`;
    document.getElementById('practicePercent').textContent = `${Math.round((index + 1) / state.questions.length * 100)}%`;
    const typeMap = { 'single': '单项选择题', 'multi': '多项选择题', 'judge': '判断题' };
    document.getElementById('questionType').textContent = typeMap[question.type] || '选择题';
    document.getElementById('questionContent').textContent = question.content;
    const optionsList = document.getElementById('optionsList');
    if (question.type === 'judge') {
        optionsList.innerHTML = ['对', '错'].map((opt, i) => `<label class="option-item" data-value="${i === 0 ? 'true' : 'false'}"><input type="radio" name="answer" value="${i === 0 ? 'true' : 'false'}"><div class="option-content"><span class="option-letter">${opt}</span><span class="option-text">${opt}</span></div><i class="fas fa-check correct-icon"></i><i class="fas fa-times wrong-icon"></i></label>`).join('');
    } else {
        optionsList.innerHTML = Object.entries(question.options || {}).map(([key, value]) => `<label class="option-item" data-value="${key}"><input type="radio" name="answer" value="${key}"><div class="option-content"><span class="option-letter">${key}</span><span class="option-text">${value}</span></div><i class="fas fa-check correct-icon"></i><i class="fas fa-times wrong-icon"></i></label>`).join('');
    }
    document.getElementById('analysisCard').style.display = 'none';
    document.getElementById('submitAnswer').style.display = 'inline-flex';
    document.getElementById('nextQuestion').style.display = 'none';
    document.getElementById('prevQuestion').disabled = index === 0;
    initPractice();
}

async function loadWrongData() {
    const filter = document.getElementById('wrongFilter').value;
    const result = await api.getWrongQuestions(filter);
    const wrongList = document.getElementById('wrongList');
    if (!result || !result.data || result.data.length === 0) {
        wrongList.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 40px;">暂无错题记录，继续保持！</p>';
        document.getElementById('wrongCount').textContent = '0道';
        return;
    }
    state.wrongQuestions = result.data;
    document.getElementById('wrongCount').textContent = `${result.data.length}道`;
    wrongList.innerHTML = result.data.map(w => `<div class="wrong-card"><div class="wrong-knowledge"><i class="fas fa-tag"></i><span>${w.knowledge_name || '未知知识点'}</span></div><div class="wrong-question"><h4>Q: ${w.question_content}</h4><div class="wrong-answer"><div class="answer-item wrong"><span class="label">❌ 你的回答：</span><span>${w.user_answer}</span></div><div class="answer-item correct"><span class="label">✅ 正确答案：</span><span>${w.correct_answer}</span></div></div></div><div class="wrong-footer"><span class="date"><i class="fas fa-calendar"></i> ${w.wrong_date || ''}</span><button class="btn btn-sm btn-outline" onclick="reviewWrong(${w.id})"><i class="fas fa-redo"></i> 重新练习</button></div></div>`).join('');
}

async function loadReportData() {
    const result = await api.getReport();
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('reportDate').textContent = today;
    if (!result || !result.data) { renderDemoReport(); return; }
    const report = result.data;
    document.getElementById('reportStatus').textContent = report.completed ? '✅ 今日任务已完成！' : '⏳ 今日任务进行中';
    document.getElementById('reportSections').innerHTML = `<div class="report-card"><div class="report-icon"><i class="fas fa-book"></i></div><h4>📚 学习内容</h4><ul><li>${report.knowledge_name || '存储系统'}</li><li>掌握${report.concepts_count || 3}个核心概念</li><li>完成${report.questions_count || 5}道练习题</li></ul></div><div class="report-card"><div class="report-icon"><i class="fas fa-star"></i></div><h4>⭐ 获得积分</h4><ul><li>答题得分：+${report.answer_points || 40}分</li><li>连击奖励：+${report.streak_bonus || 6}分</li><li>今日总计：<strong>+${report.total_points || 46}分</strong></li></ul></div><div class="report-card"><div class="report-icon"><i class="fas fa-fire"></i></div><h4>🔥 学习连续性</h4><ul><li>连续学习：${report.streak || 2}天</li><li>最长连续：${report.max_streak || 5}天</li></ul></div><div class="report-card"><div class="report-icon"><i class="fas fa-calendar-check"></i></div><h4>📅 明日预告</h4><ul><li>${report.next_knowledge || '1.3 CPU结构 - 寄存器/控制器'}</li></ul></div>`;
}

function renderDemoReport() {
    document.getElementById('reportStatus').textContent = '✅ 今日任务已完成！';
    document.getElementById('reportSections').innerHTML = `<div class="report-card"><div class="report-icon"><i class="fas fa-book"></i></div><h4>📚 学习内容</h4><ul><li>存储系统 - 内存管理</li><li>掌握3个核心概念</li><li>完成5道练习题</li></ul></div><div class="report-card"><div class="report-icon"><i class="fas fa-star"></i></div><h4>⭐ 获得积分</h4><ul><li>答题得分：+40分</li><li>连击奖励：+6分</li><li>今日总计：<strong>+46分</strong></li></ul></div><div class="report-card"><div class="report-icon"><i class="fas fa-fire"></i></div><h4>🔥 学习连续性</h4><ul><li>连续学习：2天</li><li>最长连续：5天</li></ul></div><div class="report-card"><div class="report-icon"><i class="fas fa-calendar-check"></i></div><h4>📅 明日预告</h4><ul><li>1.3 CPU结构 - 寄存器/控制器</li></ul></div>`;
}

// ========================================
// 侧边栏控制
// ========================================
function initSidebar() {
    const menuBtn = document.getElementById('menuBtn');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    if (menuBtn) menuBtn.addEventListener('click', () => sidebar.classList.toggle('open'));
    if (sidebarToggle) sidebarToggle.addEventListener('click', () => sidebar.classList.remove('open'));
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.getAttribute('data-page');
            if (page) navigateTo(page);
        });
    });
}

// ========================================
// 题目练习功能
// ========================================
function initPractice() {
    const options = document.querySelectorAll('.option-item');
    const submitBtn = document.getElementById('submitAnswer');
    const nextBtn = document.getElementById('nextQuestion');
    const prevBtn = document.getElementById('prevQuestion');
    const analysisCard = document.getElementById('analysisCard');
    let selectedAnswer = null;

    options.forEach(option => {
        option.addEventListener('click', () => {
            if (analysisCard.style.display === 'block') return;
            options.forEach(opt => opt.classList.remove('selected'));
            option.classList.add('selected');
            selectedAnswer = option.getAttribute('data-value');
        });
    });

    if (submitBtn) {
        submitBtn.addEventListener('click', async () => {
            if (!selectedAnswer) { showToast('请先选择一个答案', 'warning'); return; }
            const question = state.questions[state.currentQuestionIndex];
            await api.submitAnswer(question.id, selectedAnswer);
            const correctAnswer = String(question.answer).toLowerCase();
            selectedAnswer = String(selectedAnswer).toLowerCase();
            options.forEach(option => {
                const value = option.getAttribute('data-value').toLowerCase();
                if (value === correctAnswer) option.classList.add('correct');
                else if (value === selectedAnswer && value !== correctAnswer) option.classList.add('wrong');
            });
            analysisCard.style.display = 'block';
            const isCorrect = selectedAnswer === correctAnswer;
            if (isCorrect) {
                document.getElementById('analysisHeader').innerHTML = '<i class="fas fa-check-circle"></i><span>回答正确！ +10分</span>';
                document.getElementById('analysisText').textContent = question.analysis || '回答正确！';
                showToast('回答正确！ +10分', 'success');
                // 标记练习完成
                if (state.currentKnowledge) {
                    await api.completeLearningStep(state.currentKnowledge.id, 'practice');
                }
            } else {
                document.getElementById('analysisHeader').innerHTML = '<i class="fas fa-times-circle"></i><span>回答错误，已收录到错题本</span>';
                document.getElementById('analysisText').textContent = question.analysis || '回答错误，请复习相关知识点。';
                showToast('回答错误，已收录到错题本', 'error');
            }
            submitBtn.style.display = 'none';
            nextBtn.style.display = 'inline-flex';
            if (state.currentQuestionIndex >= state.questions.length - 1) { nextBtn.textContent = '查看报告'; nextBtn.onclick = () => navigateTo('report'); }
        });
    }
    if (nextBtn) { nextBtn.addEventListener('click', () => { if (state.currentQuestionIndex < state.questions.length - 1) { state.currentQuestionIndex++; renderQuestion(state.currentQuestionIndex); } }); }
    if (prevBtn) { prevBtn.addEventListener('click', () => { if (state.currentQuestionIndex > 0) { state.currentQuestionIndex--; renderQuestion(state.currentQuestionIndex); } }); }
}

// ========================================
// 学习地图 - 阶段切换
// ========================================
function initStageTabs() {
    document.querySelectorAll('.stage-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.stage-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const stage = tab.getAttribute('data-stage');
            renderKnowledgePoints(stage);
        });
    });
}

// ========================================
// 聊天界面功能
// ========================================
function initChat() {
    const sendBtn = document.getElementById('sendBtn');
    const userInput = document.getElementById('userInput');
    if (sendBtn && userInput) {
        sendBtn.addEventListener('click', () => sendMessage());
        userInput.addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } });
    }
}

async function sendMessage() {
    const userInput = document.getElementById('userInput');
    const text = userInput.value.trim();
    if (!text) return;
    addUserMessage(text);
    userInput.value = '';
    const result = await api.sendMessage(text);
    if (result && result.data) {
        addAIMessage(result.data.response);

        // 更新学习阶段
        if (result.data.learning_phase) {
            state.learningPhase = result.data.learning_phase;
            updatePhaseDisplay();

            // 更新输入框 placeholder
            if (result.data.learning_phase === 'interactive') {
                userInput.placeholder = '输入你的问题，或输入「学习好了」...';
            } else if (result.data.learning_phase === 'socratic') {
                userInput.placeholder = '输入你的回答...';
            } else if (result.data.learning_phase === 'completed') {
                userInput.placeholder = '学习已完成，前往地图选择下一个知识点';
            }
        }

        // 更新掌握度显示
        const masteryPercent = result.data.mastery_percentage || 0;
        const knowledgeName = result.data.knowledge_name || state.currentKnowledge?.name || '';

        if (result.data.learning_phase === 'completed') {
            document.getElementById('socraticText').textContent = `🎉 已完成「${knowledgeName}」！前往学习地图选择下一个知识点`;
            showToast('🎉 恭喜！已掌握该知识点！', 'success');
        } else if (masteryPercent > 0) {
            document.getElementById('socraticText').textContent = `🎯 ${knowledgeName} | 掌握度：${masteryPercent}%`;
        } else if (result.data.socratic_hint) {
            document.getElementById('socraticText').textContent = result.data.socratic_hint;
        }
    } else {
        setTimeout(() => {
            addAIMessage('AI服务暂时不可用，请稍后重试。');
        }, 500);
    }
}

function addUserMessage(text) {
    const chatMessages = document.getElementById('chatMessages');
    const div = document.createElement('div');
    div.className = 'message user-message';
    div.innerHTML = `<div class="message-content"><div class="message-text">${formatText(text)}</div><div class="message-time">${getCurrentTime()}</div></div><div class="message-avatar"><i class="fas fa-user"></i></div>`;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addAIMessage(text) {
    const chatMessages = document.getElementById('chatMessages');
    const div = document.createElement('div');
    div.className = 'message ai-message';
    div.innerHTML = `<div class="message-avatar"><i class="fas fa-robot"></i></div><div class="message-content"><div class="message-sender">AI伴学助手</div><div class="message-text">${formatText(text)}</div><div class="message-time">${getCurrentTime()}</div></div>`;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function formatText(text) {
    return text
        .replace(/\*\*(.*?)\*\*/g, '<span class="knowledge-tag" onclick="showKnowledgeCard(\'$1\')">$1</span>')
        .replace(/\n/g, '<br>');
}
function getCurrentTime() { return new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }); }

async function startLearn(code) {
    const result = await api.selectLearningUnit(code);
    if (result && result.success) {
        showToast('已选择该知识点，开始学习', 'success');
        navigateTo('learn');
    } else {
        showToast(result.message || '选择失败', 'error');
    }
}

async function reviewWrong(id) { navigateTo('practice'); }

async function selectKnowledgePoint(knowledgeId, knowledgeName) {
    // 先跳转到学习模块，避免重复加载学习内容
    const result = await api.selectLearningUnit(knowledgeId);
    if (result && result.success) {
        navigateTo('learn');
    } else {
        showToast(result.message || '选择失败，请检查是否已解锁', 'error');
    }
}

function renderPhaseIndicator(currentPhase) {
    const phases = [
        { key: 'feynman', label: '1.费曼学习', icon: 'fa-book-open' },
        { key: 'interactive', label: '2.互动学习', icon: 'fa-comments' },
        { key: 'socratic', label: '3.苏格拉底检验', icon: 'fa-brain' }
    ];
    const phaseOrder = ['feynman', 'interactive', 'socratic', 'completed'];
    const currentIdx = phaseOrder.indexOf(currentPhase);

    return `<div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;flex-wrap:wrap;">
        ${phases.map((p, i) => {
            const pIdx = phaseOrder.indexOf(p.key);
            const isCompleted = currentIdx > pIdx || currentPhase === 'completed';
            const isCurrent = currentPhase === p.key;
            let bg, color;
            if (isCompleted) { bg = '#10B981'; color = 'white'; }
            else if (isCurrent) { bg = '#2563EB'; color = 'white'; }
            else { bg = '#e2e8f0'; color = '#64748b'; }
            const checkmark = isCompleted ? '✓ ' : '';
            return `<span style="background:${bg};color:${color};padding:4px 12px;border-radius:16px;font-size:12px;">${checkmark}${p.label}</span>`;
        }).join('<span style="color:#94a3b8;">→</span>')}
    </div>`;
}

function updatePhaseDisplay() {
    const phase = state.learningPhase;
    const socraticText = document.getElementById('socraticText');
    const knowledgeName = state.currentKnowledge?.name || '当前知识点';

    switch (phase) {
        case 'feynman':
            socraticText.textContent = `📖 费曼学习 → ${knowledgeName}`;
            break;
        case 'interactive':
            socraticText.textContent = `💬 互动学习 → ${knowledgeName} | 可随时输入「学习好了」进入检验`;
            break;
        case 'socratic':
            socraticText.textContent = `🎯 苏格拉底检验 → ${knowledgeName} | 达到90%掌握度解锁下一单元`;
            break;
        case 'completed':
            socraticText.textContent = `🎉 已完成 ${knowledgeName}！前往学习地图选择下一个知识点`;
            break;
        default:
            socraticText.textContent = `📚 ${knowledgeName}`;
    }
}

function transitionToSocratic() {
    const userInput = document.getElementById('userInput');
    userInput.value = '学习好了';
    sendMessage();
}

async function loadLearnDataWithFeynman(knowledgeId) {
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.innerHTML = `<div class="message ai-message"><div class="message-avatar"><i class="fas fa-robot"></i></div><div class="message-content"><div class="message-sender">AI伴学助手</div><div class="message-text"><p>正在加载学习内容...</p></div><div class="message-time">${getCurrentTime()}</div></div></div>`;

    const mastery = await api.getMastery(knowledgeId);
    const phase = mastery?.learning_phase || 'feynman';
    state.learningPhase = phase;

    const knowledgeName = state.currentKnowledge?.name || '当前知识点';

    // 根据阶段渲染不同UI
    chatMessages.innerHTML = '';

    if (phase === 'completed') {
        addAIMessage(`<div style="margin-bottom:16px;">${renderPhaseIndicator('completed')}</div><div style="text-align:center;padding:32px 0;"><i class="fas fa-check-circle" style="font-size:48px;color:#10B981;margin-bottom:16px;"></i><h3 style="color:#10B981;">已完成「${knowledgeName}」的学习！</h3><p style="color:#64748b;margin-top:8px;">前往学习地图选择下一个知识点继续学习。</p></div>`);
        updatePhaseDisplay();
        return;
    }

    if (phase === 'socratic') {
        addAIMessage(`<div style="margin-bottom:16px;">${renderPhaseIndicator('socratic')}</div><div style="text-align:center;padding:24px 0;"><i class="fas fa-brain" style="font-size:40px;color:#2563EB;margin-bottom:12px;"></i><h3>苏格拉底检验进行中</h3><p style="color:#64748b;margin-top:8px;">当前掌握度：${mastery?.mastery_percentage || 0}%（需要达到90%）</p><p style="color:#64748b;">请回答AI的问题来提升掌握度。</p></div>`);
        const userInput = document.getElementById('userInput');
        userInput.placeholder = '输入你的回答...';
        updatePhaseDisplay();
        return;
    }

    // feynman 或 interactive 阶段 — 加载费曼内容
    const feynmanResult = await api.getFeynmanContent(knowledgeId);

    if (feynmanResult && feynmanResult.success && feynmanResult.data) {
        const feynmanContent = feynmanResult.data.content;
        state.currentKnowledge = { id: knowledgeId, name: feynmanResult.data.knowledge_name };
        addAIMessage(`<div style="margin-bottom:16px;">${renderPhaseIndicator(phase)}</div><div class="feynman-card"><div class="feynman-header"><i class="fas fa-lightbulb"></i><strong>费曼学习法讲解：${feynmanResult.data.knowledge_name}</strong></div><div class="feynman-content">${feynmanContent}</div></div><p style="margin-top:16px;">现在你可以：</p><ul style="margin-top:8px;padding-left:20px;"><li>💬 输入你对这个知识点的疑问，我会为你解答</li><li>✅ 输入「<strong>学习好了</strong>」进入苏格拉底检验环节</li></ul><div style="margin-top:12px;"><button onclick="transitionToSocratic()" style="background:#2563EB;color:white;padding:8px 20px;border:none;border-radius:8px;cursor:pointer;font-size:14px;"><i class="fas fa-arrow-right"></i> 直接进入检验</button></div>`);
    } else {
        addAIMessage(`<div style="margin-bottom:16px;">${renderPhaseIndicator(phase)}</div><p>知识点讲解内容正在准备中。现在你可以：</p><ul style="margin-top:8px;padding-left:20px;"><li>💬 输入你对这个知识点的疑问</li><li>✅ 输入「<strong>学习好了</strong>」进入检验环节</li></ul><div style="margin-top:12px;"><button onclick="transitionToSocratic()" style="background:#2563EB;color:white;padding:8px 20px;border:none;border-radius:8px;cursor:pointer;font-size:14px;"><i class="fas fa-arrow-right"></i> 直接进入检验</button></div>`);
    }

    const userInput = document.getElementById('userInput');
    userInput.placeholder = phase === 'interactive' ? '输入你的问题，或输入「学习好了」...' : '输入你的回答...';
    updatePhaseDisplay();
}

// ========================================
// Toast提示
// ========================================
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    const icons = { 'success': 'fa-check-circle', 'error': 'fa-exclamation-circle', 'warning': 'fa-exclamation-triangle', 'info': 'fa-info-circle' };
    const colors = { 'success': 'var(--success)', 'error': 'var(--error)', 'warning': 'var(--warning)', 'info': 'var(--primary)' };
    toast.innerHTML = `<i class="fas ${icons[type]}"></i><span>${message}</span>`;
    toast.style.cssText = `position: fixed; top: 20px; right: 20px; background: white; padding: 16px 24px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); display: flex; align-items: center; gap: 12px; z-index: 1000; border-left: 4px solid ${colors[type]}; animation: slideInRight 0.3s ease;`;
    document.body.appendChild(toast);
    setTimeout(() => { toast.style.animation = 'slideOutRight 0.3s ease'; setTimeout(() => toast.remove(), 300); }, 3000);
    if (!document.getElementById('toast-styles')) {
        const style = document.createElement('style');
        style.id = 'toast-styles';
        style.textContent = `@keyframes slideInRight { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } } @keyframes slideOutRight { from { transform: translateX(0); opacity: 1; } to { transform: translateX(100%); opacity: 0; } }`;
        document.head.appendChild(style);
    }
}

// ========================================
// 题库上传功能
// ========================================
async function loadUploadData() {
    const template = await api.getUploadTemplate();
    if (template) {
        renderFormatExample('json', template);
    }

    // 加载知识点下拉框
    const knowledgeResult = await api.getKnowledgePoints();
    const knowledgeSelect = document.getElementById('knowledgeSelect');
    if (knowledgeResult && knowledgeResult.data) {
        knowledgeSelect.innerHTML = '<option value="">-- 不关联特定知识点 --</option>';
        knowledgeResult.data.forEach(k => {
            knowledgeSelect.innerHTML += `<option value="${k.id}">${k.code} ${k.name}</option>`;
        });
    }

    // 绑定格式切换事件
    document.querySelectorAll('.format-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.format-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const format = tab.getAttribute('data-format');
            if (template) renderFormatExample(format, template);
        });
    });

    // 模板按钮事件
    const showTemplateBtn = document.getElementById('showTemplateBtn');
    if (showTemplateBtn) {
        showTemplateBtn.addEventListener('click', () => {
            document.querySelector('.format-info').scrollIntoView({ behavior: 'smooth' });
        });
    }
}

function renderFormatExample(format, template) {
    const formatContent = document.getElementById('formatExample');
    let example = '';

    if (format === 'json') {
        example = JSON.stringify(template.example, null, 2);
    } else if (format === 'txt') {
        example = `题目内容
A: 选项A
B: 选项B
C: 选项C
D: 选项D
答案: B
---
判断题示例
答案: 对`;
    } else if (format === 'md') {
        example = `### 下列关于Cache的说法，错误的是？
- A. 位于CPU和内存之间
- B. 容量比内存大
- C. 访问速度比内存快
- D. 由高速SRAM组成
答案: B

### Cache的命中率越高越好。
答案: 错`;
    } else if (format === 'pdf') {
        example = `PDF格式说明：

1. PDF文件会被自动提取文本内容
2. 系统会尝试智能解析题目结构
3. 支持扫描版PDF（需要文字识别支持）

推荐做法：
- 如果PDF是文本型（非扫描），系统会自动解析
- 如果解析效果不佳，建议转换为JSON格式导入
- PDF解析支持：选择题、判断题

上传后将自动处理，无需额外配置。`;
    }

    formatContent.textContent = example;
}

function initUpload() {
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');

    if (!uploadZone || !fileInput) return;

    // 拖拽事件
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });

    // 点击上传
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });

    // 拖拽点击区域也触发文件选择
    uploadZone.addEventListener('click', () => {
        fileInput.click();
    });
}

async function handleFileUpload(file) {
    if (!file) return;

    const allowedTypes = ['.txt', '.json', '.md', '.pdf'];
    const ext = '.' + file.name.split('.').pop().toLowerCase();

    if (!allowedTypes.includes(ext)) {
        showToast('不支持的文件格式，请上传 .txt、.json、.md 或 .pdf 文件', 'error');
        return;
    }

    // 显示进度
    const uploadProgress = document.getElementById('uploadProgress');
    const progressStage = document.getElementById('progressStage');
    const progressFill = document.getElementById('progressFill');
    const progressPercent = document.getElementById('progressPercent');
    const progressCount = document.getElementById('progressCount');
    const uploadResult = document.getElementById('uploadResult');
    const fileInput = document.getElementById('fileInput');

    uploadProgress.style.display = 'block';
    uploadResult.style.display = 'none';
    progressStage.textContent = '正在上传文件...';
    progressFill.style.width = '10%';
    progressPercent.textContent = '10%';
    progressCount.textContent = '0 / 0 题';

    const formData = new FormData();
    formData.append('file', file);

    const knowledgeSelect = document.getElementById('knowledgeSelect');
    if (knowledgeSelect && knowledgeSelect.value) {
        formData.append('knowledge_point', knowledgeSelect.value);
    }

    showToast('正在上传...', 'info');

    const useAiParse = document.getElementById('useAiParse')?.checked ?? true;
    const aiProvider = document.getElementById('aiProvider')?.value || 'deepseek';
    const result = await api.uploadQuestions(formData, useAiParse, aiProvider);

    const resultMessage = document.getElementById('resultMessage');
    const totalFound = document.getElementById('totalFound');
    const importedCount = document.getElementById('importedCount');

    // Clear file input so same file can be selected again
    fileInput.value = '';

    if (result && result.success) {
        uploadProgress.style.display = 'none';
        uploadResult.style.display = 'block';
        resultMessage.textContent = '上传成功！';
        totalFound.textContent = result.total_found || 0;
        importedCount.textContent = result.imported || 0;
        showToast(result.message || '导入成功', 'success');
    } else {
        uploadProgress.style.display = 'none';
        uploadResult.style.display = 'block';
        resultMessage.textContent = result.message || '上传失败';
        totalFound.textContent = result.total_found || 0;
        importedCount.textContent = result.imported || 0;
        showToast(result.message || '导入失败', 'error');
    }
}

// ========================================
// 题库管理功能
// ========================================
async function loadQuestionBankData() {
    const [banksResult, statsResult] = await Promise.all([
        api.getQuestionBanks(),
        api.getQuestionBankStats()
    ]);

    // 更新统计卡片
    if (statsResult) {
        document.getElementById('totalQuestions').textContent = statsResult.total || 0;
        document.getElementById('approvedQuestions').textContent = statsResult.approved || 0;
        document.getElementById('pendingQuestions').textContent = statsResult.pending || 0;
    }

    // 渲染题库列表
    renderBankList(banksResult?.data || []);

    // 绑定筛选事件
    document.getElementById('questionTypeFilter')?.addEventListener('change', applyQuestionFilters);
    document.getElementById('questionStatusFilter')?.addEventListener('change', applyQuestionFilters);
}

function renderBankList(banks) {
    const bankList = document.getElementById('bankList');
    if (!banks || banks.length === 0) {
        bankList.innerHTML = '<p class="empty-hint">暂无题库，上传题目后自动生成</p>';
        return;
    }

    bankList.innerHTML = banks.map(bank => `
        <div class="bank-item" data-source="${bank.source}">
            <div class="bank-info">
                <div class="bank-source">${bank.source}</div>
                <div class="bank-meta">
                    <span class="badge badge-success">已启用 ${bank.approved}</span>
                    <span class="badge badge-warning">待审核 ${bank.pending}</span>
                </div>
            </div>
            <div class="bank-actions">
                <button class="btn btn-sm btn-outline" onclick="loadQuestions('${bank.source}')">
                    <i class="fas fa-eye"></i> 查看题目
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteBank('${bank.source}')">
                    <i class="fas fa-trash"></i> 删除
                </button>
            </div>
        </div>
    `).join('');
}

let currentQuestionSource = null;
let currentQuestionPage = 1;
let currentQuestionType = '';
let currentQuestionStatus = '';

async function loadQuestions(source, page = 1) {
    currentQuestionSource = source;
    currentQuestionPage = page;

    const params = { source, page: page.toString(), page_size: '20' };
    if (currentQuestionType) params.type = currentQuestionType;
    if (currentQuestionStatus) params.status = currentQuestionStatus;

    const result = await api.getQuestionBankQuestions(source, page, 20);
    renderQuestionsList(result?.data || [], result);
}

function renderQuestionsList(questions, pagination) {
    const list = document.getElementById('questionsList');
    if (!questions || questions.length === 0) {
        list.innerHTML = '<p class="empty-hint">该题库中暂无题目</p>';
        document.getElementById('questionPagination').innerHTML = '';
        return;
    }

    list.innerHTML = `
        <table class="questions-table">
            <thead>
                <tr>
                    <th>类型</th>
                    <th>题目内容</th>
                    <th>知识点</th>
                    <th>状态</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody>
                ${questions.map(q => `
                    <tr>
                        <td><span class="badge badge-${q.type === 'single' ? 'primary' : q.type === 'multi' ? 'info' : 'warning'}">${q.type === 'single' ? '单选' : q.type === 'multi' ? '多选' : '判断'}</span></td>
                        <td class="question-content-cell">${q.content.substring(0, 50)}${q.content.length > 50 ? '...' : ''}</td>
                        <td>${q.knowledge_point || '-'}</td>
                        <td><span class="badge badge-${q.status === 'approved' ? 'success' : 'warning'}">${q.status === 'approved' ? '已启用' : '待审核'}</span></td>
                        <td>
                            <button class="btn btn-sm btn-outline" onclick="toggleQuestionDetail(${q.id})" title="查看详情">
                                <i class="fas fa-chevron-down"></i>
                            </button>
                            ${q.status !== 'approved' ? `<button class="btn btn-sm btn-primary" onclick="approveQuestion(${q.id})"><i class="fas fa-check"></i></button>` : ''}
                            <button class="btn btn-sm btn-danger" onclick="deleteQuestion(${q.id})"><i class="fas fa-trash"></i></button>
                        </td>
                    </tr>
                    <tr class="question-detail" id="detail-${q.id}" style="display: none;">
                        <td colspan="5">
                            <div class="question-detail-content">
                                <p><strong>题目：</strong>${q.content}</p>
                                ${q.options ? `<p><strong>选项：</strong>${JSON.stringify(q.options)}</p>` : ''}
                                <p><strong>答案：</strong>${q.answer}</p>
                                ${q.analysis ? `<p><strong>解析：</strong>${q.analysis}</p>` : ''}
                            </div>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;

    // 渲染分页
    renderPagination(pagination);
}

function renderPagination(pagination) {
    const paginationEl = document.getElementById('questionPagination');
    if (!pagination || pagination.total_pages <= 1) {
        paginationEl.innerHTML = '';
        return;
    }

    let html = '';
    if (pagination.page > 1) {
        html += `<button class="page-btn" onclick="loadQuestions('${currentQuestionSource}', ${pagination.page - 1})"><i class="fas fa-chevron-left"></i></button>`;
    }
    html += `<span class="page-info">第 ${pagination.page} / ${pagination.total_pages} 页</span>`;
    if (pagination.page < pagination.total_pages) {
        html += `<button class="page-btn" onclick="loadQuestions('${currentQuestionSource}', ${pagination.page + 1})"><i class="fas fa-chevron-right"></i></button>`;
    }
    paginationEl.innerHTML = html;
}

function applyQuestionFilters() {
    currentQuestionType = document.getElementById('questionTypeFilter')?.value || '';
    currentQuestionStatus = document.getElementById('questionStatusFilter')?.value || '';
    if (currentQuestionSource) {
        loadQuestions(currentQuestionSource, 1);
    }
}

function toggleQuestionDetail(id) {
    const detail = document.getElementById(`detail-${id}`);
    if (detail) {
        detail.style.display = detail.style.display === 'none' ? 'table-row' : 'none';
    }
}

async function deleteQuestion(id) {
    if (!confirm('确定要删除这道题目吗？')) return;
    const result = await api.deleteQuestion(id);
    if (result && result.message) {
        showToast('删除成功', 'success');
        if (currentQuestionSource) loadQuestions(currentQuestionSource, currentQuestionPage);
    } else {
        showToast('删除失败', 'error');
    }
}

async function deleteBank(source) {
    if (!confirm(`确定要删除题库「${source}」吗？该操作将删除此题库下的所有题目，且不可恢复！`)) return;
    const result = await api.deleteBank(source);
    if (result && result.message) {
        showToast(result.message, 'success');
        currentQuestionSource = null;
        loadQuestionBankData();
    } else {
        showToast(result?.detail || '删除失败', 'error');
    }
}

async function approveQuestion(id) {
    const result = await api.approveQuestion(id);
    if (result && result.message) {
        showToast('已批准', 'success');
        if (currentQuestionSource) loadQuestions(currentQuestionSource, currentQuestionPage);
    } else {
        showToast('操作失败', 'error');
    }
}

async function resetLearningMap() {
    if (!confirm('确定要重置所有学习进度吗？此操作不可恢复。')) return;
    const result = await api.resetLearning();
    if (result && result.success) {
        showToast('学习进度已重置', 'success');
        navigateTo('map');
    } else {
        showToast('重置失败', 'error');
    }
}

function refreshQuestionBank() {
    loadQuestionBankData();
}

// ========================================
// 知识点管理
// ========================================

let currentManageTab = 'questions';

function initManageTabs() {
    const tabs = document.querySelectorAll('.manage-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentManageTab = tab.dataset.tab;
            if (currentManageTab === 'knowledge') {
                document.getElementById('knowledgeManageSection').style.display = 'block';
                loadKnowledgeManageList();
            } else {
                document.getElementById('knowledgeManageSection').style.display = 'none';
            }
        });
    });
}

async function loadKnowledgeManageList() {
    const result = await api.getKnowledgePoints();
    const list = document.getElementById('knowledgeManageList');
    if (!result || !result.data || result.data.length === 0) {
        list.innerHTML = '<p class="empty-hint">暂无知识点数据</p>';
        return;
    }

    let html = '<table class="knowledge-table"><thead><tr><th>编码</th><th>名称</th><th>章节</th><th>阶段</th><th>状态</th><th>操作</th></tr></thead><tbody>';
    result.data.forEach(kp => {
        const statusClass = kp.status === 'completed' ? 'completed' : kp.status === 'unlocked' ? 'unlocked' : 'locked';
        html += `<tr>
            <td>${kp.code}</td>
            <td>${kp.name}</td>
            <td>${kp.chapter || '-'}</td>
            <td>${kp.stage || '-'}</td>
            <td><span class="status-badge ${statusClass}">${kp.status === 'completed' ? '已完成' : kp.status === 'unlocked' ? '已解锁' : '锁定'}</span></td>
            <td class="action-cell">
                <button class="btn btn-sm btn-outline" onclick="editKnowledgePoint(${kp.id})"><i class="fas fa-edit"></i></button>
                <button class="btn btn-sm btn-danger" onclick="deleteKnowledgePoint(${kp.id})"><i class="fas fa-trash"></i></button>
            </td>
        </tr>`;
    });
    html += '</tbody></table>';
    list.innerHTML = html;
}

function showAddKnowledgeForm() {
    document.getElementById('knowledgeFormCard').style.display = 'block';
    document.getElementById('knowledgeFormTitle').innerHTML = '<i class="fas fa-plus"></i> 添加知识点';
    document.getElementById('kpEditId').value = '';
    document.getElementById('knowledgeForm').reset();
}

function hideKnowledgeForm() {
    document.getElementById('knowledgeFormCard').style.display = 'none';
}

async function editKnowledgePoint(id) {
    const result = await api.request(`/knowledge/code?kp_id=${id}`);
    if (!result || result.error) {
        const allResult = await api.getKnowledgePoints();
        const kp = allResult?.data?.find(k => k.id === id);
        if (kp) fillKnowledgeForm(kp);
    } else {
        fillKnowledgeForm(result);
    }
}

function fillKnowledgeForm(kp) {
    document.getElementById('knowledgeFormCard').style.display = 'block';
    document.getElementById('knowledgeFormTitle').innerHTML = '<i class="fas fa-edit"></i> 编辑知识点';
    document.getElementById('kpEditId').value = kp.id;
    document.getElementById('kpCode').value = kp.code || '';
    document.getElementById('kpName').value = kp.name || '';
    document.getElementById('kpChapter').value = kp.chapter || '';
    document.getElementById('kpStage').value = kp.stage || '';
    document.getElementById('kpSortOrder').value = kp.sort_order || 0;
    document.getElementById('kpStatus').value = kp.status || 'locked';
}

async function saveKnowledgePoint(event) {
    event.preventDefault();
    const editId = document.getElementById('kpEditId').value;
    const data = {
        code: document.getElementById('kpCode').value,
        name: document.getElementById('kpName').value,
        chapter: document.getElementById('kpChapter').value,
        stage: document.getElementById('kpStage').value,
        sort_order: parseInt(document.getElementById('kpSortOrder').value) || 0,
        status: document.getElementById('kpStatus').value
    };

    let result;
    if (editId) {
        result = await api.request(`/knowledge/${editId}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    } else {
        result = await api.request('/knowledge', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    if (result && (result.message || result.id)) {
        showToast(editId ? '更新成功' : '创建成功', 'success');
        hideKnowledgeForm();
        loadKnowledgeManageList();
    } else {
        showToast(result?.detail || '操作失败', 'error');
    }
}

async function deleteKnowledgePoint(id) {
    if (!confirm('确定要删除这个知识点吗？')) return;
    const result = await api.request(`/knowledge/${id}`, { method: 'DELETE' });
    if (result && result.message) {
        showToast('删除成功', 'success');
        loadKnowledgeManageList();
    } else {
        showToast(result?.detail || '删除失败', 'error');
    }
}

// ========================================
// AI问答模块
// ========================================
async function sendQAMessage() {
    const qaUserInput = document.getElementById('qaUserInput');
    const text = qaUserInput.value.trim();
    if (!text) return;

    addQAUserMessage(text);
    qaUserInput.value = '';

    // 显示加载提示
    addQAIMessage('正在思考中...');

    const result = await api.request('/ai-qa/chat', {
        method: 'POST',
        body: JSON.stringify({
            question: text,
            current_knowledge_id: state.currentKnowledge?.id
        })
    });

    // 移除加载提示
    const qaChatMessages = document.getElementById('qaChatMessages');
    if (qaChatMessages.lastChild) {
        qaChatMessages.removeChild(qaChatMessages.lastChild);
    }

    if (result && result.data) {
        addQAIMessage(result.data.response);
    } else {
        setTimeout(() => {
            addQAIMessage('AI服务暂时不可用，请稍后重试。');
        }, 500);
    }
}

function addQAUserMessage(text) {
    const qaChatMessages = document.getElementById('qaChatMessages');
    const div = document.createElement('div');
    div.className = 'message user-message';
    div.innerHTML = `<div class="message-content"><div class="message-text">${formatText(text)}</div><div class="message-time">${getCurrentTime()}</div></div><div class="message-avatar"><i class="fas fa-user"></i></div>`;
    qaChatMessages.appendChild(div);
    qaChatMessages.scrollTop = qaChatMessages.scrollHeight;
}

function addQAIMessage(text) {
    const qaChatMessages = document.getElementById('qaChatMessages');
    const div = document.createElement('div');
    div.className = 'message ai-message';
    div.innerHTML = `<div class="message-avatar"><i class="fas fa-robot"></i></div><div class="message-content"><div class="message-sender">AI伴学助手</div><div class="message-text">${formatText(text)}</div><div class="message-time">${getCurrentTime()}</div></div>`;
    qaChatMessages.appendChild(div);
    qaChatMessages.scrollTop = qaChatMessages.scrollHeight;
}

function initQAChat() {
    const qaSendBtn = document.getElementById('qaSendBtn');
    const qaUserInput = document.getElementById('qaUserInput');
    if (qaSendBtn && qaUserInput) {
        qaSendBtn.addEventListener('click', () => sendQAMessage());
        qaUserInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendQAMessage();
            }
        });
    }
}

// ========================================
// 知识卡片功能
// ========================================
async function showKnowledgeCard(term) {
    const modal = document.getElementById('knowledgeCardModal');
    const titleEl = document.getElementById('cardTitle');
    const definitionEl = document.getElementById('cardDefinition');
    const exampleEl = document.getElementById('cardExample');
    const relatedEl = document.getElementById('cardRelated');
    const questionsEl = document.getElementById('cardQuestions');
    const relatedSection = document.getElementById('relatedSection');
    const questionsSection = document.getElementById('questionsSection');

    // 显示弹窗并设置加载状态
    titleEl.textContent = term;
    definitionEl.textContent = '加载中...';
    exampleEl.textContent = '加载中...';
    relatedEl.innerHTML = '';
    questionsEl.innerHTML = '';
    modal.style.display = 'flex';

    // 调用API获取知识点详情
    const result = await api.request(`/ai-qa/knowledge-card/${encodeURIComponent(term)}`);

    if (result && result.data) {
        const data = result.data;
        titleEl.textContent = data.term || term;
        definitionEl.textContent = data.definition || '暂无定义';
        exampleEl.textContent = data.example || '暂无示例';

        // 显示关联知识
        if (data.related_knowledge && data.related_knowledge.length > 0) {
            relatedSection.style.display = 'block';
            relatedEl.innerHTML = data.related_knowledge.map(k =>
                `<div class="related-item">
                    <span class="related-name">${k.name}</span>
                    <span class="related-status ${k.status}">${k.status === 'completed' ? '已学习' : '待学习'}</span>
                </div>`
            ).join('');
        } else {
            relatedSection.style.display = 'none';
        }

        // 显示相关题目
        if (data.related_questions && data.related_questions.length > 0) {
            questionsSection.style.display = 'block';
            questionsEl.innerHTML = data.related_questions.map(q =>
                `<div class="related-question">${q}</div>`
            ).join('');
        } else {
            questionsSection.style.display = 'none';
        }
    } else {
        definitionEl.textContent = '暂无详细信息';
        exampleEl.textContent = '';
        relatedSection.style.display = 'none';
        questionsSection.style.display = 'none';
    }
}

function closeKnowledgeCard() {
    const modal = document.getElementById('knowledgeCardModal');
    modal.style.display = 'none';
}

// 点击弹窗外部关闭
document.addEventListener('click', (e) => {
    const modal = document.getElementById('knowledgeCardModal');
    if (e.target === modal) {
        closeKnowledgeCard();
    }
});

// ========================================
// 初始化
// ========================================
document.addEventListener('DOMContentLoaded', () => {
    initSidebar();
    initPractice();
    initStageTabs();
    initChat();
    initQAChat();
    initUpload();
    initManageTabs();
    // 首次访问跳转到登录页面
    navigateTo('login');
    console.log('AI伴学系统界面已加载');
});

async function loadUserInfo() {
    try {
        const user = await api.getUser();
        if (user && (user.nickname || user.username)) {
            document.getElementById('userName').textContent = user.nickname || user.username;
            // Show user management nav for admin role
            showUserManagementNav(user.role);
        } else {
            document.getElementById('userName').textContent = '学员';
        }
    } catch (e) {
        document.getElementById('userName').textContent = '学员';
    }
}

// 登录
async function doLogin() {
    const username = document.getElementById('loginUsername').value.trim();
    const password = document.getElementById('loginPassword').value;

    if (!username || !password) {
        showToast('请输入用户名和密码', 'warning');
        return;
    }

    console.log('Logging in with:', username);
    const result = await api.login(username, password);
    console.log('Login result:', result);
    if (result && result.user_id) {
        afterLogin(result);
    } else {
        showToast(result?.detail || '登录失败', 'error');
    }
}

// 注册
async function doRegister() {
    const username = document.getElementById('registerUsername').value.trim();
    const password = document.getElementById('registerPassword').value;
    const confirmPassword = document.getElementById('registerConfirmPassword').value;
    const nickname = document.getElementById('registerNickname').value.trim();

    if (!username || !password) {
        showToast('请输入用户名和密码', 'warning');
        return;
    }

    if (password !== confirmPassword) {
        showToast('两次密码输入不一致', 'warning');
        return;
    }

    const result = await api.register(username, password, nickname || username);
    if (result && result.success) {
        showToast('注册成功，请登录', 'success');
        showLogin();
    } else {
        showToast(result?.message || '注册失败', 'error');
    }
}

// 新登录页 - 密码/验证码切换
function switchLoginTab(type) {
    const tabs = document.querySelectorAll('.login-tab-item');
    const passwordInput = document.getElementById('password-input-group');
    const codeInput = document.getElementById('code-input-group');
    const passwordField = document.getElementById('loginPassword');

    if (type === 'password') {
        tabs[0].classList.add('active');
        tabs[1].classList.remove('active');
        passwordInput.style.display = 'block';
        codeInput.style.display = 'none';
        passwordField.required = true;
    } else {
        tabs[0].classList.remove('active');
        tabs[1].classList.add('active');
        passwordInput.style.display = 'none';
        codeInput.style.display = 'flex';
        passwordField.required = false;
    }
}

// 发送验证码倒计时
async function sendLoginCode(btn) {
    const username = document.getElementById('loginUsername').value.trim();
    if (!username) {
        showToast('请先输入手机号/用户名', 'warning');
        return;
    }

    // 调用后端API发送验证码
    const result = await api.sendSmsCode(username);
    if (!result || !result.success) {
        alert(result?.message || '发送失败，请稍后重试');
        return;
    }

    let time = 60;
    btn.disabled = true;
    btn.style.background = '#eee';
    btn.style.color = '#999';
    btn.style.border = '1px solid #ddd';

    const timer = setInterval(() => {
        time--;
        btn.innerText = `${time}s`;
        if (time <= 0) {
            clearInterval(timer);
            btn.innerText = '获取验证码';
            btn.disabled = false;
            btn.style.background = '#fff';
            btn.style.color = '#667eea';
            btn.style.border = '1px solid #667eea';
        }
    }, 1000);
}

// 新登录页 - 登录提交
async function doLoginNew(event) {
    event.preventDefault();

    const username = document.getElementById('loginUsername').value.trim();
    const password = document.getElementById('loginPassword').value;
    const code = document.getElementById('loginCode')?.value;

    // 判断是密码登录还是验证码登录
    const isPasswordTab = document.querySelector('.login-tab-item.active').textContent.includes('密码');

    if (!username) {
        showToast('请输入手机号/用户名', 'warning');
        return;
    }

    if (isPasswordTab && !password) {
        showToast('请输入密码', 'warning');
        return;
    }

    if (!isPasswordTab && !code) {
        showToast('请输入验证码', 'warning');
        return;
    }

    const btn = document.querySelector('.login-submit-btn');
    const originalText = btn.innerText;

    btn.innerText = '登录中...';
    btn.disabled = true;

    try {
        let result;
        if (isPasswordTab) {
            result = await api.login(username, password);
        } else {
            // 验证码登录逻辑
            result = await api.loginWithCode(username, code);
        }

        console.log('Login result:', result);
        if (result && result.user_id) {
            afterLogin(result);
        } else {
            showToast(result?.detail || '登录失败', 'error');
        }
    } catch (error) {
        showToast('登录失败: ' + error.message, 'error');
    } finally {
        btn.innerText = originalText;
        btn.disabled = false;
    }
}

// 新登录页 - 注册提交
async function doRegisterNew(event) {
    event.preventDefault();

    const username = document.getElementById('regUsername').value.trim();
    const password = document.getElementById('regPassword').value;
    const nickname = document.getElementById('regNickname')?.value.trim();
    const email = document.getElementById('regEmail')?.value.trim();

    if (!username || !password) {
        showToast('请输入用户名和密码', 'warning');
        return;
    }

    const btn = document.querySelector('.login-submit-btn');
    const originalText = btn.innerText;

    btn.innerText = '注册中...';
    btn.disabled = true;

    try {
        const result = await api.register(username, password, nickname || username, email);
        if (result && result.success) {
            showToast('注册成功，请登录', 'success');
            showLogin();
        } else {
            showToast(result?.message || '注册失败', 'error');
        }
    } catch (error) {
        showToast('注册失败: ' + error.message, 'error');
    } finally {
        btn.innerText = originalText;
        btn.disabled = false;
    }
}

function showRegister() {
    navigateTo('register');
}

function showLogin() {
    navigateTo('login');
}

// 用户主动退出登录
async function doLogout() {
    if (!confirm('确认退出登录？')) return;
    try {
        await api.logout();
    } catch (e) {
        console.warn('logout api error', e);
    }
    // 清理本地状态
    try { localStorage.removeItem('user'); } catch (e) {}
    state.user = null;
    // 更新 UI 显示
    document.getElementById('userName') && (document.getElementById('userName').textContent = '请登录');
    document.getElementById('streakDays') && (document.getElementById('streakDays').textContent = '0');
    document.getElementById('totalPoints') && (document.getElementById('totalPoints').textContent = '0');
    applyNavPermissionCheck();
    showToast('已退出登录', 'success');
    navigateTo('login');
}

// 用户管理页面加载
async function loadUserManagementData() {
    const userListEl = document.getElementById('userList');
    if (!userListEl) return;

    const users = await api.getUserList();
    if (!users || !users.data) {
        userListEl.innerHTML = '<div class="user-management-toolbar"></div><p class="empty-hint">加载失败</p>';
        return;
    }

    // 工具栏（必须在 users 获取之后）
    const toolbarHtml = '<div class="user-management-toolbar">' +
        '<span style="font-size:14px;color:#666;">共 ' + users.data.length + ' 个用户</span>' +
        '<button class="btn btn-primary btn-sm" onclick="showAddUserDialog()">' +
        '<i class="fas fa-plus"></i> 添加用户</button></div>';

    if (users.data.length === 0) {
        userListEl.innerHTML = toolbarHtml + '<p class="empty-hint">暂无用户</p>';
        return;
    }

    userListEl.innerHTML = toolbarHtml + users.data.map(user => `
        <div class="user-card">
            <div class="user-info">
                <div class="user-avatar">${(user.nickname || user.username).charAt(0).toUpperCase()}</div>
                <div class="user-details">
                    <div class="user-name">${user.nickname || user.username}</div>
                    <div class="user-email">${user.email || '-'}</div>
                </div>
            </div>
            <div class="user-meta">
                <span class="badge-${user.role}">${user.role === 'admin' ? '管理员' : '用户'}</span>
                <span class="badge-${user.status}">${user.status === 'active' ? '正常' : '禁用'}</span>
            </div>
            <div class="user-stats">
                <div class="stat-item">
                    <span class="stat-label">积分</span>
                    <span class="stat-value">${user.score || 0}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">连续学习</span>
                    <span class="stat-value">${user.streak || 0}天</span>
                </div>
            </div>
            <div class="user-actions">
                <button class="btn btn-sm btn-outline" onclick="editUser(${user.id})">编辑</button>
                <button class="btn btn-sm btn-outline" onclick="openAuthModal(${user.id})">授权</button>
                ${user.status === 'active'
                    ? `<button class="btn btn-sm btn-outline" onclick="toggleUserStatus(${user.id}, 'ban')">禁用</button>`
                    : `<button class="btn btn-sm btn-primary" onclick="toggleUserStatus(${user.id}, 'unban')">启用</button>`
                }
            </div>
        </div>
    `).join('');
}

// ── 模块权限常量 ──────────────────────────────────

const PRD_MODULES = [
    { key: 'map', name: '学习地图', group: '学习相关' },
    { key: 'learn', name: '知识点讲解（费曼学习法）', group: '学习相关' },
    { key: 'socratic', name: 'AI帮测（苏格拉底提问）', group: '学习相关' },
    { key: 'practice', name: '题目练习', group: '学习相关' },
    { key: 'wrong', name: '错题本', group: '学习相关' },
    { key: 'report', name: '学习报告', group: '学习相关' },
    { key: 'upload', name: '题库上传', group: '题库相关' },
    { key: 'question-bank', name: '题库管理', group: '题库相关' },
    { key: 'ai-qa', name: 'AI问答', group: 'AI相关' },
];

const DEFAULT_PERMISSIONS = PRD_MODULES.map(m => m.key);

const PAGE_PERMISSION_MAP = {
    'home': null,
    'map': 'map',
    'learn': 'learn',
    'practice': 'practice',
    'wrong': 'wrong',
    'report': 'report',
    'upload': 'upload',
    'question-bank': 'question-bank',
    'ai-qa': 'ai-qa',
    'user-management': null,
    'login': null,
    'register': null,
};

// ── 编辑用户模态框 ──────────────────────────────────

async function openEditUserModal(userId) {
    const user = await api.getUserById(userId);
    if (!user) { showToast('用户不存在', 'error'); return; }
    document.getElementById('editUserId').value = user.id;
    document.getElementById('editUsername').value = user.username;
    document.getElementById('editNickname').value = user.nickname || '';
    document.getElementById('editEmail').value = user.email || '';
    document.getElementById('editRole').value = user.role === 'admin' ? 'admin' : 'user';
    document.getElementById('editStatus').value = user.status === 'banned' ? 'banned' : 'active';
    document.getElementById('editUserModal').style.display = 'flex';
}

function closeEditUserModal() {
    document.getElementById('editUserModal').style.display = 'none';
}

async function saveEditUser() {
    const userId = parseInt(document.getElementById('editUserId').value);
    const data = {
        nickname: document.getElementById('editNickname').value.trim(),
        email: document.getElementById('editEmail').value.trim(),
        role: document.getElementById('editRole').value,
        status: document.getElementById('editStatus').value,
    };
    const result = await api.updateUser(userId, data);
    if (result && result.message) {
        showToast(result.message, 'success');
        closeEditUserModal();
        loadUserManagementData();
    }
}

// ── 功能授权模态框 ──────────────────────────────────

let currentAuthUserId = null;
let currentAuthPermissions = [];

function openAuthModal(userId) {
    currentAuthUserId = userId;
    document.getElementById('authModal').style.display = 'flex';
    document.getElementById('authUserInfo').textContent = '加载中...';
    renderAuthModules([]);
    loadAuthUserData(userId);
}

function closeAuthModal() {
    document.getElementById('authModal').style.display = 'none';
    currentAuthUserId = null;
    currentAuthPermissions = [];
}

async function loadAuthUserData(userId) {
    const user = await api.getUserById(userId);
    if (!user) { document.getElementById('authUserInfo').textContent = '用户不存在'; return; }
    document.getElementById('authUserInfo').textContent = '当前用户：' + (user.nickname || user.username);
    currentAuthPermissions = user.permissions || [];
    renderAuthModules(currentAuthPermissions);
}

function renderAuthModules(selectedPerms) {
    const container = document.getElementById('authModuleList');
    const groups = [...new Set(PRD_MODULES.map(m => m.group))];
    container.innerHTML = groups.map(group => {
        const modules = PRD_MODULES.filter(m => m.group === group);
        return '<div class="auth-module-group"><h4>' + group + '</h4>' +
            modules.map(m => {
                const checked = selectedPerms.includes(m.key) ? 'checked' : '';
                return '<div class="auth-module-item"><label>' + m.name + '</label>' +
                    '<label class="auth-toggle">' +
                    '<input type="checkbox" ' + checked +
                    ' onchange="toggleAuthModule(\'' + m.key + '\', this.checked)">' +
                    '<span class="auth-toggle-slider"></span></label></div>';
            }).join('') + '</div>';
    }).join('');
}

function toggleAuthModule(key, checked) {
    if (checked) {
        if (!currentAuthPermissions.includes(key)) { currentAuthPermissions.push(key); }
    } else {
        currentAuthPermissions = currentAuthPermissions.filter(k => k !== key);
    }
}

async function saveAuthPermissions() {
    if (!currentAuthUserId) return;
    const result = await api.updateUserPermissions(currentAuthUserId, currentAuthPermissions);
    if (result && result.message) {
        showToast(result.message, 'success');
        closeAuthModal();
        loadUserManagementData();
    }
}

function resetAuthDefaults() {
    currentAuthPermissions = [...DEFAULT_PERMISSIONS];
    renderAuthModules(currentAuthPermissions);
}

// ── 用户管理操作 ──────────────────────────────────

async function editUser(userId) { await openEditUserModal(userId); }

async function toggleUserStatus(userId, action) {
    const confirmMsg = action === 'ban' ? '确定要禁用此用户吗？' : '确定要启用此用户吗？';
    if (!confirm(confirmMsg)) return;
    const result = action === 'ban' ? await api.banUser(userId) : await api.unbanUser(userId);
    if (result && result.message) {
        showToast(result.message, 'success');
        loadUserManagementData();
    }
}

// ── 添加用户 ──────────────────────────────────

function showAddUserDialog() {
    const modal = document.getElementById('addUserModal');
    if (!modal) return;
    modal.style.display = 'flex';
    document.getElementById('addUsername').value = '';
    document.getElementById('addPassword').value = '';
    document.getElementById('addNickname').value = '';
    document.getElementById('addEmail').value = '';
}

function closeAddUserDialog() {
    const modal = document.getElementById('addUserModal');
    if (!modal) return;
    modal.style.display = 'none';
}

async function createUserFromForm() {
    const username = document.getElementById('addUsername').value.trim();
    const password = document.getElementById('addPassword').value;
    const nickname = document.getElementById('addNickname').value.trim() || username;
    const email = document.getElementById('addEmail').value.trim();

    if (!username || !password) {
        showToast('用户名和密码为必填项', 'warning');
        return;
    }

    const result = await api.createUser({ username, password, nickname, email });
    if (result && result.message) {
        showToast(result.message, 'success');
        closeAddUserDialog();
        loadUserManagementData();
    } else {
        showToast(result?.detail || '添加用户失败', 'error');
    }
}

// ── 用户管理导航可见性 ──────────────────────────────────

function showUserManagementNav(role) {
    const nav = document.getElementById('userManagementNav');
    if (nav) { nav.style.display = role === 'admin' ? 'block' : 'none'; }
}

// ── 导航权限校验 ──────────────────────────────────

function applyNavPermissionCheck() {
    const userStr = localStorage.getItem('user');
    if (!userStr) return;
    let user;
    try { user = JSON.parse(userStr); } catch { return; }
    const permissions = user.permissions || [];
    const role = user.role || 'user';
    document.querySelectorAll('.nav-item').forEach(item => {
        const page = item.getAttribute('data-page');
        if (!page) return;
        if (page === 'user-management') {
            item.style.display = role === 'admin' ? '' : 'none';
            return;
        }
        const requiredPerm = PAGE_PERMISSION_MAP[page];
        if (requiredPerm && !permissions.includes(requiredPerm)) {
            item.classList.add('nav-disabled');
            item.title = '该功能未授权，请联系管理员';
        } else {
            item.classList.remove('nav-disabled');
            item.title = '';
        }
    });
}

function afterLogin(userData) {
    localStorage.setItem('user', JSON.stringify(userData));
    showUserManagementNav(userData.role);
    applyNavPermissionCheck();
    loadUserInfo();
    navigateTo('map');
}