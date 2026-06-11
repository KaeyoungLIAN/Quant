<template>
  <div class="progress-status" v-if="loaded">
    <div v-for="ch in chapters" :key="ch.key" class="ch-status">
      <span class="icon">{{ ch.icon }}</span>
      <span class="label" :class="ch.status">{{ ch.label }}</span>
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

const loaded = ref(false)
const chapters = ref([])

onMounted(async () => {
  try {
    const resp = await fetch(`${API_BASE}/api/v1/progress`)
    const data = await resp.json()
    if (data.chapters) {
      // Group by chapter number and determine overall chapter status
      const chStatus = {}
      const chSlugs = {}
      for (const c of data.chapters) {
        const ch = c.chapter_key.split('.')[0]
        if (!chStatus[ch]) {
          chStatus[ch] = { completed: 0, total: 0, status: 'locked' }
          chSlugs[ch] = CHAPTER_MAP[ch]?.slug || ''
        }
        chStatus[ch].total++
        if (c.status === 'completed') chStatus[ch].completed++
      }

      // Compute overall status: locked if all locked, completed if all completed, else in_progress
      const result = []
      for (let i = 1; i <= 7; i++) {
        const s = chStatus[String(i)]
        const info = CHAPTER_MAP[String(i)]
        if (!s || !info) continue
        let status = 'locked'
        if (s.completed === s.total) {
          status = 'completed'
        } else if (s.completed > 0 || s.status === 'in_progress') {
          status = 'in_progress'
        }
        result.push({
          key: String(i),
          label: info.label,
          slug: info.slug,
          icon: status === 'completed' ? '✅' : status === 'in_progress' ? '⬜' : '🔒',
          status,
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
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 0;
}
.ch-status .icon {
  width: 20px;
  text-align: center;
}
.ch-status .label {
  color: var(--vp-c-text-1);
  font-weight: 500;
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
</style>
