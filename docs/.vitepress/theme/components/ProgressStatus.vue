<template>
  <div class="progress-status" v-if="loaded">
    <div v-for="ch in chapters" :key="ch.key" class="ch-status">
      <div class="ch-row" @click="ch.expanded = !ch.expanded">
        <span class="icon">{{ ch.icon }}</span>
        <span class="label" :class="ch.status">{{ ch.label }}</span>
        <span class="section-count">{{ ch.done }}/{{ ch.total }}</span>
      </div>
      <div v-if="ch.expanded" class="section-dots">
        <span
          v-for="s in ch.sections"
          :key="s.key"
          class="dot"
          :class="{ completed: s.status === 'completed', active: s.status === 'in_progress', locked: s.status === 'locked' }"
          :title="s.title"
        ></span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const API_BASE = import.meta.env.PROD ? '' : 'http://localhost:8000'

const CHAPTER_MAP = {
  '1': { label: '第一章：出发', slug: '01-getting-started' },
  '2': { label: '第二章：金融扫盲', slug: '02-finance-basics' },
  '3': { label: '第三章：数学工具箱', slug: '03-math-toolbox' },
  '4': { label: '第四章：量化编程', slug: '04-python-quant' },
  '5': { label: '第五章：经典策略', slug: '05-classic-strategies' },
  '6': { label: '第六章：ML 因子', slug: '06-ml-strategies' },
  '7': { label: '第七章：实战', slug: '07-live' },
}

const SECTION_TITLES = {
  '1.1': '安装配置', '1.2': '第一次获取数据', '1.3': '画第一张K线图', '1.4': '设定学习目标',
  '2.1': '交易品种', '2.2': '市场机制', '2.3': '时间价值', '2.4': '风险入门',
  '3.1': '线性代数', '3.2': '概率与蒙特卡洛', '3.3': '矩阵分解', '3.4': '随机过程',
  '3.5': '回归分析', '3.6': 'VaR与商品', '3.7': '时间序列', '3.8': '波动率建模',
  '3.9': '正则化模型', '3.10': '组合理论',
  '4.1': 'NumPy/Pandas', '4.2': '数据获取与清洗', '4.3': '可视化', '4.4': '回测骨架',
  '5.1': '趋势跟踪', '5.2': '均值回归', '5.3': '统计套利', '5.4': '风险管理',
  '6.1': '特征工程', '6.2': 'XGBoost', '6.3': 'LSTM', '6.4': '过拟合与诊断',
  '7.1': '数据源与API', '7.2': '资金管理', '7.3': '毕业设计',
}

const loaded = ref(false)
const chapters = ref([])

onMounted(async () => {
  try {
    const resp = await fetch(`${API_BASE}/api/v1/progress`)
    const data = await resp.json()
    if (data.chapters) {
      const chData = {}
      for (const c of data.chapters) {
        const ch = c.chapter_key.split('.')[0]
        if (!chData[ch]) {
          chData[ch] = { sections: [], done: 0, total: 0 }
        }
        chData[ch].sections.push({ key: c.chapter_key, status: c.status, title: SECTION_TITLES[c.chapter_key] || c.chapter_key })
        chData[ch].total++
        if (c.status === 'completed') chData[ch].done++
      }

      const result = []
      for (let i = 1; i <= 7; i++) {
        const s = chData[String(i)]
        const info = CHAPTER_MAP[String(i)]
        if (!s || !info) continue
        let status = 'locked'
        if (s.done === s.total) {
          status = 'completed'
        } else if (s.done > 0 || s.sections.some(x => x.status === 'in_progress')) {
          status = 'in_progress'
        }
        result.push({
          key: String(i),
          label: info.label,
          slug: info.slug,
          icon: status === 'completed' ? '✅' : status === 'in_progress' ? '📖' : '🔒',
          status,
          done: s.done,
          total: s.total,
          sections: s.sections,
          expanded: false,
        })
      }
      chapters.value = result
    }
  } catch (e) {
    console.warn('Failed to load chapter status:', e)
  }
  loaded.value = true
})
</script>

<style scoped>
.progress-status {
  padding: 8px 12px;
  font-size: 13px;
}
.ch-status {
  padding: 2px 0;
}
.ch-row {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s;
}
.ch-row:hover {
  background: var(--vp-c-bg-soft);
}
.ch-status .icon {
  width: 20px;
  text-align: center;
  flex-shrink: 0;
}
.ch-status .label {
  flex: 1;
  font-weight: 500;
  color: var(--vp-c-text-1);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.ch-status .label.locked {
  color: var(--vp-c-text-3);
}
.ch-status .label.in_progress {
  color: var(--vp-c-brand-1);
}
.ch-status .label.completed {
  color: var(--vp-c-text-1);
}
.section-count {
  font-size: 11px;
  color: var(--vp-c-text-3);
  flex-shrink: 0;
}
.section-dots {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  padding: 4px 8px 4px 28px;
}
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--vp-c-text-3);
  opacity: 0.3;
  flex-shrink: 0;
}
.dot.completed {
  background: var(--vp-c-brand-1);
  opacity: 1;
}
.dot.active {
  background: var(--vp-c-brand-2);
  opacity: 1;
  box-shadow: 0 0 4px var(--vp-c-brand-1);
}
.dot.locked {
  background: var(--vp-c-text-3);
  opacity: 0.2;
}
</style>
