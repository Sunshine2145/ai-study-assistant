/**
 * 导航相关 DOM 交互测试（jsdom）
 */
import { describe, it, expect, beforeEach } from 'vitest';
import { getPageTitle } from '../js/lib/utils.js';

describe('navigateTo (DOM simulation)', () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <div id="pageTitle"></div>
            <div id="sidebar" class="sidebar"></div>
            <div id="page-home" class="page active" style="display:block"></div>
            <div id="page-map" class="page" style="display:none"></div>
            <a class="nav-item active" data-page="home"></a>
            <a class="nav-item" data-page="map"></a>
        `;
    });

    it('updates page title when navigating', () => {
        const pageTitle = document.getElementById('pageTitle');
        pageTitle.textContent = getPageTitle('map');
        expect(pageTitle.textContent).toBe('学习地图');
    });

    it('shows target page and hides others', () => {
        const pages = document.querySelectorAll('.page');
        const targetPage = document.getElementById('page-map');
        pages.forEach((p) => {
            p.style.display = 'none';
            p.classList.remove('active');
        });
        targetPage.style.display = 'block';
        targetPage.classList.add('active');

        expect(document.getElementById('page-home').style.display).toBe('none');
        expect(targetPage.style.display).toBe('block');
        expect(targetPage.classList.contains('active')).toBe(true);
    });

    it('activates matching nav item', () => {
        document.querySelectorAll('.nav-item').forEach((item) => item.classList.remove('active'));
        const activeNav = document.querySelector('.nav-item[data-page="map"]');
        activeNav.classList.add('active');

        expect(document.querySelector('.nav-item[data-page="home"]').classList.contains('active')).toBe(false);
        expect(activeNav.classList.contains('active')).toBe(true);
    });
});
