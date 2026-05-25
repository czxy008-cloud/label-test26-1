<template>
  <div class="detail-page" v-loading="loading">
    <template v-if="item">
      <el-row :gutter="24">
        <el-col :span="14">
          <el-carousel :interval="4000" arrow="always" height="460px" v-if="item.images && item.images.length">
            <el-carousel-item v-for="(img, idx) in item.images" :key="idx">
              <el-image :src="img" fit="contain" style="height:460px;width:100%" :preview-src-list="item.images" :initial-index="idx" />
            </el-carousel-item>
          </el-carousel>
          <div v-else class="no-image"><el-icon :size="80"><Picture /></el-icon><p>暂无图片</p></div>

          <el-card class="info-card" shadow="never">
            <h2>{{ item.title }}</h2>
            <div class="meta">
              <el-avatar :size="36" :src="item.owner?.avatar_url">
                {{ (item.owner?.nickname || 'U')[0] }}
              </el-avatar>
              <div class="meta-info">
                <div class="meta-name">{{ item.owner?.nickname || item.owner?.username }}</div>
                <div class="meta-time">{{ formatTime(item.created_at) }} · 浏览 {{ item.view_count }}</div>
              </div>
            </div>
            <div class="tag-row" v-if="item.tags && item.tags.length">
              <el-tag v-for="t in item.tags" :key="t" type="info">{{ t }}</el-tag>
            </div>
            <div class="desc">{{ item.description }}</div>
            <div v-if="item.expectation" class="expect-box">
              <div class="expect-label"><el-icon><RefreshRight /></el-icon> 期望置换</div>
              <div class="expect-text">{{ item.expectation }}</div>
              <div v-if="item.expected_tags && item.expected_tags.length" class="expect-tags">
                <el-tag v-for="t in item.expected_tags" :key="t" size="small" type="success">{{ t }}</el-tag>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="10">
          <el-card shadow="never" class="action-card">
            <template v-if="!isOwner && userStore.isLogin">
              <el-button type="primary" size="large" @click="dialogVisible = true" style="width:100%">
                <el-icon><RefreshRight /></el-icon> 发起置换请求
              </el-button>
              <el-button size="large" @click="goChat" style="width:100%;margin-top:12px">
                <el-icon><ChatDotRound /></el-icon> 私信 {{ item.owner?.nickname }}
              </el-button>
            </template>
            <template v-else-if="isOwner">
              <el-alert type="info" :closable="false">这是你发布的物品</el-alert>
              <el-button type="primary" style="width:100%;margin-top:12px" @click="$router.push('/my-items')">
                管理我的物品
              </el-button>
            </template>
            <template v-else>
              <el-button type="primary" size="large" @click="$router.push('/login')" style="width:100%">登录后发起置换</el-button>
            </template>
          </el-card>

          <el-card shadow="never" class="status-card" style="margin-top:16px">
            <div class="status-label">物品状态</div>
            <el-tag :type="statusType">{{ statusText }}</el-tag>
          </el-card>
        </el-col>
      </el-row>
    </template>

    <el-dialog v-model="dialogVisible" title="发起置换请求" width="520px">
      <el-form :model="reqForm" label-width="100px">
        <el-form-item label="留言">
          <el-input v-model="reqForm.message" type="textarea" :rows="3" placeholder="介绍一下你自己和你能提供的物品" />
        </el-form-item>
        <el-form-item label="提供物品">
          <el-select
            v-model="reqForm.offered_item_ids" multiple filterable
            placeholder="选择你提供用于置换的物品" style="width:100%"
          >
            <el-option v-for="it in myItems" :key="it.id" :label="it.title" :value="it.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitRequest">确认发起</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { useUserStore } from '@/store/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const item = ref(null)
const loading = ref(false)
const dialogVisible = ref(false)
const submitting = ref(false)
const myItems = ref([])
const reqForm = ref({ message: '', offered_item_ids: [] })

const isOwner = computed(() => userStore.isLogin && item.value?.owner_id === userStore.user.id)
const statusType = computed(() => ({
  1: 'success', 2: 'warning', 3: 'info', 4: 'info'
}[item.value?.status] || 'info'))
const statusText = computed(() => ({
  1: '可置换', 2: '置换中', 3: '已完成', 4: '已下架'
}[item.value?.status] || '未知'))

function formatTime(t) { return t ? new Date(t).toLocaleString('zh-CN') : '' }

async function loadItem() {
  loading.value = true
  try {
    const res = await request.get(`/items/${route.params.id}`)
    item.value = res.data
  } catch (_) {} finally {
    loading.value = false
  }
}

async function loadMyItems() {
  try {
    const res = await request.get('/items/mine')
    myItems.value = res.data || []
  } catch (_) {}
}

async function submitRequest() {
  submitting.value = true
  try {
    await request.post('/exchanges', {
      item_id: item.value.id,
      message: reqForm.value.message,
      offered_item_ids: reqForm.value.offered_item_ids
    })
    ElMessage.success('请求已发送')
    dialogVisible.value = false
    router.push('/exchanges')
  } finally {
    submitting.value = false
  }
}

function goChat() {
  router.push(`/messages/${item.value.owner_id}`)
}

onMounted(() => {
  loadItem()
  if (userStore.isLogin) loadMyItems()
})
</script>

<style scoped>
.detail-page {}
.no-image { background: #f5f7fa; height: 460px; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #c0c4cc; }
.info-card { margin-top: 16px; }
.info-card h2 { margin: 0 0 12px; }
.meta { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.meta-name { font-weight: 600; }
.meta-time { font-size: 12px; color: #909399; }
.tag-row { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px; }
.desc { font-size: 14px; line-height: 1.8; color: #303133; white-space: pre-wrap; }
.expect-box { margin-top: 16px; padding: 12px; background: #f0f9eb; border-radius: 6px; }
.expect-label { color: #67c23a; font-weight: 600; margin-bottom: 6px; display: flex; align-items: center; gap: 4px; }
.expect-text { font-size: 13px; }
.expect-tags { margin-top: 8px; display: flex; gap: 4px; flex-wrap: wrap; }
.action-card .el-button { margin-left: 0; }
.status-card .status-label { font-size: 13px; color: #909399; margin-bottom: 8px; }
</style>
