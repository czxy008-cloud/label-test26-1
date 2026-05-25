<template>
  <div class="profile-page">
    <el-card>
      <template #header><h2>个人中心</h2></template>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="用户名">{{ user.username }}</el-descriptions-item>
        <el-descriptions-item label="昵称">{{ user.nickname || '—' }}</el-descriptions-item>
        <el-descriptions-item label="个人简介">{{ user.bio || '—' }}</el-descriptions-item>
        <el-descriptions-item label="注册时间">{{ formatTime(user.created_at) }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()
const user = computed(() => userStore.user || {})
function formatTime(t) { return t ? new Date(t).toLocaleString('zh-CN') : '' }
</script>

<style scoped>
.profile-page { max-width: 600px; margin: 0 auto; }
.profile-page h2 { margin: 0; }
</style>
