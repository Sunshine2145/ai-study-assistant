/**
 * AI伴学系统 - 主JavaScript文件
 * 实现界面交互功能
 */

// ========================================
// 页面导航
// ========================================
function navigateTo(page) {
    // 隐藏所有页面
    const pages = document.querySelectorAll('.page');
    pages.forEach(p => {
        p.style.display = 'none';
        p.classList.remove('active');
    });
    
    // 显示目标页面
    const targetPage = document.getElementById(`page-${page}`);
    if (targetPage) {
        targetPage.style.display = 'block';
        targetPage.classList.add('active');
    }
    
    // 更新导航状态
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => item.classList.remove('active'));
    
    const activeNav = document.querySelector(`.nav-item[data-page="${page}"]`);
    if (activeNav) {
        activeNav.classList.add('active');
    }
    
    // 更新页面标题
    const pageTitles = {
        'home': '学习首页',
        'learn': '开始学习',
        'map': '学习地图',
        'practice': '题目练习',
        'wrong': '错题本',
        'report': '学习报告'
    };
    
    const pageTitle = document.getElementById('pageTitle');
    if (pageTitle && pageTitles[page]) {
        pageTitle.textContent = pageTitles[page];
    }
    
    // 关闭移动端侧边栏
    const sidebar = document.getElementById('sidebar');
    if (window.innerWidth <= 1024) {
        sidebar.classList.remove('open');
    }
}

// ========================================
// 侧边栏控制
// ========================================
function initSidebar() {
    const menuBtn = document.getElementById('menuBtn');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    
    if (menuBtn) {
        menuBtn.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
    }
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.remove('open');
        });
    }
    
    // 点击导航项后关闭移动端侧边栏
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.getAttribute('data-page');
            if (page) {
                navigateTo(page);
            }
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
    const analysisCard = document.getElementById('analysisCard');
    
    let selectedAnswer = null;
    
    // 选项点击事件
    options.forEach(option => {
        option.addEventListener('click', () => {
            // 如果已经显示答案，不允许重新选择
            if (analysisCard.style.display === 'block') return;
            
            // 清除其它选项的选中状态
            options.forEach(opt => opt.classList.remove('selected'));
            
            // 选中当前选项
            option.classList.add('selected');
            selectedAnswer = option.querySelector('input[type="radio"]').value;
        });
    });
    
    // 提交答案
    if (submitBtn) {
        submitBtn.addEventListener('click', () => {
            if (!selectedAnswer) {
                showToast('请先选择一个答案', 'warning');
                return;
            }
            
            // 正确答案
            const correctAnswer = 'B';
            
            // 显示正确答案和错误答案
            options.forEach(option => {
                const input = option.querySelector('input[type="radio"]');
                const value = input.value;
                
                if (value === correctAnswer) {
                    option.classList.add('correct');
                } else if (value === selectedAnswer && value !== correctAnswer) {
                    option.classList.add('wrong');
                }
            });
            
            // 显示解析
            analysisCard.style.display = 'block';
            
            // 切换按钮
            submitBtn.style.display = 'none';
            nextBtn.style.display = 'inline-flex';
            
            // 显示提示
            if (selectedAnswer === correctAnswer) {
                showToast('回答正确！ +10分', 'success');
            } else {
                showToast('回答错误，已收录到错题本', 'error');
            }
        });
    }
}

// ========================================
// 学习地图 - 阶段切换
// ========================================
function initStageTabs() {
    const stageTabs = document.querySelectorAll('.stage-tab');
    
    stageTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // 更新标签页状态
            stageTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            // 获取阶段信息
            const stage = tab.getAttribute('data-stage');
            updateStageContent(stage);
        });
    });
}

function updateStageContent(stage) {
    // 阶段信息映射
    const stageInfo = {
        '1': {
            title: '第一阶段：计算机系统基本知识',
            desc: '第1-10天 | 建议25个知识点',
            progress: 20,
            completed: 5,
            total: 25
        },
        '2': {
            title: '第二阶段：信息系统基础',
            desc: '第11-15天 | 建议15个知识点',
            progress: 0,
            completed: 0,
            total: 15
        },
        '3': {
            title: '第三阶段：信息安全技术',
            desc: '第16-18天 | 建议10个知识点',
            progress: 0,
            completed: 0,
            total: 10
        },
        '4': {
            title: '第四阶段：软件工程',
            desc: '第19-25天 | 建议15个知识点',
            progress: 0,
            completed: 0,
            total: 15
        },
        '5': {
            title: '第五阶段：数据库设计',
            desc: '第26-30天 | 建议10个知识点',
            progress: 0,
            completed: 0,
            total: 10
        },
        '6': {
            title: '第六阶段：系统架构设计',
            desc: '第31-38天 | 建议15个知识点',
            progress: 0,
            completed: 0,
            total: 15
        }
    };
    
    const info = stageInfo[stage];
    if (!info) return;
    
    // 更新页面内容
    const stageInfoEl = document.querySelector('.stage-info');
    if (stageInfoEl) {
        stageInfoEl.querySelector('h2').textContent = info.title;
        stageInfoEl.querySelector('p').textContent = info.desc;
        
        const progressBar = stageInfoEl.querySelector('.progress-fill');
        const progressText = stageInfoEl.querySelector('.progress-text');
        progressBar.style.width = `${info.progress}%`;
        progressText.textContent = `已完成 ${info.completed}/${info.total} 知识点 (${info.progress}%)`;
    }
}

// ========================================
// 聊天界面功能
// ========================================
function initChat() {
    const sendBtn = document.getElementById('sendBtn');
    const userInput = document.getElementById('userInput');
    const chatMessages = document.getElementById('chatMessages');
    
    if (sendBtn && userInput && chatMessages) {
        sendBtn.addEventListener('click', () => sendMessage());
        userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
    
    function sendMessage() {
        const text = userInput.value.trim();
        if (!text) return;
        
        // 添加用户消息
        const userMsg = createMessage(text, 'user');
        chatMessages.appendChild(userMsg);
        
        // 清空输入框
        userInput.value = '';
        
        // 滚动到底部
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // 模拟AI回复（延迟1秒）
        setTimeout(() => {
            const aiResponse = getAIResponse(text);
            const aiMsg = createMessage(aiResponse, 'ai');
            chatMessages.appendChild(aiMsg);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }, 1000);
    }
    
    function createMessage(text, type) {
        const div = document.createElement('div');
        div.className = `message ${type}-message`;
        
        const avatarIcon = type === 'ai' ? 'fa-robot' : 'fa-user';
        const avatarBg = type === 'ai' ? 'var(--primary-bg)' : 'var(--success-light)';
        const avatarColor = type === 'ai' ? 'var(--primary)' : 'var(--success)';
        
        const senderName = type === 'ai' ? 'AI伴学助手' : '谭晓磊';
        const bgColor = type === 'ai' ? 'var(--bg-secondary)' : 'var(--primary)';
        const textColor = type === 'ai' ? 'var(--text-primary)' : 'white';
        
        const time = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
        
        if (type === 'ai') {
            div.innerHTML = `
                <div class="message-avatar" style="background: ${avatarBg}; color: ${avatarColor};">
                    <i class="fas ${avatarIcon}"></i>
                </div>
                <div class="message-content">
                    <div class="message-sender">${senderName}</div>
                    <div class="message-text" style="background: ${bgColor}; color: ${textColor};">
                        ${formatText(text)}
                    </div>
                    <div class="message-time">${time}</div>
                </div>
            `;
        } else {
            div.innerHTML = `
                <div class="message-content">
                    <div class="message-text" style="background: ${bgColor}; color: ${textColor};">
                        ${formatText(text)}
                    </div>
                    <div class="message-time">${time}</div>
                </div>
                <div class="message-avatar" style="background: ${avatarBg}; color: ${avatarColor};">
                    <i class="fas ${avatarIcon}"></i>
                </div>
            `;
        }
        
        return div;
    }
    
    function formatText(text) {
        // 简单的文本格式化
        return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                  .replace(/\n/g, '<br>');
    }
    
    function getAIResponse(userText) {
        // 简单的模拟回复逻辑
        const responses = [
            '很好的理解！让我再问你一个问题：为什么RISC指令集通常需要更多的指令来完成同样的任务？',
            '你的思考方向是对的。让我们继续深入：CISC和RISC在编译器设计上有什么不同的要求？',
            '说得好！现在让我们做个小测试，来做几道题巩固一下这个知识点吧。',
            '理解得很到位！这就是费曼学习法的精髓 - 用简单的语言讲清楚复杂的概念。'
        ];
        
        return responses[Math.floor(Math.random() * responses.length)];
    }
}

// ========================================
// Toast提示
// ========================================
function showToast(message, type = 'info') {
    // 创建toast元素
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icons = {
        'success': 'fa-check-circle',
        'error': 'fa-exclamation-circle',
        'warning': 'fa-exclamation-triangle',
        'info': 'fa-info-circle'
    };
    
    const colors = {
        'success': 'var(--success)',
        'error': 'var(--error)',
        'warning': 'var(--warning)',
        'info': 'var(--primary)'
    };
    
    toast.innerHTML = `
        <i class="fas ${icons[type]}"></i>
        <span>${message}</span>
    `;
    
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        padding: 16px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        display: flex;
        align-items: center;
        gap: 12px;
        z-index: 1000;
        border-left: 4px solid ${colors[type]};
        animation: slideInRight 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    // 3秒后移除
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
    
    // 添加动画样式（如果不存在）
    if (!document.getElementById('toast-styles')) {
        const style = document.createElement('style');
        style.id = 'toast-styles';
        style.textContent = `
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOutRight {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
}

// ========================================
// 初始化
// ========================================
document.addEventListener('DOMContentLoaded', () => {
    initSidebar();
    initPractice();
    initStageTabs();
    initChat();
    
    // 默认显示首页
    navigateTo('home');
    
    console.log('AI伴学系统界面已加载');
});
