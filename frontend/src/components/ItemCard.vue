<template>
  <el-card class="item-card" shadow="hover" @click="goDetail">
    <div class="cover">
      <el-image
        :src="coverUrl" fit="cover"
        class="cover-img"
        :preview-src-list="previewList"
        preview-teleported
      >
        <template #error>
          <div class="image-placeholder"><el-icon :size="48"><Picture /></el-icon></div>
        </template>
      </el-image>
      <div class="tag-row" v-if="item.tags && item.tags.length">
        <el-tag v-for="t in item.tags.slice(0, 3)" :key="t" size="small" type="info" effect="dark">{{ t }}</el-tag>
      </div>
    </div>
    <el-card class="card-body" shadow="never" body-style="padding: 12px 16px">
      <div class="title">{{ item.title }}</div>
      <div class="desc">{{ item.description }}</div>
      <div class="expect" v-if="item.expectation">
        <span class="expect-label">期望置换:</span>
        <span class="expect-value">{{ item.expectation }}</span>
      </div>
      <div class="footer">
        <div class="owner">
          <el-avatar :size="20" :src="item.owner?.avatar_url">
            {{ (item.owner?.nickname || 'U')[0] }}
          </el-avatar>
          <span class="owner-name">{{ item.owner?.nickname || item.owner?.username }}</span>
        </div>
        <span class="views"><el-icon><View /></el-icon> {{ item.view_count }}</span>
      </div>
    </el-card>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({ item: { type: Object, required: true } })
const router = useRouter()

const coverUrl = computed(() => {
  if (props.item.images && props.item.images.length > 0) return props.item.images[0]
  return ''
})
const previewList = computed(() => props.item.images || [])

function goDetail() {
  router.push(`/item/${props.item.id}`)
}
</script>

<style scoped>
.item-card {
  cursor: pointer;
  border: none;
  transition: transform 0.2s;
}
.item-card:hover { transform: translateY(-4px); }
.item-card :deep(.el-card__body) { padding: 0; }
.cover { position: relative; }
.cover-img { width: 100%; height: 200px; display: block; }
.image-placeholder {
  width: 100%; height: 200px;
  background: #f5f7fa; display: flex; align-items: center; justify-content: center;
  color: #c0c4cc;
}
.tag-row {
  position: absolute; bottom: 8px; left: 8px;
  display: flex; gap: 4px; flex-wrap: wrap;
}
.tag-row .el-tag { opacity: 0.9; }
.card-body { border: none !important; }
.title { font-size: 15px; font-weight: 600; margin-bottom: 6px; }
.desc {
  font-size: 13px; color: #606266;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 8px;
}
.expect {
  font-size: 12px; color: #409EFF; background: #ecf5ff;
  padding: 4px 8px; border-radius: 4px; margin-bottom: 8px;
  display: flex; gap: 4px;
}
.footer { display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #909399; }
.owner { display: flex; align-items: center; gap: 6px; }
.owner-name { color: #606266; }
.views { display: flex; align-items: center; gap: 4px; }
</style>
