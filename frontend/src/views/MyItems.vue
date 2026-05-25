<template>
  <div class="my-items-page">
    <div class="page-header">
      <h2>我的物品</h2>
      <el-button type="primary" @click="$router.push('/publish')">
        <el-icon><Plus /></el-icon> 发布新物品
      </el-button>
    </div>

    <el-table :data="items" v-loading="loading" style="width: 100%">
      <el-table-column prop="title" label="物品" min-width="220">
        <template #default="{ row }">
          <div class="cell-item" @click="$router.push(`/item/${row.id}`)" style="cursor:pointer">
            <el-image :src="row.images?.[0]" fit="cover" style="width:48px;height:48px;border-radius:4px" />
            <span class="item-title">{{ row.title }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="view_count" label="浏览" width="80" />
      <el-table-column prop="created_at" label="发布时间" width="180">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="onOffShelf(row)" v-if="row.status === 1">下架</el-button>
          <el-button size="small" @click="onOffShelf(row)" v-if="row.status === 4">重新上架</el-button>
          <el-button size="small" type="danger" @click="onDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-empty v-if="!loading && items.length === 0" description="还没有发布任何物品" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const items = ref([])
const loading = ref(false)

function statusType(s) { return { 1: 'success', 2: 'warning', 3: 'info', 4: 'info' }[s] || 'info' }
function statusText(s) { return { 1: '可置换', 2: '置换中', 3: '已完成', 4: '已下架' }[s] || '未知' }
function formatTime(t) { return t ? new Date(t).toLocaleString('zh-CN') : '' }

async function loadItems() {
  loading.value = true
  try {
    const res = await request.get('/items/mine')
    items.value = res.data || []
  } catch (_) {} finally {
    loading.value = false
  }
}

async function onOffShelf(row) {
  const newStatus = row.status === 1 ? 4 : 1
  try {
    await request.put(`/items/${row.id}`, { status: newStatus })
    ElMessage.success('操作成功')
    loadItems()
  } catch (_) {}
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除「${row.title}」吗？`, '提示', { type: 'warning' })
    await request.delete(`/items/${row.id}`)
    ElMessage.success('已删除')
    loadItems()
  } catch (_) {}
}

onMounted(loadItems)
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-header h2 { margin: 0; }
.cell-item { display: flex; align-items: center; gap: 10px; }
.item-title { font-size: 14px; }
</style>
