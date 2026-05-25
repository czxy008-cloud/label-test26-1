<template>
  <div class="home-page">
    <div class="search-bar">
      <el-input
        v-model="keyword" placeholder="搜索物品关键词..." clearable
        style="max-width: 400px"
        @keyup.enter="onSearch"
        @clear="onSearch"
      >
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-button type="primary" @click="onSearch">搜索</el-button>
    </div>

    <h2 class="section-title">{{ keyword ? '搜索结果' : '为你推荐' }}</h2>

    <div v-loading="loading" class="item-grid">
      <item-card v-for="item in items" :key="item.id" :item="item" />
    </div>

    <el-empty v-if="!loading && items.length === 0" description="暂无物品" />

    <div v-if="!keyword && total > items.length" class="load-more">
      <el-button :loading="loadingMore" @click="loadMore">加载更多</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import ItemCard from '@/components/ItemCard.vue'

const items = ref([])
const total = ref(0)
const page = ref(1)
const keyword = ref('')
const loading = ref(false)
const loadingMore = ref(false)

async function fetchRecommend() {
  loading.value = true
  try {
    const res = await request.get('/items/recommend', { params: { limit: 20 } })
    items.value = res.data || []
    total.value = items.value.length
  } catch (_) {} finally {
    loading.value = false
  }
}

async function onSearch() {
  if (!keyword.value.trim()) {
    page.value = 1
    await fetchRecommend()
    return
  }
  loading.value = true
  try {
    const res = await request.get('/items', {
      params: { keyword: keyword.value.trim(), page: 1, per_page: 20 }
    })
    items.value = res.data || []
    total.value = res.total || 0
  } catch (_) {} finally {
    loading.value = false
  }
}

async function loadMore() {
  loadingMore.value = true
  try {
    page.value++
    const res = await request.get('/items', {
      params: { keyword: keyword.value.trim(), page: page.value, per_page: 20 }
    })
    items.value.push(...(res.data || []))
    total.value = res.total || total.value
  } catch (_) {} finally {
    loadingMore.value = false
  }
}

onMounted(fetchRecommend)
</script>

<style scoped>
.home-page {}
.search-bar { display: flex; gap: 12px; margin-bottom: 24px; }
.section-title { margin: 16px 0; font-size: 20px; }
.item-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}
.load-more { text-align: center; margin-top: 24px; }
</style>
