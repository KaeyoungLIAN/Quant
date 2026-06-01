import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'Quant Wiki',
  description: '量化 & AI 技术知识库',
  lang: 'zh-CN',

  head: [
    ['link', { rel: 'icon', href: '/favicon.svg' }],
    ['meta', { name: 'theme-color', content: '#0ea5e9' }],
  ],

  themeConfig: {
    logo: '/logo.svg',

    nav: [
      { text: '首页', link: '/' },
      { text: '量化金融', link: '/quant-finance/' },
      { text: '前置数学知识', link: '/prerequisite-math/' },
      { text: 'AI 技术与工具', link: '/ai/' },
      { text: '技术栈', link: '/tech-stack/' },
      { text: '资源收藏', link: '/resources/' },
    ],

    sidebar: {
      '/quant-finance/': [
        {
          text: '量化金融',
          collapsible: false,
          items: [
            { text: '概述', link: '/quant-finance/' },
          ],
        },
      ],
      '/prerequisite-math/': [
        {
          text: '前置数学知识',
          collapsible: false,
          items: [
            { text: '概述', link: '/prerequisite-math/' },
          ],
        },
        {
          text: '01 高等数学',
          collapsed: true,
          items: [
            { text: '1.1 极限与连续', link: '/prerequisite-math/01-calculus/1.1-limits-and-continuity' },
            { text: '1.2 导数与微分', link: '/prerequisite-math/01-calculus/1.2-derivatives' },
            { text: '1.3 积分学', link: '/prerequisite-math/01-calculus/1.3-integration' },
            { text: '1.4 多元微积分', link: '/prerequisite-math/01-calculus/1.4-multivariable-calculus' },
          ],
        },
        {
          text: '02 线性代数',
          collapsed: true,
          items: [
            { text: '2.1 向量与矩阵', link: '/prerequisite-math/02-linear-algebra/2.1-vectors-matrices' },
            { text: '2.2 线性方程组', link: '/prerequisite-math/02-linear-algebra/2.2-linear-equations' },
            { text: '2.3 正定矩阵与二次型', link: '/prerequisite-math/02-linear-algebra/2.3-positive-definite' },
            { text: '2.4 特征值分解与SVD', link: '/prerequisite-math/02-linear-algebra/2.4-eigen-decomposition' },
            { text: '2.5 PCA', link: '/prerequisite-math/02-linear-algebra/2.5-pca' },
            { text: '2.6 矩阵微积分', link: '/prerequisite-math/02-linear-algebra/2.6-matrix-calculus' },
          ],
        },
        {
          text: '03 概率论',
          collapsed: true,
          items: [
            { text: '3.1 概率空间与条件概率', link: '/prerequisite-math/03-probability/3.1-probability-space' },
            { text: '3.2 随机变量与分布', link: '/prerequisite-math/03-probability/3.2-random-variables' },
            { text: '3.3 期望、方差与条件期望', link: '/prerequisite-math/03-probability/3.3-expectation-variance' },
            { text: '3.4 贝叶斯定理与不等式', link: '/prerequisite-math/03-probability/3.4-conditional-probability' },
            { text: '3.5 大数定律与中心极限定理', link: '/prerequisite-math/03-probability/3.5-lln-clt' },
          ],
        },
        {
          text: '04 数理统计',
          collapsed: true,
          items: [
            { text: '4.1 参数估计', link: '/prerequisite-math/04-statistics/4.1-parameter-estimation' },
            { text: '4.2 假设检验', link: '/prerequisite-math/04-statistics/4.2-hypothesis-testing' },
            { text: '4.3 方差分析(ANOVA)', link: '/prerequisite-math/04-statistics/4.3-anova' },
            { text: '4.4 回归分析', link: '/prerequisite-math/04-statistics/4.4-regression' },
            { text: '4.5 时间序列分析', link: '/prerequisite-math/04-statistics/4.5-time-series' },
          ],
        },
        {
          text: '05 最优化理论',
          collapsed: true,
          items: [
            { text: '概述', link: '/prerequisite-math/05-optimization/' },
          ],
        },
        {
          text: '06 随机过程',
          collapsed: true,
          items: [
            { text: '概述', link: '/prerequisite-math/06-stochastic-processes/' },
          ],
        },
        {
          text: '07 信息论',
          collapsed: true,
          items: [
            { text: '概述', link: '/prerequisite-math/07-information-theory/' },
          ],
        },
        {
          text: '08 傅里叶分析',
          collapsed: true,
          items: [
            { text: '概述', link: '/prerequisite-math/08-fourier-analysis/' },
          ],
        },
        {
          text: '09 数值计算',
          collapsed: true,
          items: [
            { text: '概述', link: '/prerequisite-math/09-numerical-computing/' },
          ],
        },
        {
          text: '10 图论基础',
          collapsed: true,
          items: [
            { text: '概述', link: '/prerequisite-math/10-graph-theory/' },
          ],
        },
      ],
      '/ai/': [
        {
          text: 'AI 技术与工具',
          items: [
            { text: '概述', link: '/ai/' },
          ],
        },
      ],
      '/tech-stack/': [
        {
          text: '技术栈',
          items: [
            { text: '概述', link: '/tech-stack/' },
          ],
        },
      ],
      '/resources/': [
        {
          text: '资源收藏',
          items: [
            { text: '资料索引', link: '/resources/' },
          ],
        },
      ],
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/KaeyoungLIAN/Quant' },
    ],

    footer: {
      message: 'Built with VitePress',
      copyright: 'Copyright © 2026 Kaeyoung',
    },

    search: {
      provider: 'local',
    },

    editLink: {
      pattern: 'https://github.com/KaeyoungLIAN/Quant/edit/main/docs/:path',
      text: '在 GitHub 上编辑此页',
    },

    lastUpdated: {
      text: '最后更新',
    },
  },

  cleanUrls: true,
  lastUpdated: true,
})
