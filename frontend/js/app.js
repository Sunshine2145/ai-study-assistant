/**
 * AI伴学系统 - 主JavaScript文件
 * 实现界面交互功能 + API集成
 */

// ========================================
// 配置
// ========================================
const API_BASE = 'http://localhost:8081/api';

// ========================================
// 状态管理
// ========================================
const state = {
    user: null,
    currentKnowledge: null,
    questions: [],
    currentQuestionIndex: 0,
    wrongQuestions: [],
    stageData: []
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

    async getUser() { return await this.request('/user/current'); },
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

    const pageTitles = { 'home': '学习首页', 'learn': '开始学习', 'map': '学习地图', 'practice': '题目练习', 'wrong': '错题本', 'report': '学习报告', 'upload': '题库上传', 'question-bank': '题库管理' };
    const pageTitle = document.getElementById('pageTitle');
    if (pageTitle && pageTitles[page]) pageTitle.textContent = pageTitles[page];

    const sidebar = document.getElementById('sidebar');
    if (window.innerWidth <= 1024) sidebar.classList.remove('open');

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
    if (!result || !result.data) { renderStageTabsDemo(); renderKnowledgePointsDemo(1); return; }
    state.stageData = result.data;
    const stages = [...new Set(result.data.map(k => k.stage))].sort();
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
            const matchingPoints = state.stageData.filter(k => k.stage === stage);
            if (matchingPoints.length > 0) {
                renderKnowledgePoints(stage);
            } else {
                renderKnowledgePointsDemo(parseInt(stage));
            }
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

        const masteryPercent = result.data.mastery_percentage || 0;
        const socraticRounds = result.data.socratic_rounds || 0;
        const canPractice = result.data.can_practice || false;
        const knowledgeName = result.data.knowledge_name || state.currentKnowledge?.name || '';

        if (knowledgeName) {
            document.getElementById('socraticText').textContent = `📚 ${knowledgeName} | 掌握度：${masteryPercent}%`;
        } else {
            document.getElementById('socraticText').textContent = `📊 掌握度：${masteryPercent}%`;
        }

        if (canPractice || masteryPercent >= 90) {
            showToast('🎉 恭喜！已达到90%掌握度！', 'success');
        }

        if (result.data.socratic_hint) {
            if (canPractice || masteryPercent >= 90) {
                document.getElementById('socraticText').textContent = '🎉 达成90%掌握度！可以解锁下一单元了';
            } else {
                document.getElementById('socraticText').textContent = result.data.socratic_hint;
            }
        }
    } else {
        setTimeout(() => {
            const responses = ['很好的理解！让我再问你一个问题：为什么RISC指令集通常需要更多的指令来完成同样的任务？', '你的思考方向是对的。让我们继续深入：CISC和RISC在编译器设计上有什么不同的要求？', '说得好！现在让我们做个小测试，来做几道题巩固一下这个知识点吧。', '理解得很到位！这就是费曼学习法的精髓 - 用简单的语言讲清楚复杂的概念。'];
            addAIMessage(responses[Math.floor(Math.random() * responses.length)]);
        }, 1000);
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

function formatText(text) { return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>'); }
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
    const result = await api.selectLearningUnit(knowledgeId);
    if (result && result.success) {
        showToast(`已选择「${knowledgeName}」，开始学习`, 'success');
        state.currentKnowledge = { id: knowledgeId, name: knowledgeName };
        await loadLearnDataWithFeynman(knowledgeId);
        navigateTo('learn');
    } else {
        showToast(result.message || '选择失败，请检查是否已解锁', 'error');
    }
}

async function loadLearnDataWithFeynman(knowledgeId) {
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.innerHTML = `<div class="message ai-message"><div class="message-avatar"><i class="fas fa-robot"></i></div><div class="message-content"><div class="message-sender">AI伴学助手</div><div class="message-text"><p>正在生成费曼讲解...</p></div><div class="message-time">${getCurrentTime()}</div></div></div>`;

    const mastery = await api.getMastery(knowledgeId);
    const masteryPercent = mastery?.mastery_percentage || 0;
    const socraticRounds = mastery?.socratic_rounds || 0;

    let stageIndicator = `<div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;">
        <span style="background:#2563EB;color:white;padding:4px 12px;border-radius:16px;font-size:12px;">1.费曼学习</span>
        <span style="color:#94a3b8;">→</span>
        <span style="background:#e2e8f0;color:#64748b;padding:4px 12px;border-radius:16px;font-size:12px;">2.苏格拉底</span>
        <span style="color:#94a3b8;">→</span>
        <span style="background:#e2e8f0;color:#64748b;padding:4px 12px;border-radius:16px;font-size:12px;">3.解锁下一单元</span>
    </div>`;

    const feynmanResult = await api.getFeynmanContent(knowledgeId);

    if (feynmanResult && feynmanResult.success && feynmanResult.data) {
        const feynmanContent = feynmanResult.data.content;
        const knowledgeName = feynmanResult.data.knowledge_name;
        state.currentKnowledge = { id: knowledgeId, name: knowledgeName };
        chatMessages.innerHTML = '';
        addAIMessage(`<p style="margin-bottom:16px;">欢迎开始学习之旅！</p>${stageIndicator}<div class="feynman-card"><div class="feynman-header"><i class="fas fa-lightbulb"></i><strong>费曼学习法讲解：${knowledgeName}</strong></div><div class="feynman-content">${feynmanContent}</div></div><p style="margin-top:16px;">学完以后，用一句话解释一下这个概念~</p><div style="margin-top:12px;padding:12px;background:#fef3c7;border-radius:8px;"><i class="fas fa-target"></i> <strong>学习目标：</strong>通过苏格拉底问答达到90%掌握度后解锁下一单元</div>`);
    } else {
        chatMessages.innerHTML = '';
        addAIMessage(`<p style="margin-bottom:16px;">欢迎开始学习之旅！</p>${stageIndicator}<p>知识点讲解内容正在准备中，请先尝试用自己的语言描述一下这个概念。</p><div style="margin-top:12px;padding:12px;background:#fef3c7;border-radius:8px;"><i class="fas fa-target"></i> <strong>学习目标：</strong>通过苏格拉底问答达到90%掌握度后解锁下一单元</div>`);
    }

    const knowledgeName = feynmanResult?.data?.knowledge_name || state.currentKnowledge?.name || '当前知识点';
    document.getElementById('socraticText').textContent = `📚 ${knowledgeName} | 掌握度：${masteryPercent}%`;
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

    const uploadResult = document.getElementById('uploadResult');
    const resultMessage = document.getElementById('resultMessage');
    const totalFound = document.getElementById('totalFound');
    const importedCount = document.getElementById('importedCount');

    // Clear file input so same file can be selected again
    fileInput.value = '';

    if (result && result.success) {
        uploadResult.style.display = 'block';
        resultMessage.textContent = '上传成功！';
        totalFound.textContent = result.total_found || 0;
        importedCount.textContent = result.imported || 0;
        showToast(result.message || '导入成功', 'success');
    } else {
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
// 初始化
// ========================================
document.addEventListener('DOMContentLoaded', () => {
    initSidebar();
    initPractice();
    initStageTabs();
    initChat();
    initUpload();
    navigateTo('map');
    console.log('AI伴学系统界面已加载');
});