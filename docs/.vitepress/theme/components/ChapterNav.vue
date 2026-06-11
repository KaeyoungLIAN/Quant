<template>
  <div class="chapter-nav">
    <div class="nav-row">
      <a v-if="prev" :href="prev.link" class="nav-link prev">
        <span class="nav-arrow">←</span>
        <span class="nav-text">
          <span class="nav-label">上一节</span>
          <span class="nav-title">{{ prev.text }}</span>
        </span>
      </a>
      <div v-else class="nav-link prev disabled">
        <span class="nav-arrow">←</span>
        <span class="nav-text">
          <span class="nav-label">已经是第一节</span>
        </span>
      </div>

      <a v-if="next" :href="next.link" class="nav-link next">
        <span class="nav-text">
          <span class="nav-label">下一节</span>
          <span class="nav-title">{{ next.text }}</span>
        </span>
        <span class="nav-arrow">→</span>
      </a>
      <div v-else class="nav-link next disabled">
        <span class="nav-text">
          <span class="nav-label">已经是最后一节</span>
        </span>
        <span class="nav-arrow">→</span>
      </div>
    </div>
    <div class="back-to-chapter">
      <a :href="chapterLink" class="back-link">↑ 返回 {{ chapterTitle }} 概览</a>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useData } from 'vitepress'

const { page } = useData()

// Full ordered list of all learning sections
const ALL_SECTIONS = [
  // Chapter 1
  { text: '1.1 安装配置', link: '/learn/01-getting-started/01-setup' },
  { text: '1.2 第一次获取数据', link: '/learn/01-getting-started/02-first-data' },
  { text: '1.3 画第一张K线图', link: '/learn/01-getting-started/03-first-chart' },
  { text: '1.4 设定学习目标', link: '/learn/01-getting-started/04-set-goal' },
  // Chapter 2
  { text: '2.1 交易品种', link: '/learn/02-finance-basics/01-instruments' },
  { text: '2.2 市场机制', link: '/learn/02-finance-basics/02-market-mechanism' },
  { text: '2.3 时间价值', link: '/learn/02-finance-basics/03-time-value' },
  { text: '2.4 风险入门', link: '/learn/02-finance-basics/04-risk-intro' },
  // Chapter 3
  { text: '3.0 MIT路线图', link: '/learn/03-math-toolbox/00-overview' },
  { text: '3.1 线性代数', link: '/learn/03-math-toolbox/01-linear-algebra' },
  { text: '3.2 概率与蒙特卡洛', link: '/learn/03-math-toolbox/02-probability' },
  { text: '3.3 矩阵分解', link: '/learn/03-math-toolbox/03-matrix-decomposition' },
  { text: '3.4 随机过程', link: '/learn/03-math-toolbox/04-stochastic-processes' },
  { text: '3.5 回归分析', link: '/learn/03-math-toolbox/05-regression' },
  { text: '3.6 VaR与商品', link: '/learn/03-math-toolbox/06-var-commodity' },
  { text: '3.7 时间序列', link: '/learn/03-math-toolbox/07-time-series' },
  { text: '3.8 波动率建模', link: '/learn/03-math-toolbox/08-volatility' },
  { text: '3.9 正则化模型', link: '/learn/03-math-toolbox/09-regularization' },
  { text: '3.10 组合理论', link: '/learn/03-math-toolbox/10-portfolio-theory' },
  // Chapter 4
  { text: '4.1 NumPy/Pandas', link: '/learn/04-python-quant/01-numpy-pandas' },
  { text: '4.2 数据获取与清洗', link: '/learn/04-python-quant/02-data-wrangling' },
  { text: '4.3 可视化', link: '/learn/04-python-quant/03-visualization' },
  { text: '4.4 回测骨架', link: '/learn/04-python-quant/04-backtest-framework' },
  // Chapter 5
  { text: '5.1 趋势跟踪', link: '/learn/05-classic-strategies/01-trend-following' },
  { text: '5.2 均值回归', link: '/learn/05-classic-strategies/02-mean-reversion' },
  { text: '5.3 统计套利', link: '/learn/05-classic-strategies/03-stat-arb' },
  { text: '5.4 风险管理', link: '/learn/05-classic-strategies/04-risk-management' },
  // Chapter 6
  { text: '6.1 特征工程', link: '/learn/06-ml-strategies/01-feature-engineering' },
  { text: '6.2 XGBoost', link: '/learn/06-ml-strategies/02-xgboost' },
  { text: '6.3 LSTM', link: '/learn/06-ml-strategies/03-lstm' },
  { text: '6.4 过拟合与诊断', link: '/learn/06-ml-strategies/04-overfitting' },
  // Chapter 7
  { text: '7.1 数据源与API', link: '/learn/07-live/01-data-sources' },
  { text: '7.2 资金管理', link: '/learn/07-live/02-capital-mgmt' },
  { text: '7.3 毕业设计', link: '/learn/07-live/03-graduation' },
]

const CHAPTER_INFO = {
  '01-getting-started': { title: '第一章：出发', link: '/learn/01-getting-started/' },
  '02-finance-basics': { title: '第二章：金融扫盲', link: '/learn/02-finance-basics/' },
  '03-math-toolbox': { title: '第三章：数学工具箱', link: '/learn/03-math-toolbox/' },
  '04-python-quant': { title: '第四章：量化编程', link: '/learn/04-python-quant/' },
  '05-classic-strategies': { title: '第五章：经典策略', link: '/learn/05-classic-strategies/' },
  '06-ml-strategies': { title: '第六章：ML因子', link: '/learn/06-ml-strategies/' },
  '07-live': { title: '第七章：实战', link: '/learn/07-live/' },
}

const currentPath = computed(() => page.value.relativePath.replace(/\.md$/, ''))

const currentIndex = computed(() => {
  return ALL_SECTIONS.findIndex(s => {
    const sPath = s.link.replace(/^\//, '').replace(/\/$/, '')
    return currentPath.value === sPath
  })
})

const prev = computed(() => {
  const i = currentIndex.value
  if (i <= 0) return null
  return ALL_SECTIONS[i - 1]
})

const next = computed(() => {
  const i = currentIndex.value
  if (i < 0 || i >= ALL_SECTIONS.length - 1) return null
  return ALL_SECTIONS[i + 1]
})

const chapterSlug = computed(() => {
  const parts = currentPath.value.split('/')
  return parts.length >= 2 ? parts[1] : ''
})

const chapterInfo = computed(() => CHAPTER_INFO[chapterSlug.value] || null)

const chapterLink = computed(() => chapterInfo.value?.link || '/learn/')
const chapterTitle = computed(() => chapterInfo.value?.title || '学习路线')
</script>

<style scoped>
.chapter-nav {
  margin-top: 48px;
  padding-top: 24px;
  border-top: 1px solid var(--vp-c-divider);
}
.nav-row {
  display: flex;
  gap: 16px;
}
.nav-link {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  text-decoration: none;
  transition: border-color 0.2s, background 0.2s;
}
.nav-link:hover {
  border-color: var(--vp-c-brand-1);
  background: var(--vp-c-bg-soft);
}
.nav-link.disabled {
  opacity: 0.4;
  cursor: not-allowed;
  pointer-events: none;
}
.nav-link.next {
  text-align: right;
  justify-content: flex-end;
}
.nav-arrow {
  font-size: 18px;
  flex-shrink: 0;
  color: var(--vp-c-brand-1);
}
.nav-link.disabled .nav-arrow {
  color: var(--vp-c-text-3);
}
.nav-label {
  display: block;
  font-size: 12px;
  color: var(--vp-c-text-3);
  margin-bottom: 2px;
}
.nav-title {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--vp-c-text-1);
}
.back-to-chapter {
  text-align: center;
  margin-top: 16px;
}
.back-link {
  font-size: 13px;
  color: var(--vp-c-text-3);
  text-decoration: none;
  transition: color 0.2s;
}
.back-link:hover {
  color: var(--vp-c-brand-1);
}
</style>
