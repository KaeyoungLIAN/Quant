<template>
  <div class="ai-teacher">
    <!-- Bubble -->
    <button v-if="!open" class="bubble" @click="openPanel">
      <span class="bubble-icon">🤖</span>
    </button>

    <!-- Panel -->
    <div v-else class="panel">
      <div class="panel-header">
        <span>🧠 Quant Learning 助教</span>
        <button class="close-btn" @click="open = false">✕</button>
      </div>

      <div class="chat-box" ref="chatBox">
        <div v-if="chatHistory.length === 0" class="welcome">
          <p>👋 有什么量化问题？</p>
          <p class="hint">问任何量化相关的概念、代码或策略问题。</p>
        </div>
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
</template>

<script setup>
import { ref, nextTick } from 'vue'

const API_BASE = import.meta.env.PROD ? '' : 'http://localhost:8000'

const open = ref(false)
const chatInput = ref('')
const chatHistory = ref([])
const chatLoading = ref(false)
const chatBox = ref(null)

async function sendChat() {
  const msg = chatInput.value.trim()
  if (!msg || chatLoading.value) return
  chatInput.value = ''
  chatHistory.value.push({ role: 'user', message: msg })
  chatLoading.value = true
  try {
    const res = await fetch(`${API_BASE}/api/v1/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg }),
    })
    const data = await res.json()
    chatHistory.value.push({ role: 'assistant', message: data.reply })
  } catch (e) {
    chatHistory.value.push({ role: 'assistant', message: '出错: ' + e.message })
  } finally {
    chatLoading.value = false
    await nextTick()
    if (chatBox.value) chatBox.value.scrollTop = chatBox.value.scrollHeight
  }
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
  max-height: 500px;
  background: var(--vp-c-bg-soft);
  border-radius: 16px;
  box-shadow: 0 8px 32px var(--vp-c-shadow, rgba(0,0,0,0.4));
  display: flex;
  flex-direction: column;
  overflow: hidden;
  color: var(--vp-c-text-1);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  background: var(--vp-c-bg-mute);
  font-weight: 600;
  font-size: 15px;
}
.close-btn {
  background: none;
  border: none;
  color: var(--vp-c-text-3);
  cursor: pointer;
  font-size: 18px;
}
.close-btn:hover { color: var(--vp-c-text-1); }

.chat-box {
  flex: 1;
  overflow-y: auto;
  max-height: 360px;
  padding: 14px 18px;
}

.welcome { text-align: center; padding: 20px 0; color: var(--vp-c-text-3); }
.welcome p { margin: 6px 0; }
.hint { font-size: 12px; }

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
  background: var(--vp-c-brand-1);
  color: #fff;
  border-bottom-right-radius: 4px;
}
.msg.assistant .msg-bubble {
  background: var(--vp-c-bg-mute);
  color: var(--vp-c-text-1);
  border-bottom-left-radius: 4px;
}

.loading {
  text-align: center;
  color: var(--vp-c-text-3);
  padding: 10px;
}

.chat-input {
  display: flex;
  gap: 6px;
  padding: 10px 14px;
  border-top: 1px solid var(--vp-c-divider);
}
.chat-input input {
  flex: 1;
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-size: 13px;
  outline: none;
}
.chat-input input:focus { border-color: var(--vp-c-brand-1); }
.chat-input button {
  padding: 8px 16px;
  border-radius: 8px;
  border: none;
  background: var(--vp-c-brand-1);
  color: #fff;
  cursor: pointer;
  font-size: 13px;
}
.chat-input button:disabled { opacity: 0.5; }
</style>
