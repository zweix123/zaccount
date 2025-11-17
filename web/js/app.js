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
                className: 'm-t-sm',
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
                        title: '添加交易',
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
                                    // 初始化服务：获取默认时间
                                    {
                                        type: 'service',
                                        api: {
                                            method: 'get',
                                            url: '/config/init',
                                            adaptor: 'return {status: 0, data: {start_date: payload.earliest_date, end_date: payload.latest_date}};'
                                        },
                                        name: 'initService',
                                        body: [
                                            // 日期选择表单
                                            {
                                                type: 'form',
                                                name: 'dateForm',
                                                wrapWithPanel: false,
                                                mode: 'horizontal',
                                                data: {
                                                    start_date: '${start_date}',
                                                    end_date: '${end_date}'
                                                },
                                                onEvent: {
                                                    submit: {
                                                        actions: [
                                                            {
                                                                actionType: 'ajax',
                                                                api: {
                                                                    method: 'get',
                                                                    url: '/display/common',
                                                                    data: {
                                                                        start_date: '${start_date}',
                                                                        end_date: '${end_date}'
                                                                    }
                                                                },
                                                                outputVar: 'analyzeData'
                                                            },
                                                            {
                                                                actionType: 'reload',
                                                                target: 'analyzeResult',
                                                                data: {
                                                                    income: '${analyzeData.income}',
                                                                    expense: '${analyzeData.expense}',
                                                                    balance: '${analyzeData.balance}'
                                                                }
                                                            }
                                                        ]
                                                    }
                                                },
                                                body: [
                                                    {
                                                        type: 'input-date',
                                                        name: 'start_date',
                                                        label: '开始日期',
                                                        format: 'YYYY-MM-DD',
                                                        required: true,
                                                        clearable: false
                                                    },
                                                    {
                                                        type: 'input-date',
                                                        name: 'end_date',
                                                        label: '结束日期',
                                                        format: 'YYYY-MM-DD',
                                                        required: true,
                                                        clearable: false
                                                    },
                                                    {
                                                        type: 'submit',
                                                        label: '确认',
                                                        level: 'primary',
                                                        className: 'ml-2'
                                                    }
                                                ]
                                            },
                                            // 数据展示容器：根据ajax返回的数据展示
                                            {
                                                type: 'service',
                                                name: 'analyzeResult',
                                                className: 'mt-3',
                                                visibleOn: 'typeof analyzeData !== "undefined" && analyzeData && analyzeData.income !== undefined',
                                                data: {
                                                    income: '${analyzeData.income}',
                                                    expense: '${analyzeData.expense}',
                                                    balance: '${analyzeData.balance}'
                                                },
                                                body: [
                                                    {
                                                        type: 'flex',
                                                        items: [
                                                            {
                                                                type: 'card',
                                                                className: 'flex-1 mr-2',
                                                                header: {
                                                                    title: '收入',
                                                                    className: 'text-success'
                                                                },
                                                                body: {
                                                                    type: 'tpl',
                                                                    tpl: '<div style="font-size: 24px; font-weight: bold; color: #52c41a;">¥${income|number:2}</div>'
                                                                }
                                                            },
                                                            {
                                                                type: 'card',
                                                                className: 'flex-1 mr-2',
                                                                header: {
                                                                    title: '支出',
                                                                    className: 'text-danger'
                                                                },
                                                                body: {
                                                                    type: 'tpl',
                                                                    tpl: '<div style="font-size: 24px; font-weight: bold; color: #ff4d4f;">¥${expense|number:2}</div>'
                                                                }
                                                            },
                                                            {
                                                                type: 'card',
                                                                className: 'flex-1',
                                                                header: {
                                                                    title: '结余',
                                                                    className: 'text-primary'
                                                                },
                                                                body: {
                                                                    type: 'tpl',
                                                                    tpl: '<div style="font-size: 24px; font-weight: bold; color: #1890ff;">¥${balance|number:2}</div>'
                                                                }
                                                            }
                                                        ]
                                                    }
                                                ]
                                            }
                                        ]
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

