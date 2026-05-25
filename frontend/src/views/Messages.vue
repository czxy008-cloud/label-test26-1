<template>
  <div class="messages-page">
    <el-row :gutter="16">
      <el-col :span="8">
        <el-card shadow="never" class="conv-card">
          <template #header><strong>会话列表</strong></template>
          <div
            v-for="c in conversations" :key="c.other?.id"
            class="conv-item" :class="{ active: activeId === c.other?.id }"
            @click="selectConversation(c.other?.id)"
          >
            <el-avatar :size="40" :src="c.other?.avatar_url">
              {{ (c.other?.nickname || 'U')[0] }}
            </el-avatar>
            <div class="conv-info">
              <div class="conv-name">
                {{ c.other?.nickname || c.other?.username }}
                <el-badge v-if="c.unread_count > 0" :value="c.unread_count" class="conv-badge" />
              </div>
              <div class="conv-last">{{ c.last_message?.content }}</div>
            </div>
          </div>
          <el-empty v-if="conversations.length === 0" description="暂无会话" :image-size="80" />
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card shadow="never" class="chat-card" v-if="activeId">
          <template #header>
            <div class="chat-header">
              <el-avatar :size="32" :src="activeUser?.avatar_url">
                {{ (activeUser?.nickname || 'U')[0] }}
              </el-avatar>
              <strong>{{ activeUser?.nickname || activeUser?.username }}</strong>
            </div>
          </template>

          <div class="chat-body" ref="chatBodyRef">
            <div
              v-for="m in messages" :key="m.id"
              class="msg-row" :class="{ mine: m.sender_id === userStore.user?.id }"
            >
              <div class="msg-bubble">{{ m.content }}</div>
              <div class="msg-time">{{ formatTime(m.created_at) }}</div>
            </div>
            <el-empty v-if="messages.length === 0" description="开始聊天吧" :image-size="80" />
          </div>

          <div class="chat-input">
            <el-input
              v-model="inputMsg" placeholder="输入消息..."
              @keyup.enter="sendMessage"
              clearable
            >
              <template #append>
                <el-button :loading="sending" @click="sendMessage">
                  <el-icon><Promotion /></el-icon>
                </el-button>
              </template>
            </el-input>
          </div>
        </el-card>
        <el-card shadow="never" v-else class="chat-empty">
          <el-empty description="从左侧选择一个会话开始聊天" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { useUserStore } from '@/store/user'
import { on as socketOn, off as socketOff } from '@/utils/socket'

const route = useRoute()
const userStore = useUserStore()

const conversations = ref([])
const messages = ref([])
const activeId = ref(null)
const activeUser = ref(null)
const inputMsg = ref('')
const sending = ref(false)
const chatBodyRef = ref(null)
let messageCb = null

async function loadConversations() {
  try {
    const res = await request.get('/messages/conversations')
    conversations.value = res.data || []
  } catch (_) {}
}

async function loadMessages(uid) {
  try {
    const res = await request.get(`/messages/${uid}`)
    messages.value = res.data || []
    activeId.value = uid
    const found = conversations.value.find((c) => c.other?.id === uid)
    activeUser.value = found?.other || { id: uid, nickname: '', username: '用户' }
    await nextTick()
    scrollBottom()
  } catch (_) {}
}

function selectConversation(uid) {
  loadMessages(uid)
}

function scrollBottom() {
  if (chatBodyRef.value) {
    chatBodyRef.value.scrollTop = chatBodyRef.value.scrollHeight
  }
}

async function sendMessage() {
  const text = inputMsg.value.trim()
  if (!text || !activeId.value) return
  sending.value = true
  try {
    await request.post('/messages', { receiver_id: activeId.value, content: text })
    inputMsg.value = ''
    await loadMessages(activeId.value)
    loadConversations()
  } catch (_) {} finally {
    sending.value = false
  }
}

function formatTime(t) { return t ? new Date(t).toLocaleTimeString('zh-CN', { hour12: false }) : '' }

function onNewMessage(msg) {
  const myId = userStore.user?.id
  const otherId = msg.sender_id === myId ? msg.receiver_id : msg.sender_id
  if (activeId.value && otherId === activeId.value) {
    const exists = messages.value.some((m) => m.id === msg.id)
    if (!exists) {
      messages.value.push(msg)
      nextTick(scrollBottom)
    }
    if (msg.receiver_id === myId) {
      loadConversations()
    }
  } else {
    loadConversations()
  }
}

onMounted(async () => {
  await loadConversations()
  const uid = route.params.userId
  if (uid) {
    activeId.value = Number(uid)
    await loadMessages(activeId.value)
  }
  messageCb = socketOn('new_message', onNewMessage)
})

onUnmounted(() => {
  if (messageCb) {
    socketOff('new_message', messageCb)
    messageCb = null
  }
})

watch(() => route.params.userId, (uid) => {
  if (uid) {
    activeId.value = Number(uid)
    loadMessages(activeId.value)
  }
})
</script>

<style scoped>
.messages-page { }
.conv-card { min-height: 600px; }
.conv-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px; border-radius: 6px; cursor: pointer;
  transition: background 0.15s;
}
.conv-item:hover { background: #f5f7fa; }
.conv-item.active { background: #ecf5ff; }
.conv-info { flex: 1; min-width: 0; }
.conv-name { font-weight: 600; display: flex; align-items: center; gap: 6px; }
.conv-badge { margin-left: auto; }
.conv-last { font-size: 12px; color: #909399; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.chat-card { min-height: 600px; display: flex; flex-direction: column; }
.chat-header { display: flex; align-items: center; gap: 10px; }
.chat-body {
  flex: 1; height: 480px; overflow-y: auto;
  padding: 16px; background: #f5f7fa; border-radius: 6px;
  display: flex; flex-direction: column; gap: 12px;
}
.msg-row { display: flex; flex-direction: column; }
.msg-row.mine { align-items: flex-end; }
.msg-bubble {
  max-width: 70%; padding: 8px 14px; border-radius: 12px;
  background: #fff; font-size: 14px; line-height: 1.5;
  word-break: break-word;
}
.msg-row.mine .msg-bubble { background: #409EFF; color: #fff; }
.msg-time { font-size: 11px; color: #909399; margin-top: 4px; }
.chat-input { margin-top: 12px; }
.chat-empty { min-height: 600px; }
</style>
