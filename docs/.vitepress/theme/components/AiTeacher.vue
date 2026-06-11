<template>
  <div class="ai-teacher">
    <!-- Bubble -->
    <button v-if="!open" class="bubble" @click="openPanel">
      <span class="bubble-icon">🤖</span>
    </button>

    <!-- Panel -->
    <div v-else class="panel">
      <!-- Header -->
      <div class="panel-header">
        <span>🧠 Quant Learning</span>
        <button class="close-btn" @click="open = false">✕</button>
      </div>

      <!-- Tab: Chat / Progress -->
      <div class="tabs">
        <button :class="['tab', { active: tab === 'chat' }]" @click="tab = 'chat'">💬 问答</button>
        <button :class="['tab', { active: tab === 'lesson' }]" @click="tab = 'lesson'">📘 课程</button>
        <button :class="['tab', { active: tab === 'progress' }]" @click="tab = 'progress'">📊 进度</button>
      </div>

      <!-- Progress Tab -->
      <div v-if="tab === 'progress'" class="tab-content">
        <div v-if="loading" class="loading">加载中...</div>
        <div v-else-if="statusError" class="error">{{ statusError }}</div>
        <div v-else-if="status">
          <p class="summary">{{ status.summary }}</p>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: status.overall_progress + '%' }"></div>
          </div>
          <p class="progress-label">总进度 {{ status.overall_progress }}%</p>
          <div class="module-list">
            <div v-for="m in status.modules" :key="m.module_key" class="module-item">
              <span class="module-name">{{ moduleName(m.module_key) }}</span>
              <span :class="['module-status', m.status]">
                {{ statusLabel(m.status) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Lesson Tab -->
      <div v-if="tab === 'lesson'" class="tab-content lesson-content">
        <div v-if="lessonLoading" class="loading">AI 正在为你生成课程...</div>
        <div v-else-if="lessonError" class="error">{{ lessonError }}</div>
        <div v-else-if="currentLesson">
          <h3>{{ currentLesson.title }}</h3>
          <div v-html="currentLesson.html_content" class="lesson-body"></div>
          <div v-if="currentLesson.checkpoint" class="checkpoint">
            <h4>✅ 掌握检查</h4>
            <p>{{ currentLesson.checkpoint }}</p>
            <div class="checkpoint-actions">
              <button class="btn btn-pass" @click="passCheckpoint">我掌握了</button>
              <button class="btn btn-fail" @click="failCheckpoint">还没掌握</button>
            </div>
          </div>
        </div>
        <div v-else>
          <button class="btn btn-primary" @click="requestLesson" :disabled="lessonLoading">
            🎯 给我一节课
          </button>
        </div>
      </div>

      <!-- Chat Tab -->
      <div v-if="tab === 'chat'" class="tab-content chat-content">
        <div ref="chatBox" class="chat-box">
          <div v-for="(msg, i) in chatHistory" :key="i" :class="['msg', msg.role]">
            <div class="msg-bubble">{{ msg.message }}</div>
          </div>
          <div v-if="chatLoading" class="loading">思考中...</div>
        </div>
        <div class="chat-input">
          <input
            v-model="chatInput"
            placeholder="问任何量化问题..."
            @keyup.enter="sendChat"
            :disabled="chatLoading"
          />
          <button @click="sendChat" :disabled="chatLoading || !chatInput.trim()">发送</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'

const API_BASE = ''

// State
const open = ref(false)
const tab = ref('chat')
const loading = ref(false)
const status = ref(null)
const statusError = ref('')
const chatInput = ref('')
const chatHistory = ref([])
const chatLoading = ref(false)
const currentLesson = ref(null)
const lessonLoading = ref(false)
const lessonError = ref('')

const token = ref('')
const username = ref('')
const userId = ref(0)

// Load saved auth state on mount (client-side only)
function loadAuth() {
  if (typeof localStorage !== 'undefined') {
    token.value = localStorage.getItem('quant_teacher_token') || ''
    username.value = localStorage.getItem('quant_teacher_username') || ''
    userId.value = Number(localStorage.getItem('quant_teacher_user_id') || 0)
  }
}
loadAuth()

// Helpers
const moduleName = (key) => {
  const names = {
    '01-calculus': '高等数学', '02-linear-algebra': '线性代数',
    '03-probability': '概率论', '04-statistics': '数理统计',
    'finance-basics': '金融入门',
    '05-stochastic-processes': '随机过程',
    '06-trend-following': '趋势跟踪', '07-mean-reversion': '均值回归',
    '08-backtesting': '回测框架', '09-risk-metrics': '风险指标',
    '10-execution': '执行算法',
    '11-paper-reproduction': '论文复现', '12-own-strategy': '自主策略',
    '13-live-trading': '实盘交易',
  }
  return names[key] || key
}
const statusLabel = (s) => ({ not_started: '未开始', in_progress: '学习中', completed: '已完成' })[s] || s

// API calls
async function api(method, path, body = null) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  }
  if (token.value) opts.headers['Authorization'] = `Bearer ${token.value}`
  if (body) opts.body = JSON.stringify(body)
  const res = await fetch(`${API_BASE}${path}`, opts)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  return res.json()
}

async function loadStatus() {
  if (!token.value) return
  loading.value = true
  statusError.value = ''
  try {
    status.value = await api('GET', '/api/teacher/status')
  } catch (e) {
    statusError.value = e.message
  } finally {
    loading.value = false
  }
}

async function requestLesson() {
  lessonLoading.value = true
  lessonError.value = ''
  currentLesson.value = null
  try {
    currentLesson.value = await api('POST', '/api/teacher/lesson')
  } catch (e) {
    lessonError.value = e.message
  } finally {
    lessonLoading.value = false
  }
}

async function passCheckpoint() {
  if (!currentLesson.value) return
  await api('POST', '/api/teacher/checkpoint', {
    lesson_id: currentLesson.value.lesson_id,
    passed: true,
    notes: '',
  })
  currentLesson.value = null
  await loadStatus()
  tab.value = 'progress'
}

async function failCheckpoint() {
  if (!currentLesson.value) return
  await api('POST', '/api/teacher/checkpoint', {
    lesson_id: currentLesson.value.lesson_id,
    passed: false,
    notes: '',
  })
  currentLesson.value = null
}

async function sendChat() {
  const msg = chatInput.value.trim()
  if (!msg || chatLoading.value) return
  chatInput.value = ''
  chatHistory.value.push({ role: 'user', message: msg })
  chatLoading.value = true
  try {
    const res = await api('POST', '/api/teacher/chat', { message: msg })
    chatHistory.value.push({ role: 'assistant', message: res.reply })
  } catch (e) {
    chatHistory.value.push({ role: 'assistant', message: '出错: ' + e.message })
  } finally {
    chatLoading.value = false
    await nextTick()
    const box = document.querySelector('.chat-box')
    if (box) box.scrollTop = box.scrollHeight
  }
}

async function openPanel() {
  open.value = true
  if (!token.value) {
    // Simple auto-login: create a default user
    try {
      const r = await api('POST', '/api/auth/register', {
        username: 'user',
        password: 'quant',
      })
      token.value = r.token
      username.value = r.username
      userId.value = r.user_id
      localStorage.setItem('quant_teacher_token', r.token)
      localStorage.setItem('quant_teacher_username', r.username)
      localStorage.setItem('quant_teacher_user_id', String(r.user_id))
    } catch {
      // User already exists, try login
      try {
        const r = await api('POST', '/api/auth/login', {
          username: 'user',
          password: 'quant',
        })
        token.value = r.token
        username.value = r.username
        userId.value = r.user_id
        localStorage.setItem('quant_teacher_token', r.token)
        localStorage.setItem('quant_teacher_username', r.username)
        localStorage.setItem('quant_teacher_user_id', String(r.user_id))
      } catch (e) {
        statusError.value = '无法登录: ' + e.message
        return
      }
    }
  }
  await loadStatus()
}
</script>

<style scoped>
.ai-teacher {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.bubble {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0ea5e9, #38bdf8);
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(14, 165, 233, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
}
.bubble:hover { transform: scale(1.1); }
.bubble-icon { font-size: 24px; }

.panel {
  width: 380px;
  max-height: 600px;
  background: #1a1a2e;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  color: #e0e0e0;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  background: #16213e;
  font-weight: 600;
  font-size: 15px;
}
.close-btn {
  background: none;
  border: none;
  color: #888;
  cursor: pointer;
  font-size: 18px;
}
.close-btn:hover { color: #fff; }

.tabs {
  display: flex;
  background: #16213e;
  border-bottom: 1px solid #2a2a4a;
}
.tab {
  flex: 1;
  padding: 10px;
  background: none;
  border: none;
  color: #888;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}
.tab.active { color: #38bdf8; background: rgba(56, 189, 248, 0.1); }
.tab:hover { color: #a0a0c0; }

.tab-content {
  flex: 1;
  overflow-y: auto;
  padding: 14px 18px;
}

.loading {
  text-align: center;
  color: #888;
  padding: 20px;
}

.error {
  color: #ff6b6b;
  text-align: center;
  padding: 10px;
}

.summary {
  margin-bottom: 8px;
  font-size: 14px;
}
.progress-bar {
  height: 8px;
  background: #2a2a4a;
  border-radius: 4px;
  overflow: hidden;
  margin: 4px 0;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #0ea5e9, #38bdf8);
  border-radius: 4px;
  transition: width 0.3s;
}
.progress-label {
  font-size: 12px;
  color: #888;
  margin-bottom: 12px;
}
.module-item {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  border-bottom: 1px solid #2a2a4a;
  font-size: 13px;
}
.module-name { color: #c0c0d0; }
.module-status.not_started { color: #888; }
.module-status.in_progress { color: #f0c040; }
.module-status.completed { color: #40c080; }

.lesson-body :deep(pre) {
  background: #0d0d1a;
  border-radius: 8px;
  padding: 12px;
  overflow-x: auto;
  font-size: 13px;
}
.lesson-body :deep(code) { font-size: 13px; }

.checkpoint {
  margin-top: 16px;
  padding: 12px;
  background: rgba(56, 189, 248, 0.08);
  border-radius: 8px;
}
.checkpoint-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.btn {
  padding: 8px 16px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}
.btn-primary {
  background: linear-gradient(135deg, #0ea5e9, #38bdf8);
  color: #fff;
  width: 100%;
  padding: 12px;
  margin-top: 10px;
}
.btn-pass { background: #10b981; color: #fff; }
.btn-fail { background: #6b7280; color: #fff; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }

.chat-box {
  flex: 1;
  overflow-y: auto;
  max-height: 300px;
  margin-bottom: 8px;
}
.msg { margin-bottom: 10px; }
.msg.user { text-align: right; }
.msg.assistant { text-align: left; }
.msg-bubble {
  display: inline-block;
  max-width: 85%;
  padding: 8px 12px;
  border-radius: 12px;
  font-size: 13px;
  line-height: 1.5;
  text-align: left;
}
.msg.user .msg-bubble {
  background: #0ea5e9;
  color: #fff;
  border-bottom-right-radius: 4px;
}
.msg.assistant .msg-bubble {
  background: #2a2a4a;
  color: #e0e0e0;
  border-bottom-left-radius: 4px;
}

.chat-input {
  display: flex;
  gap: 6px;
  border-top: 1px solid #2a2a4a;
  padding-top: 8px;
}
.chat-input input {
  flex: 1;
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid #2a2a4a;
  background: #0d0d1a;
  color: #e0e0e0;
  font-size: 13px;
  outline: none;
}
.chat-input input:focus { border-color: #0ea5e9; }
.chat-input button {
  padding: 8px 16px;
  border-radius: 8px;
  border: none;
  background: #0ea5e9;
  color: #fff;
  cursor: pointer;
  font-size: 13px;
}
.chat-input button:disabled { opacity: 0.5; }
</style>
