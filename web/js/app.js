/**
 * ZAccount 前端应用主文件
 * 负责初始化 Amis 应用和页面路由
 */

// 等待 Amis 加载完成
function initApp() {
    // SDK 版本使用 amisRequire
    let amisEmbed;
    if (typeof amisRequire !== 'undefined') {
        amisEmbed = amisRequire('amis/embed');
    } else if (typeof amis !== 'undefined') {
        amisEmbed = amis;
    } else {
        setTimeout(initApp, 100);
        return;
    }

    // 应用配置
    const appConfig = {
        type: 'page',
        title: 'ZAccount - 记账系统',
        body: [
            {
                type: 'tabs',
                tabsMode: 'line',
                className: 'm-t-lg',
                tabs: [
                    {
                        title: '概览',
                        tab: [
                            {
                                type: 'container',
                                className: 'tab-content',
                                body: [
                                    {
                                        type: 'tpl',
                                        tpl: '<div style="text-align: center; padding: 40px; color: #999;">概览页面内容待开发</div>'
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        title: '交易记录',
                        tab: [
                            {
                                type: 'container',
                                className: 'tab-content',
                                body: [
                                    {
                                        type: 'tpl',
                                        tpl: '<div style="text-align: center; padding: 40px; color: #999;">交易记录页面内容待开发</div>'
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        title: '统计分析',
                        tab: [
                            {
                                type: 'container',
                                className: 'tab-content',
                                body: [
                                    {
                                        type: 'tpl',
                                        tpl: '<div style="text-align: center; padding: 40px; color: #999;">统计分析页面内容待开发</div>'
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    };

    // 渲染应用
    amisEmbed.embed('#root', appConfig);
}

// 页面加载完成后初始化应用
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}

