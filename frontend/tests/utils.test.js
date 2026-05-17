import { describe, it, expect } from 'vitest';
import {
    PAGE_TITLES,
    PRD_MODULES,
    DEFAULT_PERMISSIONS,
    PAGE_PERMISSION_MAP,
    formatText,
    getPageTitle,
    getQuestionTypeLabel,
    calcPracticeProgress,
    buildUploadQuestionsUrl,
    checkAnswerMatch,
    parseStoredUser,
    shouldShowAdminNav,
    hasPagePermission,
    getNavItemDisplayState,
    togglePermission,
    renderPhaseIndicatorHtml,
} from '../js/lib/utils.js';

describe('formatText', () => {
    it('converts bold markdown to knowledge-tag span', () => {
        const result = formatText('这是**Cache**的概念');
        expect(result).toContain('knowledge-tag');
        expect(result).toContain('Cache');
        expect(result).toContain("showKnowledgeCard('Cache')");
    });

    it('converts newlines to br', () => {
        expect(formatText('第一行\n第二行')).toBe('第一行<br>第二行');
    });
});

describe('getPageTitle', () => {
    it('returns title for known page', () => {
        expect(getPageTitle('map')).toBe('学习地图');
        expect(getPageTitle('ai-qa')).toBe('AI问答');
    });

    it('returns default for unknown page', () => {
        expect(getPageTitle('unknown-page')).toBe('AI伴学系统');
    });
});

describe('getQuestionTypeLabel', () => {
    it('maps question types', () => {
        expect(getQuestionTypeLabel('single')).toBe('单项选择题');
        expect(getQuestionTypeLabel('multi')).toBe('多项选择题');
        expect(getQuestionTypeLabel('judge')).toBe('判断题');
    });

    it('falls back for unknown type', () => {
        expect(getQuestionTypeLabel('essay')).toBe('选择题');
    });
});

describe('calcPracticeProgress', () => {
    it('calculates percent for middle question', () => {
        expect(calcPracticeProgress(2, 5)).toEqual({ percent: 60, widthPercent: '60' });
    });

    it('returns zero when total is zero', () => {
        expect(calcPracticeProgress(0, 0)).toEqual({ percent: 0, widthPercent: '0' });
    });

    it('first question of five is 20%', () => {
        expect(calcPracticeProgress(0, 5).percent).toBe(20);
    });
});

describe('buildUploadQuestionsUrl', () => {
    const base = 'http://localhost:5001/api';

    it('builds AI parse URL with provider', () => {
        const url = buildUploadQuestionsUrl(base, true, 'deepseek');
        expect(url).toBe('http://localhost:5001/api/upload/questions?use_ai_parse=true&ai_provider=deepseek');
    });

    it('builds URL without AI parse', () => {
        const url = buildUploadQuestionsUrl(base, false);
        expect(url).toBe('http://localhost:5001/api/upload/questions?use_ai_parse=false');
    });

    it('strips trailing slash from api base', () => {
        const url = buildUploadQuestionsUrl('http://localhost:5001/api/', true, 'minimax');
        expect(url).toContain('/api/upload/questions');
        expect(url).toContain('ai_provider=minimax');
    });
});

describe('checkAnswerMatch', () => {
    it('matches case-insensitively', () => {
        expect(checkAnswerMatch('a', 'A')).toBe(true);
        expect(checkAnswerMatch(' TRUE ', 'true')).toBe(true);
    });

    it('returns false for wrong answer', () => {
        expect(checkAnswerMatch('B', 'A')).toBe(false);
    });
});

describe('parseStoredUser', () => {
    it('parses valid JSON user', () => {
        const user = parseStoredUser(JSON.stringify({ username: 'u1', role: 'user' }));
        expect(user.username).toBe('u1');
    });

    it('returns null for invalid JSON', () => {
        expect(parseStoredUser('{bad')).toBeNull();
    });

    it('returns null for empty input', () => {
        expect(parseStoredUser('')).toBeNull();
        expect(parseStoredUser(null)).toBeNull();
    });
});

describe('shouldShowAdminNav', () => {
    it('only admin sees management nav', () => {
        expect(shouldShowAdminNav('admin')).toBe(true);
        expect(shouldShowAdminNav('user')).toBe(false);
    });
});

describe('hasPagePermission', () => {
    const perms = ['map', 'learn', 'practice'];

    it('admin can access user-management', () => {
        expect(hasPagePermission(perms, 'admin', 'user-management')).toBe(true);
    });

    it('user cannot access user-management', () => {
        expect(hasPagePermission(perms, 'user', 'user-management')).toBe(false);
    });

    it('home requires no permission', () => {
        expect(hasPagePermission([], 'user', 'home')).toBe(true);
    });

    it('checks mapped permission', () => {
        expect(hasPagePermission(perms, 'user', 'map')).toBe(true);
        expect(hasPagePermission(perms, 'user', 'upload')).toBe(false);
    });
});

describe('getNavItemDisplayState', () => {
    it('hides user-management for non-admin', () => {
        const state = getNavItemDisplayState({ role: 'user', permissions: [] }, 'user-management');
        expect(state.hide).toBe(true);
    });

    it('disables nav when permission missing', () => {
        const state = getNavItemDisplayState(
            { role: 'user', permissions: ['map'] },
            'upload'
        );
        expect(state.disabled).toBe(true);
        expect(state.title).toContain('未授权');
    });

    it('allows permitted page', () => {
        const state = getNavItemDisplayState(
            { role: 'user', permissions: ['map', 'upload'] },
            'upload'
        );
        expect(state.disabled).toBe(false);
        expect(state.hide).toBe(false);
    });
});

describe('togglePermission', () => {
    it('adds permission when checked', () => {
        expect(togglePermission(['map'], 'learn', true)).toEqual(['map', 'learn']);
    });

    it('does not duplicate permission', () => {
        expect(togglePermission(['map'], 'map', true)).toEqual(['map']);
    });

    it('removes permission when unchecked', () => {
        expect(togglePermission(['map', 'learn'], 'map', false)).toEqual(['learn']);
    });
});

describe('renderPhaseIndicatorHtml', () => {
    it('includes phase labels', () => {
        const html = renderPhaseIndicatorHtml('feynman');
        expect(html).toContain('1.费曼学习');
        expect(html).toContain('2.互动学习');
        expect(html).toContain('3.苏格拉底检验');
    });

    it('highlights current phase', () => {
        const html = renderPhaseIndicatorHtml('socratic');
        expect(html).toContain('#2563EB');
    });
});

describe('constants', () => {
    it('PRD_MODULES has nine modules', () => {
        expect(PRD_MODULES).toHaveLength(9);
    });

    it('DEFAULT_PERMISSIONS matches module keys', () => {
        expect(DEFAULT_PERMISSIONS).toEqual(PRD_MODULES.map((m) => m.key));
    });

    it('PAGE_TITLES covers main pages', () => {
        expect(PAGE_TITLES['map']).toBe('学习地图');
        expect(PAGE_PERMISSION_MAP.practice).toBe('practice');
    });
});
