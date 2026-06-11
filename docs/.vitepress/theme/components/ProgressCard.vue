<template>
  <div class="progress-card" v-if="loaded">
    <div class="progress-hero">
      <div class="greeting">{{ greeting }}</div>
      <div class="progress-text">当前进度：第 {{ current.chapter_key }} 节</div>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: pct + '%' }"></div>
      </div>
      <div class="progress-label">{{ completedCount }}/{{ totalCount }} 节完成 ({{ pct }}%)</div>
      <a :href="currentLink" class="continue-btn">
        ▶ 继续学习
      </a>
    </div>
  </div>
  <div class="progress-card loading" v-else>
    <div class="progress-hero">
      <div class="greeting">欢迎来到 Quant Learning</div>
      <div class="progress-text">加载进度中...</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const CHAPTER_SLUGS = {
  '1': '01-getting-started',
  '2': '02-finance-basics',
  '3': '03-math-toolbox',
  '4': '04-python-quant',
  '5': '05-classic-strategies',
  '6': '06-ml-strategies',
  '7': '07-live',
}

const SECTION_SLUGS = {
  '1.1': '01-setup', '1.2': '02-first-data', '1.3': '03-first-chart', '1.4': '04-set-goal',
  '2.1': '01-instruments', '2.2': '02-market-mechanism', '2.3': '03-time-value', '2.4': '04-risk-intro',
  '3.1': '01-linear-algebra', '3.2': '02-probability', '3.3': '03-matrix-decomposition', '3.4': '04-stochastic-processes',
  '3.5': '05-regression', '3.6': '06-var-commodity', '3.7': '07-time-series', '3.8': '08-volatility',
  '3.9': '09-regularization', '3.10': '10-portfolio-theory',
  '4.1': '01-numpy-pandas', '4.2': '02-data-wrangling', '4.3': '03-visualization', '4.4': '04-backtest-framework',
  '5.1': '01-trend-following', '5.2': '02-mean-reversion', '5.3': '03-stat-arb', '5.4': '04-risk-management',
  '6.1': '01-feature-engineering', '6.2': '02-xgboost', '6.3': '03-lstm', '6.4': '04-overfitting',
  '7.1': '01-data-sources', '7.2': '02-capital-mgmt', '7.3': '03-graduation',
}

const API_BASE = import.meta.env.PROD ? '' : 'http://localhost:8000'
const loaded = ref(false)
const current = ref({ chapter_key: '1.1' })
const completedCount = ref(0)
const totalCount = ref(33)

function chapterSlug(key) {
  const ch = key.split('.')[0]
  return CHAPTER_SLUGS[ch] || ''
}

function sectionSlug(key) {
  return SECTION_SLUGS[key] || ''
}

const currentLink = computed(() => {
  const ch = current.value.chapter_key.split('.')[0]
  return '/learn/' + String(ch).padStart(2, '0') + '-' + chapterSlug(current.value.chapter_key) + '/' + sectionSlug(current.value.chapter_key)
})

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '🌙 这么晚还在学？'
  if (hour < 12) return '🌅 早上好，继续学习！'
  if (hour < 14) return '☀️ 下午开始学习'
  if (hour < 18) return '🌤️ 下午好'
  return '🌆 晚上好'
})

const pct = computed(() => {
  if (totalCount.value === 0) return 0
  return Math.round((completedCount.value / totalCount.value) * 100)
})

onMounted(async () => {
  try {
    const resp = await fetch(`${API_BASE}/api/v1/progress`)
    const data = await resp.json()
    if (data.chapters) {
      completedCount.value = data.chapters.filter(c => c.status === 'completed').length
      totalCount.value = data.chapters.length
      const active = data.chapters.find(c => c.status === 'in_progress')
      if (active) current.value = active
      if (data.last_visited) current.value = data.chapters.find(c => c.chapter_key === data.last_visited) || current.value
    }
  } catch (e) {
    console.warn('Failed to load progress:', e)
  }
  loaded.value = true
})
</script>

<style scoped>
.progress-card {
  max-width: 640px;
  margin: 0 auto 32px;
}

.progress-hero {
  background: linear-gradient(135deg, var(--vp-c-brand-1), var(--vp-c-brand-2));
  border-radius: 16px;
  padding: 32px 40px;
  color: white;
  text-align: center;
}

.greeting {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 8px;
}

.progress-text {
  font-size: 1.1rem;
  opacity: 0.95;
  margin-bottom: 20px;
}

.progress-bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.25);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: white;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.progress-label {
  font-size: 0.85rem;
  opacity: 0.85;
  margin-bottom: 20px;
}

.continue-btn {
  display: inline-block;
  background: white;
  color: var(--vp-c-brand-1);
  padding: 12px 32px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1.05rem;
  text-decoration: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.continue-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.loading {
  opacity: 0.6;
}
</style>
