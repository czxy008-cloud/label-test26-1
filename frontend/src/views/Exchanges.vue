<template>
  <div class="exchanges-page">
    <h2>置换进度</h2>
    <el-tabs v-model="activeTab" @tab-change="onTabChange">
      <el-tab-pane label="我收到的请求" name="received">
        <el-table :data="receivedList" v-loading="loading" style="width:100%">
          <el-table-column prop="item.title" label="我的物品" min-width="200">
            <template #default="{ row }">
              <span @click="$router.push(`/item/${row.item_id}`)" style="cursor:pointer;color:#409EFF">
                {{ row.item?.title }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="请求者" width="140">
            <template #default="{ row }">
              <el-avatar :size="24" :src="row.requester?.avatar_url">
                {{ (row.requester?.nickname || 'U')[0] }}
              </el-avatar>
              <span style="margin-left:6px">{{ row.requester?.nickname || row.requester?.username }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="message" label="留言" min-width="200" show-overflow-tooltip />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="时间" width="170">
            <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <template v-if="row.status === 0">
                <el-button size="small" type="success" @click="act(row, 'accept')">接受</el-button>
                <el-button size="small" type="danger" @click="act(row, 'reject')">拒绝</el-button>
              </template>
              <template v-else-if="row.status === 3">
                <el-button size="small" type="primary" @click="act(row, 'complete')">完成</el-button>
              </template>
              <el-button size="small" @click="$router.push(`/messages/${row.requester_id}`)">私信</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!loading && receivedList.length === 0" description="暂无请求" />
      </el-tab-pane>

      <el-tab-pane label="我发出的请求" name="sent">
        <el-table :data="sentList" v-loading="loading" style="width:100%">
          <el-table-column prop="item.title" label="目标物品" min-width="200">
            <template #default="{ row }">
              <span @click="$router.push(`/item/${row.item_id}`)" style="cursor:pointer;color:#409EFF">
                {{ row.item?.title }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="message" label="留言" min-width="200" show-overflow-tooltip />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="时间" width="170">
            <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <template v-if="row.status === 0 || row.status === 3">
                <el-button size="small" type="warning" @click="act(row, 'cancel')">取消</el-button>
              </template>
              <template v-if="row.status === 3">
                <el-button size="small" type="primary" @click="act(row, 'complete')">完成</el-button>
              </template>
              <el-button size="small" @click="$router.push(`/messages/${row.item?.owner_id}`)">私信</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!loading && sentList.length === 0" description="暂无请求" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const activeTab = ref('received')
const receivedList = ref([])
const sentList = ref([])
const loading = ref(false)

function statusType(s) {
  return { 0: 'warning', 1: 'success', 2: 'danger', 3: 'primary', 4: 'info', 5: 'info' }[s] || 'info'
}
function statusText(s) {
  return { 0: '待确认', 1: '已接受', 2: '已拒绝', 3: '进行中', 4: '已完成', 5: '已取消' }[s] || '未知'
}
function formatTime(t) { return t ? new Date(t).toLocaleString('zh-CN') : '' }

async function loadReceived() {
  loading.value = true
  try {
    const res = await request.get('/exchanges/received')
    receivedList.value = res.data || []
  } catch (_) {} finally {
    loading.value = false
  }
}

async function loadSent() {
  try {
    const res = await request.get('/exchanges/sent')
    sentList.value = res.data || []
  } catch (_) {}
}

function onTabChange(tab) {
  if (tab === 'received') loadReceived()
  else loadSent()
}

async function act(row, action) {
  const label = { accept: '接受', reject: '拒绝', complete: '完成', cancel: '取消' }[action]
  try {
    await ElMessageBox.confirm(`确定${label}该请求吗？`, '提示', { type: 'warning' })
    await request.post(`/exchanges/${row.id}/${action}`)
    ElMessage.success('操作成功')
    if (activeTab.value === 'received') loadReceived()
    else loadSent()
  } catch (_) {}
}

onMounted(loadReceived)
</script>

<style scoped>
.exchanges-page h2 { margin: 0 0 16px; }
</style>
