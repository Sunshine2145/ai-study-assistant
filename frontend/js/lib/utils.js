/**
 * 前端纯函数工具库（可单元测试，无 DOM 依赖）
 */

export const PAGE_TITLES = {
    home: '学习首页',
    learn: '开始学习',
    map: '学习地图',
    practice: '题目练习',
    wrong: '错题本',
    report: '学习报告',
    upload: '题库上传',
    'question-bank': '题库管理',
    'ai-qa': 'AI问答',
    'user-management': '用户管理',
    login: '登录',
    register: '注册',
};

export const PRD_MODULES = [
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

export const DEFAULT_PERMISSIONS = PRD_MODULES.map((m) => m.key);

export const PAGE_PERMISSION_MAP = {
    home: null,
    map: 'map',
    learn: 'learn',
    practice: 'practice',
    wrong: 'wrong',
    report: 'report',
    upload: 'upload',
    'question-bank': 'question-bank',
    'ai-qa': 'ai-qa',
    'user-management': null,
    login: null,
    register: null,
};

const QUESTION_TYPE_LABELS = {
    single: '单项选择题',
    multi: '多项选择题',
    judge: '判断题',
};

/** 将 Markdown 粗体与换行转为 HTML */
export function formatText(text) {
    return String(text)
        .replace(/\*\*(.*?)\*\*/g, '<span class="knowledge-tag" onclick="showKnowledgeCard(\'$1\')">$1</span>')
        .replace(/\n/g, '<br>');
}

export function getPageTitle(page) {
    return PAGE_TITLES[page] || 'AI伴学系统';
}

export function getQuestionTypeLabel(type) {
    return QUESTION_TYPE_LABELS[type] || '选择题';
}

/** 练习进度百分比（index 从 0 开始） */
export function calcPracticeProgress(index, total) {
    if (!total || total <= 0) {
        return { percent: 0, widthPercent: '0' };
    }
    const ratio = (index + 1) / total;
    return {
        percent: Math.round(ratio * 100),
        widthPercent: String(ratio * 100),
    };
}

export function buildUploadQuestionsUrl(apiBase, useAiParse = true, aiProvider = 'deepseek') {
    const base = apiBase.replace(/\/$/, '');
    const params = useAiParse
        ? `?use_ai_parse=true&ai_provider=${encodeURIComponent(aiProvider)}`
        : '?use_ai_parse=false';
    return `${base}/upload/questions${params}`;
}

/** 比较用户答案与正确答案（忽略大小写与首尾空白） */
export function checkAnswerMatch(userAnswer, correctAnswer) {
    return (
        String(userAnswer).trim().toLowerCase() ===
        String(correctAnswer).trim().toLowerCase()
    );
}

export function parseStoredUser(userStr) {
    if (!userStr) return null;
    try {
        const user = JSON.parse(userStr);
        if (!user || typeof user !== 'object') return null;
        return user;
    } catch {
        return null;
    }
}

export function shouldShowAdminNav(role) {
    return role === 'admin';
}

/** 判断用户是否拥有某页面权限 */
export function hasPagePermission(permissions, role, page) {
    if (page === 'user-management') {
        return role === 'admin';
    }
    const required = PAGE_PERMISSION_MAP[page];
    if (!required) return true;
    return Array.isArray(permissions) && permissions.includes(required);
}

/** 导航项展示状态（供 applyNavPermissionCheck 使用） */
export function getNavItemDisplayState(user, page) {
    const role = user.role || 'user';
    const permissions = user.permissions || [];

    if (page === 'user-management') {
        return {
            hide: !shouldShowAdminNav(role),
            disabled: false,
            title: '',
        };
    }

    const requiredPerm = PAGE_PERMISSION_MAP[page];
    if (requiredPerm && !permissions.includes(requiredPerm)) {
        return {
            hide: false,
            disabled: true,
            title: '该功能未授权，请联系管理员',
        };
    }

    return { hide: false, disabled: false, title: '' };
}

/** 切换权限列表中的模块 key */
export function togglePermission(permissions, key, checked) {
    const list = Array.isArray(permissions) ? [...permissions] : [];
    if (checked) {
        return list.includes(key) ? list : [...list, key];
    }
    return list.filter((k) => k !== key);
}

/** 学习阶段指示器 HTML */
export function renderPhaseIndicatorHtml(currentPhase) {
    const phases = [
        { key: 'feynman', label: '1.费曼学习' },
        { key: 'interactive', label: '2.互动学习' },
        { key: 'socratic', label: '3.苏格拉底检验' },
    ];
    const phaseOrder = ['feynman', 'interactive', 'socratic', 'completed'];
    const currentIdx = phaseOrder.indexOf(currentPhase);

    const inner = phases
        .map((p) => {
            const pIdx = phaseOrder.indexOf(p.key);
            const isCompleted = currentIdx > pIdx || currentPhase === 'completed';
            const isCurrent = currentPhase === p.key;
            let bg;
            let color;
            if (isCompleted) {
                bg = '#10B981';
                color = 'white';
            } else if (isCurrent) {
                bg = '#2563EB';
                color = 'white';
            } else {
                bg = '#e2e8f0';
                color = '#64748b';
            }
            const checkmark = isCompleted ? '✓ ' : '';
            return `<span style="background:${bg};color:${color};padding:4px 12px;border-radius:16px;font-size:12px;">${checkmark}${p.label}</span>`;
        })
        .join('<span style="color:#94a3b8;">→</span>');

    return `<div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;flex-wrap:wrap;">${inner}</div>`;
}
