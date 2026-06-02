import { defineConfig } from 'vitepress'
import { katex } from '@mdit/plugin-katex'

export default defineConfig({
  title: 'Quant Wiki',
  description: '量化 & AI 技术知识库',
  lang: 'zh-CN',

  head: [
    ['link', { rel: 'icon', href: '/favicon.svg' }],
    ['meta', { name: 'theme-color', content: '#0ea5e9' }],
    ['link', { rel: 'stylesheet', href: 'https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css' }],
  ],

  markdown: {
    config: (md) => {
      md.use(katex)
    }
  },

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
          text: '01 量化交易基础',
          collapsed: true,
          items: [
            { text: '1.0 概述', link: '/quant-finance/01.0-overview' },
            { text: '1.0 量化交易的本质', link: '/quant-finance/1.0-overview' },
            { text: '1.1 交易品种', link: '/quant-finance/1.1-market-instruments' },
            { text: '1.2 订单类型与市场机制', link: '/quant-finance/1.2-order-types' },
          ],
        },
        {
          text: '02 组合管理与风险',
          collapsed: true,
          items: [
            { text: '2.0 概述', link: '/quant-finance/02.0-overview' },
            { text: '2.0 组合收益与风险', link: '/quant-finance/2.0-portfolio-risk-return' },
            { text: '2.1 有效前沿与最优组合', link: '/quant-finance/2.1-efficient-frontier' },
            { text: '2.2 夏普比率与绩效度量', link: '/quant-finance/2.2-sharpe-ratio' },
            { text: '2.3 因子模型', link: '/quant-finance/2.3-factor-models' },
          ],
        },
        {
          text: '03 衍生品与定价',
          collapsed: true,
          items: [
            { text: '3.0 概述', link: '/quant-finance/03.0-overview' },
            { text: '3.0 货币时间价值', link: '/quant-finance/3.0-time-value-of-money' },
            { text: '3.1 债券定价与久期', link: '/quant-finance/3.1-bond-pricing' },
            { text: '3.2 期货定价', link: '/quant-finance/3.2-futures-pricing' },
            { text: '3.3 期权基础', link: '/quant-finance/3.3-options-intro' },
            { text: '3.4 Black-Scholes 定价模型', link: '/quant-finance/3.4-black-scholes' },
            { text: '3.5 Greeks 与风险管理', link: '/quant-finance/3.5-options-greeks' },
            { text: '3.6 期权策略', link: '/quant-finance/3.6-options-strategies' },
          ],
        },
        {
          text: '04 策略与回测',
          collapsed: true,
          items: [
            { text: '4.0 概述', link: '/quant-finance/04.0-overview' },
            { text: '4.0 趋势跟踪策略', link: '/quant-finance/4.0-strategy-trend' },
            { text: '4.1 均值回归策略', link: '/quant-finance/4.1-strategy-mean-reversion' },
            { text: '4.2 回测框架与方法论', link: '/quant-finance/4.2-backtesting' },
            { text: '4.3 绩效评估指标', link: '/quant-finance/4.3-performance-metrics' },
          ],
        },
        {
          text: '05 市场微观结构',
          collapsed: true,
          items: [
            { text: '5.0 概述', link: '/quant-finance/05.0-overview' },
            { text: '5.0 市场微观结构', link: '/quant-finance/5.0-market-microstructure' },
            { text: '5.1 订单簿分析', link: '/quant-finance/5.1-order-book-analysis' },
            { text: '5.2 执行算法', link: '/quant-finance/5.2-execution-algorithms' },
          ],
        },
      ],
      '/prerequisite-math/': [
        {
          text: '前置数学知识',
          items: [
            { text: '概述', link: '/prerequisite-math/' },
          ],
        },
        {
          text: '01 高等数学',
          collapsed: true,
          items: [
            { text: '1.0 概述', link: '/prerequisite-math/01-calculus/01.0-overview' },
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
            { text: '2.0 概述', link: '/prerequisite-math/02-linear-algebra/02.0-overview' },
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
            { text: '3.0 概述', link: '/prerequisite-math/03-probability/03.0-overview' },
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
            { text: '4.0 概述', link: '/prerequisite-math/04-statistics/04.0-overview' },
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
            { text: '5.0 概述', link: '/prerequisite-math/05-optimization/05.0-overview' },
            { text: '5.1 梯度下降与凸优化', link: '/prerequisite-math/05-optimization/5.1-gradient-descent' },
            { text: '5.2 拉格朗日乘数法与KKT条件', link: '/prerequisite-math/05-optimization/5.2-lagrange-multiplier' },
            { text: '5.3 牛顿法', link: '/prerequisite-math/05-optimization/5.3-newton-method' },
            { text: '5.4 组合优化与风险预算', link: '/prerequisite-math/05-optimization/5.4-portfolio-optimization' },
            { text: '5.5 Python实践', link: '/prerequisite-math/05-optimization/5.5-python-practice' },
          ],
        },
        {
          text: '06 随机过程',
          collapsed: true,
          items: [
            { text: '6.0 概述', link: '/prerequisite-math/06-stochastic-processes/06.0-overview' },
            { text: '6.1 随机过程基本概念', link: '/prerequisite-math/06-stochastic-processes/6.1-basics' },
            { text: '6.2 随机游走', link: '/prerequisite-math/06-stochastic-processes/6.2-random-walk' },
            { text: '6.3 布朗运动', link: '/prerequisite-math/06-stochastic-processes/6.3-brownian-motion' },
            { text: '6.4 鞅', link: '/prerequisite-math/06-stochastic-processes/6.4-martingale' },
          ],
        },
        {
          text: '07 信息论',
          collapsed: true,
          items: [
            { text: '7.0 概述', link: '/prerequisite-math/07-information-theory/07.0-overview' },
            { text: '7.1 熵', link: '/prerequisite-math/07-information-theory/7.1-entropy' },
            { text: '7.2 KL散度与交叉熵', link: '/prerequisite-math/07-information-theory/7.2-kld-cross-entropy' },
            { text: '7.3 互信息', link: '/prerequisite-math/07-information-theory/7.3-mutual-information' },
            { text: '7.4 最大熵原理与量化应用', link: '/prerequisite-math/07-information-theory/7.4-maximum-entropy' },
          ],
        },
        {
          text: '08 傅里叶分析',
          collapsed: true,
          items: [
            { text: '8.0 概述', link: '/prerequisite-math/08-fourier-analysis/08.0-overview' },
            { text: '8.1 傅里叶级数', link: '/prerequisite-math/08-fourier-analysis/8.1-fourier-series' },
            { text: '8.2 傅里叶变换', link: '/prerequisite-math/08-fourier-analysis/8.2-fourier-transform' },
            { text: '8.3 频谱分析', link: '/prerequisite-math/08-fourier-analysis/8.3-spectral-analysis' },
            { text: '8.4 量化金融应用', link: '/prerequisite-math/08-fourier-analysis/8.4-quant-applications' },
          ],
        },
        {
          text: '09 数值计算',
          collapsed: true,
          items: [
            { text: '9.0 概述', link: '/prerequisite-math/09-numerical-computing/09.0-overview' },
            { text: '9.1 浮点精度', link: '/prerequisite-math/09-numerical-computing/9.1-floating-point' },
            { text: '9.2 根求解', link: '/prerequisite-math/09-numerical-computing/9.2-root-finding' },
            { text: '9.3 数值积分', link: '/prerequisite-math/09-numerical-computing/9.3-numerical-integration' },
            { text: '9.4 数值Greeks', link: '/prerequisite-math/09-numerical-computing/9.4-numerical-greeks' },
          ],
        },
        {
          text: '10 图论基础',
          collapsed: true,
          items: [
            { text: '10.0 概述', link: '/prerequisite-math/10-graph-theory/10.0-overview' },
            { text: '10.1 图的基本概念', link: '/prerequisite-math/10-graph-theory/10.1-graph-basics' },
            { text: '10.2 最短路径', link: '/prerequisite-math/10-graph-theory/10.2-shortest-path' },
            { text: '10.3 最小生成树', link: '/prerequisite-math/10-graph-theory/10.3-minimum-spanning-tree' },
            { text: '10.4 网络中心性', link: '/prerequisite-math/10-graph-theory/10.4-network-centrality' },
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
